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


# API Base
apiServer = 'localhost:5000'

storageType = ''
storageHost = ''
storagePort = ''
storageProtocol = ''

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s=%(levelname)s,%(message)s')


# This function gets the poller information
def getPollerInfo(apiEndpoint):

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


def parseStorage(type, location):

  if type != 'graphite':
      return {'success': False, 'err': 'Unsupported storage type: %s' % type}

  storage = re.match('([\w]+)\:\/\/([\w\.]+)\:(\d+)', location)
  if storage == None:
      return {'success': False, 'err': 'Could not parse storage location: %s' % location}

  storageProtocol = storage.group(1)
  storageHost = storage.group(2)
  storagePort = int(storage.group(3))

  print 'Storage Protocol: %s' % storageProtocol
  print 'Storage Host: %s' % storageHost
  print 'Storage Port: %s' % storagePort

  if storageProtocol != 'pickle':
    return {'success': False, 'err': 'Unspported storage protocol: %s' % storageProtocol}

  return {'success': True,
          'storageType': type,
          'storageProtocol': storageProtocol,
          'storageHost': storageHost,
          'storagePort': storagePort}

# This function gets the list of targets from the server
def getTargets(url):

  try:
    response = urllib2.urlopen(url)
    data = response.read()
    targets = json.loads(data)
    pingList = targets['response']['obj']
    return { 'success': True, 'data': pingList }
  except:
    return { 'success': False, 'err': 'Target List Server Down' }


def snmpQuery(target, snmpString, oid, name):

  snmpEng = pysnmp.hlapi.SnmpEngine()
  commDat = pysnmp.hlapi.CommunityData(snmpString)
  udpTran = pysnmp.hlapi.UdpTransportTarget((target, 161))
  ctxData = pysnmp.hlapi.ContextData()
  objType = pysnmp.hlapi.ObjectType(pysnmp.hlapi.ObjectIdentity(oid))

  snmpReq = pysnmp.hlapi.getCmd(snmpEng, commDat, udpTran, ctxData, objType)

  try:
      eI, eS, eIdx, vBs = next(snmpReq)
  except:
      logging.warn('SNMP Exception for %s:%s (%s)' %(target, oid, name))
      return {'success': False, 'err': 'SNMP Error' }

  if eI:
    print logging.warn('SNMP Error for %s:%s %s: %s' % (target, oid, name, eI))
    return {'success': False, 'err': 'SNMP Error for %s:%s %s: %s' % (target, oid, name, eI)}
  elif eS:
    logging.warn('SNMP Error: %s at %s' %( eS, eI ))
    return {'success': False, 'err': 'SNMP Error: %s at %s' % (eS, eI)}
  else:
    if len(vBs) != 1:
      logging.error('SNMP %s:%s %s Query returned more than one row'
                    % (target, oid, name))

    return {'success': True, 'data':  { 'name': name, 'value': '%d' % vBs[0][1] } }

def poller(q, sQ):
  targets = []
  procName = multiprocessing.current_process().name
  while(1):
    data = []
    startTime = time.time()
    try:
      targets = q.get(False)
      logging.debug('Putting %s', str(targets))
    except:
      None
    for target in targets:
      d = snmpQuery(target['target'], target['snmpString'], target['oid'], target['name'])
      if d['success']:
        t = time.time()
        intTime = re.search('(\d+)\.(\d)', str(t))
        escapedName = re.sub('\/', '-', target['name'])
        dataItem = [(escapedName, (int(intTime.group(1)), int(d['data']['value'])))]
        data.append(dataItem)

    if storageType == 'graphite':
        sendToGraphite(data)
    else:
        logging.error('Unsupported storage type: %s' + storageType)

    stopTime = time.time()
    totalTime = stopTime - startTime
    timeLeft = cycleTime - totalTime
    # Aim for loopTime to be between 20% and 80%
    # Greater than 100% - send a exceeded message
    # Greater than 80% but less than 100% - send a looptime warning message
    # Less than 20% - send a looptime under warning message
    if timeLeft < 0:
      sQ.put( { 'message': 'Looptime-exceeded', 'details': 'Looptime: %s' % (timeLeft ) })
    elif timeLeft < 0.2:
      sQ.put({ 'message': 'Looptime-warning', 'details': 'Looptime: %s' % (timeLeft) } )
      time.sleep(timeLeft)
    elif timeLeft > 0.7:
      sQ.put({ 'message': 'Looptime-under', 'details': 'Looptime: %s' % (timeLeft) } )
      time.sleep(timeLeft)
    else:
      time.sleep(timeLeft)


def sendToGraphite(dataPoints):

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((storageHost, storagePort))
    except socket.error, e:
        logging.warn('Error opening socket to graphite %s' % e);

    try:

        for data in dataPoints:
            payload = pickle.dumps(data, protocol=2)
            header = struct.pack('!L', len(payload))
            message = header + payload

            s.sendall(message)

    except socket.error, e:
        logging.warn('Send to Graphite for %s due to %s' % (data['name'], e))

    s.close()


# Distributes the list of targets to ping to a number of pollers
def allocatePoller(pingList, numProcesses):
  # Distribute the targets to pollers
  for i in range(0, len(pingList)):
    pingList[i]['poller'] = i % numProcesses

  return pingList

# Initialises a array of arrays to hold each processes list of targets
def initPollerLists(numProcesses):
  targets = []
  for i in range(0, numProcesses):
    targets.append([])

  return targets

# Iterates through the pingList creating an array of targets for each poller
def distributePollers(pingList, targets):
  for i in range(0, len(pingList)):
    targets[pingList[i]['poller']].append(pingList[i])
    logging.debug('Putting: %s in poller %s', str(pingList[i]), pingList[i]['poller'])

  return targets

# Put the target lists messages on the queues for each of the pollers
def putTargetsLists(processes, numProcesses):
  for i in range(0, numProcesses):
    processes[i % numProcesses]['queue'].put(targets[i])

# Create a new process and return it
def createProcess(id):
  processName = 'poller-' + str(id)
  process = {}
  process['queue'] = multiprocessing.Queue()
  process['sysQueue'] = multiprocessing.Queue()
  process['processName'] = processName
  process['handle'] = multiprocessing.Process(name=processName, target=poller,
                                              args=(process['queue'], process['sysQueue'],))
  process['handle'].start()
  return process

# Terminate the process provided
def deleteProcess(process):
  process['handle'].terminate()
  logging.info('Shutdown process %s', process['processName'])

# Check for system messages from poller
def getSysMessages(process):

  messages = []

  checkMessages = True
  while checkMessages:
    try:
      message = process['sysQueue'].get(False)
      messages.append(message)
    except:
      checkMessages = False

  return messages

#######################
# Program starts here #
#######################

if __name__ == '__main__':

  parser = argparse.ArgumentParser()

  parser.add_argument('pollerName', action='store', nargs=1, help='Defines name of poller')
  parser.add_argument('-f', dest='foreground', action='store_true', help='Run process in foreground')

  args = parser.parse_args()

  if args.foreground:
    print 'Foregrounding the process is currently unsupported'
    exit(1)

  # Poller name
  pollerName = args.pollerName[0]

  logging.info('SubfragiumPoller starting')

  apiEndpoint = SubfragiumUtilsLib.getApiEndPoint(apiServer)
  if not apiEndpoint['success']:
      print 'Could not get Api Endpoints: %s' % apiEndpoint['err']
      exit(1)

  pollerInfo = getPollerInfo(apiEndpoint)
  if not pollerInfo['success']:
      print 'Could not get poller info: %s' % pollerInfo['err']
      exit(1)

  print pollerInfo

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
  cycleTime = pollerInfo['obj']['cycleTime']

  storage = parseStorage(pollerInfo['obj']['storageType'], pollerInfo['obj']['storageLocation'])
  if not storage['success']:
      print 'Error setting up storage back end: %s' % storage['err']
      exit(1)

  # Setup the storage host
  storageHost = storage['storageHost']

  # Setup the storage port
  storagePort = storage['storagePort']

  # Setup the storage type
  storageType = storage['storageType']

  # Setup the storage protocol
  storageProtocol = storage['storageProtocol']

  # The hold down period (set to the current time i.e. no hold down)
  holdDown = time.time()

  logging.info('SubfragiumPoller configuration - pollerName: %s' % pollerName)
  logging.info('SubfragiumPoller configuration - minProcesses: %s' % minProcesses)
  logging.info('SubfragiumPoller configuration - maxProcesses: %s' % maxProcesses)
  logging.info('SubfragiumPoller configuration - numProcesses: %s' % numProcesses)
  logging.info('SubfragiumPoller configuration - cycleTime: %s' % cycleTime)
  logging.info('SubfragiumPoller configuration - Storage Type: %s' % storageType)
  logging.info('SubfragiumPoller configuration - Storage Protocol: %s' % storageProtocol)
  logging.info('SubfragiumPoller configuration - Storage Host: %s' % storageHost)
  logging.info('SubfragiumPoller configuration - Storage Port: %s' % storagePort)

  # Initialise a set of processes to start with
  for i in range(0, numProcesses):
    process = createProcess(i)
    processes.append(process)

  pingList = []

  # Loop for ever
  while(1):

    # Get the API base

    apiEndpoint = SubfragiumUtilsLib.getApiEndPoint(apiServer)
    if not apiEndpoint['success']:
      logging.error(apiEndpoint['err'])
    else:

      # Get the list of targets
      info = apiEndpoint['urls']['oids'] + '?poller=' + pollerName
      result = getTargets(info)
      if result['success']:
        newPingList = result['data']

        # Distribute the targets to pollers
        newPingList = allocatePoller(newPingList, numProcesses)

        # Check if there has been any change to the list since last time
        if pingList != newPingList:
          pingList = newPingList
          logging.debug('New Ping List')

          # Initialise the target lists to pass to each of the pollers
          targets = initPollerLists(numProcesses)

          # Iterate through the target list appending targets to correct poller
          targets = distributePollers(pingList, targets)

          # Send the target lists to poller processes
          putTargetsLists(processes, numProcesses)

        else:
          # Change to the list of targets so just print a message if logging is at the debug level
          logging.debug('No change to targets')

      else:
        # Log the error when the system tried to get the ping list from the server
        logging.error('Could not get ping list due to: %s', result['err'])

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
            logging.info('%s %s', message['message'], message['details'])

            # Handle a message indicating we're getting close to the time for the loop to execute
            if message['message'] == 'Looptime-warning':
              loopCounter = loopCounter + 1

            # Handle a message indicating we're exceeding the time for the loop to execute
            elif message['message'] == 'Looptime-exceeded':
              loopCounter = loopCounter + 2

            # Handle a message indcating the loop is taking very little time to execute
            elif message['message'] == 'Looptime-under':
              loopCounter = loopCounter -1

            # Handle an unknown message type
            else:
              logging.error('Unknown system message %s', message)

          # We're still in the hold down period so log and ignore the message
          else:
            logging.info('Still in hold time for %s - ignoring message: %s, %s', inHoldDown, message['message'], message['details'])

      # If loopCounter indicates pollers are overloaded
      if loopCounter > 5:
        # Reset the loopCounter
        loopCounter = 0
        # Set the hold timer to 20 seconds so we ignore messages while the load settles down
        holdDown = time.time() + 20

        # Check if we've reached the max number of processes
        if numProcesses < maxProcesses:
          # Still less than our max so start a new process
          process = createProcess(numProcesses+1)
          processes.append(process)
          numProcesses += 1
          logging.info('Added new process - previous number: %s, new number: %s', numProcesses - 1, numProcesses)
          logging.info('Entering number of processes hold for 20 seconds' )
        else:
          # Reached our maximum so log error
          logging.error('Reached max number of processes: %s', numProcesses)
          logging.info('Entering number of processes hold for 20 seconds')

      # If looppCounter indicates pollers are underloaded
      elif loopCounter < -5:
        # Reset the loopCounter
        loopCounter = 0
        # Set the hold timer to 20 seconds so we ignore messages while the load settles down
        holdDown = time.time() + 20

        # Check if we're reached the minimum number of processes
        if numProcesses > minProcesses:
          # Still more than the minimum so destroy a process
          deleteProcess(processes[numProcesses-1])
          processes.pop(numProcesses-1)
          numProcesses -= 1
          logging.info('Removed process - previous number: %s, new number: %s', numProcesses + 1, numProcesses)
          logging.info('Entering number of process hold for 20 seconds')
        else:
          # Reached out minimum so log a message
          logging.info('Reached miniumum number of processes: %s', numProcesses)
          logging.info('Entering number of processes hold for 20 seconds')

      # loopCounter indicates no capacity issues
      else:
        None

    # Sleep for 5 seconds before repeating the management cycle
    time.sleep(5)

  # Stop the processes
  for i in range(0, numProcesses):
    processes[i]['handle'].join()