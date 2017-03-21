#!/usr/bin/python

import multiprocessing
import time
import logging
import pickle
import struct
import socket
import re
import argparse
import daemon
import os
import Queue
import ConfigParser
import signal
import lockfile

import SubfragiumPollerLib
import SubfragiumUtilsLib

# Global configuration dictionary for reference by many processes
configuration = dict()

# Global processes list
processes = []


def shutdownSignal(sigNum, frame):

    logger = logging.getLogger('SubfragiumPoller')

    logger.warn('Shutting down pollers after signal SIGINT')

    for process in processes:
        logger.warn('Shutting down process %s (pid: %s)' % (process['processName'], process['pid']))
        SubfragiumPollerLib.deleteProcess(process)

    logger.warn('Shutdown complete')
    exit(1)


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
            logger.debug('Poller Data Queue Empty')
        for target in targets:
            disabledTarget = SubfragiumPollerLib.checkTarget(target['target'], target['oid'], failures)
            if not disabledTarget:
                d = SubfragiumPollerLib.snmpQuery(target['target'], target['snmpString'], target['oid'],
                                                  target['name'], target['timeout'])
                if d['success']:
                    t = time.time()
                    intTime = re.search('(\d+)\.(\d)', str(t))
                    escapedName = re.sub('/', '-', target['name'])
                    dataItem = [(escapedName, (int(intTime.group(1)), int(d['data']['value'])))]
                    data.append(dataItem)
                else:
                    logger.info('SNMP Failure for %s' % target['target'])
                    failures = SubfragiumPollerLib.disableTarget(target['target'], target['oid'], failures,
                                                                 configuration['errorThreshold'],
                                                                 configuration['errorThreshold'])
            else:
                logger.debug('Ignoring %s:%s as its currently disabled' % (target['target'],
                                                                           target['oid']))
                failures = SubfragiumPollerLib.enableTarget(target['target'], target['oid'], failures)

        if configuration['storageType'] == 'graphite':
            if len(data) > 0:
                sendToGraphite(data)
        else:
            logger.error('Unsupported storage type: %s' + configuration['storageType'])

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
        s.connect((configuration['storageHost'], configuration['storagePort']))
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


# Create a new process and return it
def createProcess(pid, createDaemon):
    processName = 'poller-' + str(pid)
    process = dict()
    process['queue'] = multiprocessing.Queue()
    process['sysQueue'] = multiprocessing.Queue()
    process['processName'] = processName

    # Check if the proces has been started as a daemon
    if createDaemon:
        # Yes - do not set the daemon flag
        process['handle'] = multiprocessing.Process(name=processName, target=poller,
                                                    args=(process['queue'], process['sysQueue'],))
    else:
        process['handle'] = multiprocessing.Process(name=processName, target=poller,
                                                    args=(process['queue'], process['sysQueue'],))
        process['handle'].daemon = True

    process['handle'].start()
    process['pid'] = process['handle'].pid
    return process


def parseConfigFile(filePath):

    config = ConfigParser.SafeConfigParser()
    config.read(filePath)
    if config.sections() == []:
        print 'Config file not found: %s' % filePath
        exit(1)

    if 'general' not in config.sections():
        print 'Config file missing [general] section'
        exit(1)

    global configuration

    try:

        parameters = ('controller', 'logLevel', 'pollerName', 'logFile', 'pidFile', 'workingDir')
        for parameter in parameters:
            configuration[parameter] = config.get('general', parameter)
            print parameter + ' ' + config.get('general', parameter)
    except ConfigParser.NoOptionError:
        print 'No %s definition under [general] section' % parameter
        exit(1)

    results = SubfragiumPollerLib.validateLogLevel(configuration['logLevel'])
    if not results['success']:
        print 'Error in config file: %s' % filePath[0]
        print results['err']
        exit(1)


def cliControllerOverride(controller):

    global configuration

    configuration['controller'] = controller


def cliLogLevelOverride(logLevel):

    global configuration

    configuration['logLevel'] = logLevel


def cliPollerOverride(name):

    global configuration

    configuration['pollerName'] = name


def mainLoop(pollerName, isDaemon, controller):

    logger = logging.getLogger('SubfragiumPoller')

    logger.info('SubfragiumPoller starting')

    apiEndpoint = SubfragiumUtilsLib.getApiEndPoint(controller)
    if not apiEndpoint['success']:
        print 'Could not get Api Endpoints: %s' % apiEndpoint['err']
        exit(1)

    pollerInfo = SubfragiumPollerLib.getPollerInfo(apiEndpoint, pollerName)
    if not pollerInfo['success']:
        print 'Could not get poller info: %s' % pollerInfo['err']
        exit(1)

    # Global dictionary for configuration information
    global configuration

    # Global list of processes
    global processes

    # Configure the location of the controller
    configuration['controller'] = controller

    # Current number of poller processes
    configuration['numProcesses'] = pollerInfo['obj']['numProcesses']

    # How overloaded or underloaded the poller processes are
    loopCounter = 0

    # Max number of poller processes
    configuration['maxProcesses'] = pollerInfo['obj']['maxProcesses']

    # Min number of poller processes
    configuration['minProcesses'] = pollerInfo['obj']['minProcesses']

    # Cycle time between polls
    configuration['cycleTime'] = pollerInfo['obj']['cycleTime']

    storage = SubfragiumPollerLib.parseStorage(pollerInfo['obj']['storageType'], pollerInfo['obj']['storageLocation'])
    if not storage['success']:
        print 'Error setting up storage back end: %s' % storage['err']
        exit(1)

    # Setup the storage host
    configuration['storageHost'] = storage['storageHost']

    # Setup the storage port
    configuration['storagePort'] = storage['storagePort']

    # Setup the storage type
    configuration['storageType'] = storage['storageType']

    # Setup the storage protocol
    configuration['storageProtocol'] = storage['storageProtocol']

    # Setup errorThreshold
    configuration['errorThreshold'] = pollerInfo['obj']['errorThreshold']

    # Setup errorHoldTime
    configuration['errorHoldTime'] = pollerInfo['obj']['errorHoldTime']

    # The hold down period (set to the current time i.e. no hold down)
    holdDown = time.time()

    logger.info('Configuration - controller: %s' % configuration['controller'])
    logger.info('Configuration - pollerName: %s' % pollerName)
    logger.info('Configuration - minProcesses: %s' % configuration['minProcesses'])
    logger.info('Configuration - maxProcesses: %s' % configuration['maxProcesses'])
    logger.info('Configuration - numProcesses: %s' % configuration['numProcesses'])
    logger.info('Configuration - cycleTime: %s' % configuration['cycleTime'])
    logger.info('Configuration - Storage Type: %s' % configuration['storageType'])
    logger.info('Configuration - Storage Protocol: %s' % configuration['storageProtocol'])
    logger.info('Configuration - Storage Host: %s' % configuration['storageHost'])
    logger.info('Configuration - Storage Port: %s' % configuration['storagePort'])
    logger.info('Configuration - errorThreshold: %s' % configuration['errorThreshold'])
    logger.info('Configuration - errorHoldTime: %s' % configuration['errorHoldTime'])

    # Initialise a set of processes to start with
    for i in range(0, int(configuration['numProcesses'])):
        process = createProcess(i, isDaemon)
        processes.append(process)

    targetList = []

    # Loop for ever
    while 1:

        # Get the API base

        apiEndpoint = SubfragiumUtilsLib.getApiEndPoint(configuration['controller'])
        if not apiEndpoint['success']:
            logger.error(apiEndpoint['err'])
        else:

            # Get the list of targets
            info = apiEndpoint['urls']['oids'] + '?poller=' + pollerName + '&enabled=True'
            result = SubfragiumPollerLib.getTargets(info)
            if result['success']:
                newTargetList = result['data']

                # Distribute the targets to pollers
                newTargetList = SubfragiumPollerLib.allocatePoller(newTargetList, configuration['numProcesses'])

                # Check if there has been any change to the list since last time
                if targetList != newTargetList:
                    targetList = newTargetList
                    logger.debug('New Target List')

                    # Initialise the target lists to pass to each of the pollers
                    targets = SubfragiumPollerLib.initPollerLists(configuration['numProcesses'])

                    # Iterate through the target list appending targets to correct poller
                    targets = SubfragiumPollerLib.distributePollers(targetList, targets)

                    # Send the target lists to poller processes
                    SubfragiumPollerLib.putTargetsLists(targets, processes, configuration['numProcesses'])

                else:
                    # Change to the list of targets so just print a message if logging is at the debug level
                    logger.debug('No change to targets')

            else:
                # Log the error when the system tried to get the target list from the server
                logger.error('Could not get target list due to: %s', result['err'])

            # Check if we've got any messages back from the poller processes
            for process in processes:

                # Get any pending messages from the pollers
                messages = SubfragiumPollerLib.getSysMessages(process)

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
                if configuration['numProcesses'] < configuration['maxProcesses']:
                    # Still less than our max so start a new process
                    process = createProcess(configuration['numProcesses'] + 1, isDaemon)
                    processes.append(process)
                    configuration['numProcesses'] += 1
                    logger.info('Added new process - previous number: %s, new number: %s',
                                configuration['numProcesses'] - 1,
                                configuration['numProcesses'])
                    logger.info('Entering number of processes hold for 20 seconds')
                else:
                    # Reached our maximum so log error
                    logger.error('Reached max number of processes: %s', configuration['numProcesses'])
                    logger.info('Entering number of processes hold for 20 seconds')

            # If looppCounter indicates pollers are underloaded
            elif loopCounter < -5:
                # Reset the loopCounter
                loopCounter = 0
                # Set the hold timer to 20 seconds so we ignore messages while the load settles down
                holdDown = time.time() + 20

                # Check if we're reached the minimum number of processes
                if configuration['numProcesses'] > configuration['minProcesses']:
                    # Still more than the minimum so destroy a process
                    SubfragiumPollerLib.deleteProcess(processes[configuration['numProcesses'] - 1])
                    processes.pop(configuration['numProcesses'] - 1)
                    configuration['numProcesses'] -= 1
                    logger.info('Removed process - previous number: %s, new number: %s',
                                configuration['numProcesses'] + 1, configuration['numProcesses'])
                    logger.info('Entering number of process hold for 20 seconds')
                else:
                    # Reached out minimum so log a message
                    logger.info('Reached miniumum number of processes: %s', configuration['numProcesses'])
                    logger.info('Entering number of processes hold for 20 seconds')

            # loopCounter indicates no capacity issues
            else:
                logger.debug('Number of processes ok')

        # Sleep for 5 seconds before repeating the management cycle
        time.sleep(5)

    # Stop the processes
    # for i in range(0, numProcesses):
    #    processes[i]['handle'].join()


#######################
# Program starts here #
#######################

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('cfgFile', action='store', nargs=1, help='Define configuration file')
    parser.add_argument('-c', dest='controller', action='store', help='Defines controller')
    parser.add_argument('-f', dest='foreground', action='store_true', help='Run process in foreground')
    parser.add_argument('-l', dest='logLevel', action='store', choices=SubfragiumPollerLib.logLevels,
                        help='Logging level')
    parser.add_argument('-L', dest='logFile', action='store', help='Defines log file name')
    parser.add_argument('-p', dest='pollerName', action='store', help='Defines name of poller')

    args = parser.parse_args()

    parseConfigFile(args.cfgFile)

    if args.logLevel:
        cliLogLevelOverride(args.logLevel)

    if args.pollerName:
        cliPollerOverride(args.pollerName)

    if args.controller:
        cliControllerOverride(args.controller)

    if args.foreground:

        signal.signal(signal.SIGINT, shutdownSignal)

        SubfragiumPollerLib.setupLogging(False, configuration['logLevel'], 'SubfragiumPoller.log')
        mainLoop(configuration['pollerName'], False, configuration['controller'])

    else:

        signalMap = {
            'signal.SIGINT': shutdownSignal
        }

        print
        print configuration['workingDir']
        print configuration['pidFile']
        print configuration['logLevel']
        print configuration['logFile']
        print configuration['pollerName']
        print configuration['controller']
        print 'Entering Daemon Mode'

        context = daemon.DaemonContext(
            working_directory=configuration['workingDir'],
            pidfile=lockfile.FileLock(configuration['pidFile']),
            signal_map={signal.SIGINT: shutdownSignal}
        )

        with context:
            SubfragiumPollerLib.setupLogging(True, configuration['logLevel'], configuration['logFile'])
            mainLoop(configuration['pollerName'], True, configuration['controller'])
