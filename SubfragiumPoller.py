#!/usr/bin/python

import urllib2
import json
import multiprocessing
import time
import logging
import SubfragiumUtilsLib
import pysnmp.hlapi
import pickle
import struct
import socket
import re
import argparse
import daemon
import os
import Queue
import datetime


# API Base
apiServer = 'localhost:5000'

storageType = ''
storageHost = ''
storagePort = ''
storageProtocol = ''
configuration = dict()

def setupLogging(daemonStatus, loggingLevel):

    logger = logging.getLogger('SubfragiumPoller')
    logger.setLevel(loggingLevel.upper())
    formatter = logging.Formatter('%(asctime)s=%(levelname)s,%(name)s,%(message)s')

    if daemonStatus:
        # Setup logging as a daemon to a file
        handler = logging.FileHandler(filename='SubfragiumPoller.log')

    else:
        # Setup logging as a foreground process to the console
        handler = logging.StreamHandler()

    handler.setLevel(logLevel.upper())
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# This function gets the poller information
def getPollerInfo(apiEndpoint, pollerName):

    apiCall = apiEndpoint['urls']['poller'].replace('<string:name>', pollerName)
    try:
        response = urllib2.urlopen(apiCall)
        data = response.read()
        pollerInfo = json.loads(data)
        if 'response' not in pollerInfo:
            return {'success': False, 'err': 'Unknown response from Controller: %s' % data}
        if not pollerInfo['response']['success']:
            return {'success': False, 'err': 'Error from controller: %s' % pollerInfo['err']}
        return {'success': True, 'obj': pollerInfo['response']['obj']}
    except Exception, e:
        return{'success': False, 'err': 'Could not get poller information: %s' % str(e)}


def parseStorage(stype, location):

    if stype != 'graphite':
        return {'success': False, 'err': 'Unsupported storage type: %s' % stype}

    storage = re.match('([\w]+)\:\/\/([\w\.]+)\:(\d+)', location)
    if storage is None:
        return {'success': False, 'err': 'Could not parse storage location: %s' % location}

    storageProtocol = storage.group(1)
    storageHost = storage.group(2)
    storagePort = int(storage.group(3))

    if storageProtocol != 'pickle':
        return {'success': False, 'err': 'Unspported storage protocol: %s' % storageProtocol}

    return {'success': True,
            'storageType': stype,
            'storageProtocol': storageProtocol,
            'storageHost': storageHost,
            'storagePort': storagePort}


# This function gets the list of targets from the server
def getTargets(url):

    try:
        response = urllib2.urlopen(url)
        data = response.read()
        targets = json.loads(data)
        targetList = targets['response']['obj']
        return {'success': True, 'data': targetList}
    except urllib2.URLError, e:
        return {'success': False, 'err': 'Target List Server Down: %s' % e}


def snmpQuery(target, snmpString, oid, name, timeout):

    logger = logging.getLogger('SubfragiumPoller')

    timeoutSeconds = float(timeout) / 1000

    snmpEng = pysnmp.hlapi.SnmpEngine()
    commDat = pysnmp.hlapi.CommunityData(snmpString)
    udpTran = pysnmp.hlapi.UdpTransportTarget((target, 161), timeout=timeoutSeconds)
    ctxData = pysnmp.hlapi.ContextData()
    objType = pysnmp.hlapi.ObjectType(pysnmp.hlapi.ObjectIdentity(oid))

    snmpReq = pysnmp.hlapi.getCmd(snmpEng, commDat, udpTran, ctxData, objType)

    try:
        eI, eS, eIdx, vBs = next(snmpReq)
    except:
        logger.warn('SNMP Exception for %s:%s (%s)' % (target, oid, name))
        return {'success': False, 'err': 'SNMP Error'}

    if eI:
        logger.warn('SNMP Error for %s:%s %s: %s' % (target, oid, name, eI))
        return {'success': False, 'err': 'SNMP Error for %s:%s %s: %s' % (target, oid, name, eI)}
    elif eS:
        logger.warn('SNMP Error: %s at %s' % (eS, eI))
        return {'success': False, 'err': 'SNMP Error: %s at %s' % (eS, eI)}
    else:
        if len(vBs) != 1:
            logger.error('SNMP %s:%s %s Query returned more than one row'
                         % (target, oid, name))

        return {'success': True, 'data':  {'name': name, 'value': '%d' % vBs[0][1]}}


def disableTarget(target, oid, failures):

    logger = logging.getLogger('SubfragiumPoller')

    global configuration

    failureThreshold = configuration['errorThreshold']
    disableTime = configuration['errorHoldTime']

    # Create the unique identifier for the target and oid
    pollId = target + ':' + oid

    # Check if that id has already seen a failure and isn't in disabled state
    if pollId in failures:
        # It is so check if its already disabled
        if not failures[pollId]['disable']:
            failures[pollId]['count'] += 1
            logger.debug('%s:%s incrementing failure count: %s threshold %s' % (target,
                                                                                oid,
                                                                                failures[pollId]['count'],
                                                                                failureThreshold))
    else:
        # It has not so define the failure counter
        failures[pollId] = dict()
        failures[pollId]['count'] = 1
        failures[pollId]['disable'] = False
        failures[pollId]['reenable'] = ''
        logger.debug('%s:%s added to failure tracking' % (target, oid))

    # Check if we need to disable it for a while
    if not failures[pollId]['disable'] and failures[pollId]['count'] > failureThreshold:
        currTime = time.time()
        logger.debug('%s:%s disabled as count: %s exceeded threshold: %s' % (target,
                                                                             oid,
                                                                             failures[pollId]['count'],
                                                                             failureThreshold))

        failures[pollId]['count'] = 0
        failures[pollId]['disable'] = True
        failures[pollId]['reenable'] = currTime + disableTime

        holdTime = datetime.datetime.fromtimestamp(int(currTime + disableTime))
        timeString = holdTime.strftime('%Y-%m-%d %H:%M:%S')
        logger.info('Disabled %s:%s until %s' % (target, oid, timeString))

        # Return the failures object for future reference
        return failures

    # Return the failure object for future reference
    return failures


def checkTarget(target, oid, failure):

    # Form the pollId index used to track oids
    pollId = target + ':' + oid

    # Check if a target/oid id exists and if its in a disabled state
    if pollId in failure and failure[pollId]['disable']:
        # It is so return true
        return True

    # It isn't so return false
    return False


def enableTarget(target, oid, failures):

    logger = logging.getLogger('SubfragiumPoller')

    # Create the unique identifier for the target and oid
    pollId = target + ':' + oid

    # Get the current time
    currTime = int(time.time())

    # Check if this target has seen any failures
    if pollId in failures:

        # It has so check if its disabled
        if failures[pollId]['disable']:

            # It is so check if its time to re-enable it
            if currTime > failures[pollId]['reenable']:

                currTimeObj = datetime.datetime.fromtimestamp(int(currTime))
                currTimeStr = currTimeObj.strftime('%Y-%m-%d %H:%M:%S')
                enableTime = datetime.datetime.fromtimestamp(int(failures[pollId]['reenable']))
                enableTimeStr = enableTime.strftime( '%Y-%m-%d %H:%M:%S' )
                logger.debug('Enabling %s:%s as %s is later than %s' % (target,
                                                                        oid,
                                                                        currTimeStr,
                                                                        enableTimeStr))
                failures[pollId]['disable'] = False
                failures[pollId]['reenable'] = currTime
                logger.info('Enabled %s:%s for future polling' % (target, oid))

                return failures

            # Else do nothing - haven't reached re-enable time yet

        # Else do nothing - this oid isn't in a disabled state

    # Else do nothing - this oid isn't in failures list

    return failures


def poller(q, sQ):

    logger = logging.getLogger('SubfragiumPoller')

    global configuration
    cycleTime = configuration['cycleTime']

    targets = []

    failures = dict()

    while 1:
        data = []
        startTime = time.time()
        try:
            targets = q.get(False)
            for t in targets:
                logger.debug('Putting %s', str(t['id']))
        except Queue.Empty:
            None
        for target in targets:
            disabledTarget = checkTarget(target['target'], target['oid'], failures)
            if not disabledTarget:
                d = snmpQuery(target['target'], target['snmpString'], target['oid'], target['name'], target['timeout'])
                if d['success']:
                    t = time.time()
                    intTime = re.search('(\d+)\.(\d)', str(t))
                    escapedName = re.sub('\/', '-', target['name'])
                    dataItem = [(escapedName, (int(intTime.group(1)), int(d['data']['value'])))]
                    data.append(dataItem)
                else:
                    logger.info('SNMP Failure for %s' % target['target'])
                    failures = disableTarget(target['target'], target['oid'], failures)
            else:
                logger.debug('Ignoring %s:%s as its currently disabled' % (target['target'],
                                                                           target['oid']))
                failures = enableTarget(target['target'], target['oid'], failures)

        if storageType == 'graphite':
            if len(data) > 0:
                sendToGraphite(data)
        else:
            logger.error('Unsupported storage type: %s' + storageType)

        stopTime = time.time()
        totalTime = stopTime - startTime
        timeLeft = float(cycleTime) - float(totalTime)
        # Aim for loopTime to be between 20% and 80%
        # Greater than 100% - send a exceeded message
        # Greater than 80% but less than 100% - send a looptime warning message
        # Less than 20% - send a looptime under warning message
        if timeLeft < 0:
            sQ.put({'message': 'Looptime-exceeded', 'details': 'Looptime: %s' % timeLeft})
        elif timeLeft < 0.2:
            sQ.put({'message': 'Looptime-warning', 'details': 'Looptime: %s' % timeLeft})
            time.sleep(timeLeft)
        elif timeLeft > 0.7:
            sQ.put({'message': 'Looptime-under', 'details': 'Looptime: %s' % timeLeft})
            time.sleep(timeLeft)
        else:
            time.sleep(timeLeft)


def sendToGraphite(dataPoints):

    logger = logging.getLogger('SubfragiumPoller')

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((storageHost, storagePort))
    except socket.error, e:
        logger.warn('Error opening socket to graphite %s' % e)
        return

    try:

        for data in dataPoints:
            payload = pickle.dumps(data, protocol=2)
            header = struct.pack('!L', len(payload))
            message = header + payload

            s.sendall(message)

    except socket.error, e:
        logger.warn('Send to Graphite failed: %s' % e)

    s.close()


# Distributes the list of targets to target to a number of pollers
def allocatePoller(targetList, numProcesses):
    # Distribute the targets to pollers
    for i in range(0, len(targetList)):
        targetList[i]['poller'] = i % numProcesses

    return targetList


# Initialises a array of arrays to hold each processes list of targets
def initPollerLists(numProcesses):
    targets = []
    for i in range(0, numProcesses):
        targets.append([])

    return targets


# Iterates through the target list creating an array of targets for each poller
def distributePollers(targetList, targets):

    logger = logging.getLogger('SubfragiumPoller')

    for i in range(0, len(targetList)):
        targets[targetList[i]['poller']].append(targetList[i])
        logger.debug('Allocating: %s to poller %s', str(targetList[i]['id']), targetList[i]['poller'])

    return targets


# Put the target lists messages on the queues for each of the pollers
def putTargetsLists(targets, processes, numProcesses):
    for i in range(0, numProcesses):
        processes[i % numProcesses]['queue'].put(targets[i])


# Create a new process and return it
def createProcess(pid):
    processName = 'poller-' + str(pid)
    process = dict()
    process['queue'] = multiprocessing.Queue()
    process['sysQueue'] = multiprocessing.Queue()
    process['processName'] = processName
    process['handle'] = multiprocessing.Process(name=processName, target=poller,
                                                args=(process['queue'], process['sysQueue'],))
    process['handle'].start()
    return process


# Terminate the process provided
def deleteProcess(process):

    logger = logging.getLogger('SubfragiumPoller')

    process['handle'].terminate()
    logger.info('Shutdown process %s', process['processName'])


# Check for system messages from poller
def getSysMessages(process):

    messages = []

    checkMessages = True
    while checkMessages:
        try:
            message = process['sysQueue'].get(False)
            messages.append(message)
        except Queue.Empty:
            checkMessages = False

    return messages


def mainLoop(pollerName):

    logger = logging.getLogger('SubfragiumPoller')

    logger.info('SubfragiumPoller starting')

    apiEndpoint = SubfragiumUtilsLib.getApiEndPoint(apiServer)
    if not apiEndpoint['success']:
        print 'Could not get Api Endpoints: %s' % apiEndpoint['err']
        exit(1)

    pollerInfo = getPollerInfo(apiEndpoint, pollerName)
    if not pollerInfo['success']:
        print 'Could not get poller info: %s' % pollerInfo['err']
        exit(1)


    # List of poller processes
    processes = []

    # Current number of poller processes
    numProcesses = pollerInfo['obj']['numProcesses']

    # How overloaded or underloaded the poller processes are
    loopCounter = 0

    # Max number of poller processes
    maxProcesses = pollerInfo['obj']['maxProcesses']

    # Min number of poller processes
    minProcesses = pollerInfo['obj']['minProcesses']

    # Cycle time between polls
    configuration['cycleTime'] = pollerInfo['obj']['cycleTime']

    storage = parseStorage(pollerInfo['obj']['storageType'], pollerInfo['obj']['storageLocation'])
    if not storage['success']:
        print 'Error setting up storage back end: %s' % storage['err']
        exit(1)

    # Setup the storage host
    global storageHost
    storageHost = storage['storageHost']

    # Setup the storage port
    global storagePort
    storagePort = storage['storagePort']

    # Setup the storage type
    global storageType
    storageType = storage['storageType']

    # Setup the storage protocol
    global storageProtocol
    storageProtocol = storage['storageProtocol']

    # Setup errorThreshold
    global configuration
    configuration['errorThreshold'] = pollerInfo['obj']['errorThreshold']

    # Setup errorHoldTime
    configuration['errorHoldTime'] = pollerInfo['obj']['errorHoldTime']

    # The hold down period (set to the current time i.e. no hold down)
    holdDown = time.time()

    logger.info('Configuration - pollerName: %s' % pollerName)
    logger.info('Configuration - minProcesses: %s' % minProcesses)
    logger.info('Configuration - maxProcesses: %s' % maxProcesses)
    logger.info('Configuration - numProcesses: %s' % numProcesses)
    logger.info('Configuration - cycleTime: %s' % configuration['cycleTime'])
    logger.info('Configuration - Storage Type: %s' % storageType)
    logger.info('Configuration - Storage Protocol: %s' % storageProtocol)
    logger.info('Configuration - Storage Host: %s' % storageHost)
    logger.info('Configuration - Storage Port: %s' % storagePort)
    logger.info('Configuration - errorThreshold: %s' % configuration['errorThreshold'])
    logger.info('Configuration - errorHoldTime: %s' % configuration['errorHoldTime'])

    # Initialise a set of processes to start with
    for i in range(0, int(numProcesses)):
        process = createProcess(i)
        processes.append(process)

    targetList = []

    # Loop for ever
    while 1:

        # Get the API base

        apiEndpoint = SubfragiumUtilsLib.getApiEndPoint(apiServer)
        if not apiEndpoint['success']:
            logger.error(apiEndpoint['err'])
        else:

            # Get the list of targets
            info = apiEndpoint['urls']['oids'] + '?poller=' + pollerName + '&enabled=True'
            result = getTargets(info)
            if result['success']:
                newTargetList = result['data']

                # Distribute the targets to pollers
                newTargetList = allocatePoller(newTargetList, numProcesses)

                # Check if there has been any change to the list since last time
                if targetList != newTargetList:
                    targetList = newTargetList
                    logger.debug('New Target List')

                    # Initialise the target lists to pass to each of the pollers
                    targets = initPollerLists(numProcesses)

                    # Iterate through the target list appending targets to correct poller
                    targets = distributePollers(targetList, targets)

                    # Send the target lists to poller processes
                    putTargetsLists(targets, processes, numProcesses)

                else:
                    # Change to the list of targets so just print a message if logging is at the debug level
                    logger.debug('No change to targets')

            else:
                # Log the error when the system tried to get the target list from the server
                logger.error('Could not get target list due to: %s', result['err'])

            # Check if we've got any messages back from the poller processes
            for process in processes:

                # Get any pending messages from the pollers
                messages = getSysMessages(process)

                # Process each of the messages
                for message in messages:

                    # Calculate if we're still in the hold down period (i.e to ignore messages)
                    inHoldDown = holdDown - time.time()

                    # Check if we're in the hold down period (i.e the time difference is negative)
                    if inHoldDown < 0:
                        logger.debug('%s %s', message['message'], message['details'])

                        # Handle a message indicating we're getting close to the time for the loop to execute
                        if message['message'] == 'Looptime-warning':
                            loopCounter += 1

                        # Handle a message indicating we're exceeding the time for the loop to execute
                        elif message['message'] == 'Looptime-exceeded':
                            loopCounter += 2

                        # Handle a message indcating the loop is taking very little time to execute
                        elif message['message'] == 'Looptime-under':
                            loopCounter -= 1

                        # Handle an unknown message type
                        else:
                            logger.error('Unknown system message %s', message)

                    # We're still in the hold down period so log and ignore the message
                    else:
                        logger.info('Still in hold time for %s - ignoring message: %s, %s', inHoldDown,
                                    message['message'],
                                    message['details'])

            # If loopCounter indicates pollers are overloaded
            if loopCounter > 5:
                # Reset the loopCounter
                loopCounter = 0
                # Set the hold timer to 20 seconds so we ignore messages while the load settles down
                holdDown = time.time() + 20

                # Check if we've reached the max number of processes
                if numProcesses < maxProcesses:
                    # Still less than our max so start a new process
                    process = createProcess(numProcesses + 1)
                    processes.append(process)
                    numProcesses += 1
                    logger.info('Added new process - previous number: %s, new number: %s', numProcesses - 1,
                                numProcesses)
                    logger.info('Entering number of processes hold for 20 seconds')
                else:
                    # Reached our maximum so log error
                    logger.error('Reached max number of processes: %s', numProcesses)
                    logger.info('Entering number of processes hold for 20 seconds')

            # If looppCounter indicates pollers are underloaded
            elif loopCounter < -5:
                # Reset the loopCounter
                loopCounter = 0
                # Set the hold timer to 20 seconds so we ignore messages while the load settles down
                holdDown = time.time() + 20

                # Check if we're reached the minimum number of processes
                if numProcesses > minProcesses:
                    # Still more than the minimum so destroy a process
                    deleteProcess(processes[numProcesses - 1])
                    processes.pop(numProcesses - 1)
                    numProcesses -= 1
                    logger.info('Removed process - previous number: %s, new number: %s', numProcesses + 1, numProcesses)
                    logger.info('Entering number of process hold for 20 seconds')
                else:
                    # Reached out minimum so log a message
                    logger.info('Reached miniumum number of processes: %s', numProcesses)
                    logger.info('Entering number of processes hold for 20 seconds')

            # loopCounter indicates no capacity issues
            else:
                None

        # Sleep for 5 seconds before repeating the management cycle
        time.sleep(5)

    # Stop the processes
    for i in range(0, numProcesses):
        processes[i]['handle'].join()


#######################
# Program starts here #
#######################

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    levels = ['debug', 'info', 'warning', 'error', 'critical']

    parser.add_argument('pollerName', action='store', nargs=1, help='Defines name of poller')
    parser.add_argument('-f', dest='foreground', action='store_true', help='Run process in foreground')
    parser.add_argument('-l', dest='logLevel', action='store', choices=levels, help='Logging level')

    args = parser.parse_args()

    if not args.logLevel:
        logLevel = 'debug'
    else:
        logLevel = args.logLevel

    path = os.getcwd()

    if args.foreground:
        setupLogging(False, logLevel)
        mainLoop(args.pollerName[0])


    else:

        context = daemon.DaemonContext(
            working_directory=path,
        )

        with context:
            setupLogging(True, logLevel)
            mainLoop(args.PollerName[0])
