import urllib2
import json
import re
import logging
import pysnmp.hlapi
import pysnmp.proto
import time
import datetime
import Queue

logLevels = ['debug', 'info', 'warning', 'error', 'critical']


def setupLogging(daemonStatus, loggingLevel, logFile):

    logger = logging.getLogger('SubfragiumPoller')
    logger.setLevel(loggingLevel.upper())
    formatter = logging.Formatter('%(asctime)s=%(levelname)s,%(name)s,%(message)s')

    if daemonStatus:
        # Setup logging as a daemon to a file
        handler = logging.FileHandler(filename=logFile)

    else:
        # Setup logging as a foreground process to the console
        handler = logging.StreamHandler()

    handler.setLevel(loggingLevel.upper())
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

    storage = re.match('([\w]+)://([\w.]+):(\d+)', location)
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
            logger.warn('SNMP %s:%s %s Query returned more than one row'
                         % (target, oid, name))

        if isinstance(vBs[0][1], pysnmp.proto.rfc1902.Counter32):
            return {'success': True, 'data': {'name': name, 'value': '%d' % vBs[0][1]}}

        elif isinstance(vBs[0][1], pysnmp.proto.rfc1902.Counter64):
            return {'success': True, 'data': {'name': name, 'value': '%d' % vBs[0][1]}}

        elif isinstance(vBs[0][1], pysnmp.proto.rfc1902.Gauge32):
            return {'success': True, 'data': {'name': name, 'value': '%d' % vBs[0][1]}}

        elif isinstance(vBs[0][1], pysnmp.proto.rfc1905.NoSuchInstance):
            logger.warn('SNMP Error for %s:%s (%s): No Such Instance' % (target, oid, name))
            return {'success': False, 'err': 'SNMP Error for %s:%s (%s): No Such Instance' % (target, oid, name)}

        elif isinstance(vBs[0][1], pysnmp.proto.rfc1905.NoSuchObject):
            logger.warn('SNMP Error for %s:%s (%s): No Such Object' % (target, oid, name))
            return {'success': False, 'err': 'SNMP Error for %s:%s (%s): No Such Instance' % (target, oid, name)}

        else:
            logger.warn( 'SNMP Error for %s:%s (%s): Unknown type' % (target, oid, name))
            return {'success': False, 'err': 'SNMP Error for %s:%s (%s): Unknown type %s' % (target, oid, name, vBs[0][1])}


def disableTarget(target, oid, failures, failureThreshold, disableTime):

    logger = logging.getLogger('SubfragiumPoller')

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
                enableTimeStr = enableTime.strftime('%Y-%m-%d %H:%M:%S')
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


def validateLogLevel(level):

    if level not in logLevels:
        return {'success': False, 'err': 'Log level \'%s\' is not one of %s' % (level, logLevels)}

    return {'success': True}

