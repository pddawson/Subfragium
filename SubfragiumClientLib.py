import requests
import json
import re
import SubfragiumClientLib
import urllib2

def getApiEndPoint(apiServer):

  baseUrl = 'http://' + apiServer

  api = {}

  try:
    response = urllib2.urlopen(baseUrl)
    data = response.read()
    apiEndpoints = json.loads(data)
    for apiEndpoint in apiEndpoints['response']['obj']:
      url = baseUrl + apiEndpoints['response']['obj'][apiEndpoint]
      api[apiEndpoint] = url
    return {'success': True, 'urls': api}
  except:
    return {'success': False, 'err': 'Could not get API End Points'}

def addTypeTarget(data, apiEndpoint):
  validInput = 'name=([\w\.]+)\,snmpString=(\w+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error: Format must be --data name=<name|ip>,snmpString=<snmpString>'
    print 'e.g. --data name=1.1.1.1,snmpString=eur'
    exit(1)

  apiCall = {'snmpString': validatedInput.group(2)}
  jsonCall = json.dumps(apiCall)

  headers = {'content-type': 'application/json'}
  apiCall = apiEndpoint['urls']['target'].replace('<string:name>', '')
  apiCall = apiCall + validatedInput.group(1)
  r = requests.put(apiCall, data=jsonCall, headers=headers)
  rJson = json.loads(r.text)
  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      print 'OK'
    else:
      print 'Error: %s' % rJson['response']['err']
  else:
    print 'Error: Unknown response - %s' % r.text


def listTypeTargets(apiEndpoint):
  apiCall = apiEndpoint['urls']['targets']
  r = requests.get(apiCall)
  rJson = json.loads(r.text)
  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      for target in rJson['response']['obj']:
        print '%s,%s' % (target['name'], target['snmpString'])
    else:
      print 'Error: %s' % rJson['response']['err']
  else:
    print 'Error: Unknown response - %s ' % r.text


def listTypeTarget(data, apiEndpoint):
  validInput = 'name=([\w\.]+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error: Format must be --data name=<name|ip>'
    print 'e.g. --data name=1.1.1.1'
    exit(1)

  apiCall = apiEndpoint['urls']['target'].replace('<string:name>', '')
  apiCall = apiCall + validatedInput.group(1)
  r = requests.get(apiCall)
  rJson = json.loads(r.text)

  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      res = rJson['response']['obj']
      print '%s,%s' % (res['name'], res['snmpString'])
    else:
      print 'Error: %s' % rJson['response']['err']
  else:
    print 'Error: Unknown response - %s ' % r.text


def deleteTypeTarget(data, apiEndpoint):
  validInput = 'name=([\w\.]+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error: Format must be --data name=<name|ip>'
    print 'e.g. --data name=1.1.1.1'
    exit(1)

  apiCall = apiEndpoint['urls']['target'].replace('<string:name>', '')
  apiCall = apiCall + validatedInput.group(1)
  r = requests.delete(apiCall)
  rJson = json.loads(r.text)

  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      print 'OK'
    else:
      print 'Error: %s' % rJson['response']['err']
  else:
    print 'Error: Unknown response - %s' % r.text


def modifyTypeTarget(data, apiEndpoint):
  validInput = 'name=([\w\.]+)\,snmpString=(\w+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error: Format must be --data name=<name|ip>,snmpString=<snmpString>'
    print 'e.g. --data name=1.1.1.1,snmpString=eur'
    exit(1)

  apiCall = apiEndpoint['urls']['target'].replace('<string:name>', '')
  apiCall = apiCall + validatedInput.group(1)
  r = requests.get(apiCall)
  rJson = json.loads(r.text)
  if 'response' not in rJson:
    print 'Error: Unknown response %s' % r.text
    exit(1)

  if 'success' not in rJson['response']:
    print 'Error: Bad response %s' % rJson['response']
    exit(1)

  if not rJson['response']['success']:
    print 'Error: Failed %s' % rJson['response']['err']
    exit(1)

  apiCallData = {'snmpString': validatedInput.group(2)}
  jsonCall = json.dumps(apiCallData)

  headers = {'content-type': 'application/json'}
  apiCall = apiEndpoint['urls']['target'].replace('<string:name>', '')
  apiCall = apiCall + validatedInput.group(1)
  r = requests.put(apiCall, data=jsonCall, headers=headers)
  rJson = json.loads(r.text)
  if 'response' not in rJson:
    print 'Error: Unknown response %s' % r.text
    exit(1)

  if 'success' not in rJson['response']:
    print 'Error: Bad response %s' % rJson['response']
    exit(1)

  if not rJson['response']['success']:
    print 'Error: Failed %s' % rJson['response']['err']
    exit(1)

  print 'OK'


def addTypePoller(data, apiEndPoint):
  validInput = 'name=([\w\.]+)\,minProcesses=(\d+)\,maxProcesses=(\d+)\,numProcesses=(\d+)\,holdDown=(\d+),cycleTime=(\d+),storageType=(\w+),storageLocation=([\w\.\:\/]+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error: Format must be --data name=<name>,minProcesses=<num>,maxProcesses=<num>,numProcesses=<num>,' \
          'holdDown=<num>,cycleTime=<num>,storageType=graphite,storageLocation=pickle://graphite:5000'
    print 'e.g. --data name=poller1,minProcesses=1,maxProcesses=50,numProcesses=2,holdTime=20,cycleTime=5' \
          'storageType=graphite,storageLocation=pickle://graphite:5000'
    exit(1)

  payload = {
    'minProcesses': int(validatedInput.group(2)),
    'maxProcesses': int(validatedInput.group(3)),
    'numProcesses': int(validatedInput.group(4)),
    'holdDown': int(validatedInput.group(5)),
    'cycleTime': int(validatedInput.group(6)),
    'storageType': validatedInput.group(7),
    'storageLocation': validatedInput.group(8)
  }
  jsonStr = json.dumps(payload)

  apiCall = apiEndPoint['urls']['poller'].replace('<string:name>', '')
  apiCall = apiCall + validatedInput.group(1)

  headers = {'content-type': 'application/json'}
  r = requests.put(apiCall, data=jsonStr, headers=headers)
  if r.status_code == 500:
    print 'Error: %s' % r.text
    exit(1)

  rJson = json.loads(r.text)

  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      print 'OK'
    else:
      print 'Error: %s' % rJson['response']['err']
  else:
    print 'Error: Unknown response %s' % r.text


def listTypePollers(apiEndPoint):
  apiCall = apiEndPoint['urls']['pollers']
  r = requests.get(apiCall)
  rJson = json.loads(r.text)
  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      print 'name,minProcesses,maxProcesses,numProcesses,holdDown,cycleTime,storageType,storageLocation'
      for poller in rJson['response']['obj']:
        print '%s,%s,%s,%s,%s,%s,%s,%s' % (poller['name'],
                                  poller['minProcesses'],
                                  poller['maxProcesses'],
                                  poller['numProcesses'],
                                  poller['holdDown'],
                                  poller['cycleTime'],
                                  poller['storageType'],
                                  poller['storageLocation'])

    else:
      print 'Error: %s' % rJson['response']['err']
  else:
    print 'Error: Unknown response - %s ' % r.text


def listTypePoller(data, apiEndPoint):
  validInput = 'name=([\w\.]+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error: Format must be --data name=<name>'
    print 'e.g. --data name=poller1'
    exit(1)

  apiCall = apiEndpoint['urls']['poller'].replace('<string:name>', '')
  apiCall = apiCall + validatedInput.group(1)
  r = requests.get(apiCall)
  rJson = json.loads(r.text)

  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      res = rJson['response']['obj']
      print '%s,%s,%s,%s,%s,%s,%s,%s' % (res['name'],
                                res['minProcesses'],
                                res['maxProcesses'],
                                res['numProcesses'],
                                res['holdDown'],
                                res['cycleTime'],
                                res['storageType'],
                                res['storageLocation'])
    else:
      print 'Error: %s' % rJson['response']['err']
  else:
    print 'Error: Unknown response - %s ' % r.text


def deleteTypePoller(data, apiEndPoint):
  validInput = 'name=([\w\.]+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error: Format must be --data name=<name>'
    print 'e.g. --data name=poller1'
    exit(1)

  apiCall = apiEndPoint['urls']['poller'].replace('<string:name>', '')
  apiCall = apiCall + validatedInput.group(1)
  r = requests.delete(apiCall)
  rJson = json.loads(r.text)

  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      print 'OK'
    else:
      print 'Error: %s' % rJson['response']['err']
  else:
    print 'Error: Unknown response - %s' % r.text


def modifyTypePoller(data, apiEndPoint):
  validInput = 'name=([\w\.]+)(\,minProcesses=(\d+))*(\,maxProcesses=(\d+))*(\,numProcesses=(\d+))*(\,holdDown=(\d+))*(\,cycleTime=(\d+))*(\,storageType=(\w+))*(\,storageLocation=([\w\.\:\/]+))*'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error: Format must be --data name=<name>,minProcesses=<num>,maxProcesses=<num>,numProcesses=<num>,holdDown=<num>,cycleTime=<num>'
    print 'e.g. --data name=poller1,minProcesses=1,maxProcesses=50,numProcesses=2,holdTime=20,cycle=20' \
          'storageType=graphite,storageLocation=pickle://graphite:5000'
    exit(1)

  print validatedInput.group(0)

  apiCall = apiEndPoint['urls']['poller'].replace('<string:name>', '')
  apiCall = apiCall + validatedInput.group(1)
  r = requests.get(apiCall)
  rJson = json.loads(r.text)
  if 'response' not in rJson:
    print 'Error: Unknown response %s' % r.text
    exit(1)

  if 'success' not in rJson['response']:
    print 'Error: Bad response %s' % rJson['response']
    exit(1)

  if not rJson['response']['success']:
    print 'Error: Failed %s' % rJson['response']['err']
    exit(1)

  modifiedPoller = rJson['response']['obj']
  del(modifiedPoller['name'])

  if validatedInput.group(3) != None:
    modifiedPoller['minProcesses'] = validatedInput.group(3)
  if validatedInput.group(5) != None:
    modifiedPoller['maxProcesses'] = validatedInput.group(5)
  if validatedInput.group(7) != None:
    modifiedPoller['numProcesses'] = validatedInput.group(7)
  if validatedInput.group(9) != None:
    modifiedPoller['holdDown'] = validatedInput.group(9)
  if validatedInput.group(11) != None:
      modifiedPoller['cycleTime'] = validatedInput.group(11)
  if validatedInput.group(13) != None:
      modifiedPoller['storageType'] = validatedInput.group(13)
  if validatedInput.group(15) != None:
      modifiedPoller['storageLocation'] = validatedInput.group(15)

  jsonStr = json.dumps(modifiedPoller)

  apiCall = apiEndPoint['urls']['poller'].replace('<string:name>', '')
  apiCall = apiCall + validatedInput.group(1)

  headers = {'content-type': 'application/json'}
  r = requests.put(apiCall, data=jsonStr, headers=headers)
  if r.status_code != 200:
    print 'Error: %s' % r.text
    exit(1)

  rJson = json.loads(r.text)

  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      print 'OK'
    else:
      print 'Error: %s' % rJson['response']['err']
  else:
    print 'Error: Unknown response %s' % r.text


def addTypeOid(data, apiEndPoint):
  validInput = 'target=([\w\.]+)\,oid=([\d\.]+)\,poller=(\w+)\,name=([\w\.\/\-]+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error: Format must be --data target=<name|ip>,oid=<oid>,poller=<poller>,name=<name>'
    print 'e.g. --data name=1.1.1.1,1.3.6.1.2.1,poller1,ifInHcOctets'
    exit(1)

  payload = {'poller': validatedInput.group(3), 'name': validatedInput.group(4)}
  jsonStr = json.dumps(payload)

  apiCall = apiEndPoint['urls']['oid'].replace('<string:target>', validatedInput.group(1))
  apiCall = apiCall.replace('<string:oid>', validatedInput.group(2))
  headers = {'content-type': 'application/json'}
  r = requests.put(apiCall, data=jsonStr, headers=headers)
  if r.status_code == 500:
    print 'Error: %s' % r.text
    exit(1)

  rJson = json.loads(r.text)

  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      print 'OK'
    else:
      print 'Error: %s' % rJson['response']['err']
  else:
    print 'Error: Unknown response %s' % r.text


def modifyTypeOid(data, apiEndPoint):
  validInput = 'target=([\w\.]+)(\,oid=([\d\.]+))(\,poller=(\w+))*(\,name=([\w\.]+))*'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error: Format must be --data target=<name|ip>,oid=<oid>,poller=<poller>,name=<name>'
    print 'e.g. --data name=1.1.1.1,1.3.6.1.2.1,poller1,ifInHcOctets'
    exit(1)

  apiCall = apiEndPoint['urls']['oid'].replace('<string:target>', validatedInput.group(1))
  apiCall = apiCall.replace('<string:oid>', validatedInput.group(3))
  r = requests.get(apiCall)
  rJson = json.loads(r.text)
  if 'response' not in rJson:
    print 'Error: Unknown response %s' % r.text
    exit(1)

  if 'success' not in rJson['response']:
    print 'Error: Bad response %s' % rJson['response']
    exit(1)

  if not rJson['response']['success']:
    print 'Error: Failed %s' % rJson['response']['err']
    exit(1)

  existingOid = rJson['response']['obj']
  modifiedOid = {}
  modifiedOid['poller'] = existingOid['poller']
  modifiedOid['name'] = existingOid['name']

  print modifiedOid

  if validatedInput.group(5) != None:
    modifiedOid['poller'] = validatedInput.group(5)
  if validatedInput.group(7) != None:
    modifiedOid['name'] = validatedInput.group(7)

  jsonStr = json.dumps(modifiedOid)

  apiCall = apiEndPoint['urls']['oid'].replace('<string:target>', validatedInput.group(1))
  apiCall = apiCall.replace('<string:oid>', validatedInput.group(3))

  headers = {'content-type': 'application/json'}
  r = requests.put(apiCall, data=jsonStr, headers=headers)
  if r.status_code != 200:
    print 'Error: %s' % r.text
    exit(1)

  rJson = json.loads(r.text)

  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      print 'OK'
    else:
      print 'Error: %s' % rJson['response']['err']
  else:
    print 'Error: Unknown response %s' % r.text


def listTypeOids(apiEndPoint):
  apiCall = apiEndPoint['urls']['oids']
  r = requests.get(apiCall)
  rJson = json.loads(r.text)
  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      print 'id,name,oid,target,poller,snmpString'
      for oid in rJson['response']['obj']:
        print '%s,%s,%s,%s,%s,%s' % (oid['id'],
                                     oid['name'],
                                     oid['oid'],
                                     oid['target'],
                                     oid['poller'],
                                     oid['snmpString'])

    else:
      print 'Error: %s' % rJson['response']['err']
  else:
    print 'Error: Unknown response - %s ' % r.text


def listTypeOid(data, apiEndPoint):
  validInput = 'target=([\w\.]+)\,oid=([\d\.]+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error: Format must be --data target=<name|ip>,oid=<oid>'
    print 'e.g. --data name=1.1.1.1,1.3.6.1.2.1'
    exit(1)

  apiCall = apiEndPoint['urls']['oid'].replace('<string:target>', validatedInput.group(1))
  apiCall = apiCall.replace('<string:oid>', validatedInput.group(2))
  r = requests.get(apiCall)
  rJson = json.loads(r.text)

  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      res = rJson['response']['obj']
      print '%s,%s,%s,%s,%s' % (res['id'],
                                res['target'],
                                res['oid'],
                                res['poller'],
                                res['name'])
    else:
      print 'Error: %s' % rJson['response']['err']
  else:
    print 'Error: Unknown response - %s ' % r.text


def deleteTypeOid(data, apiEndPoint):
  validInput = 'target=([\w\.]+)\,oid=([\d\.]+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error: Format must be --data target=<name|ip>,oid=<oid>'
    print 'e.g. --data name=1.1.1.1,1.3.6.1.2.1'
    exit(1)

  apiCall = apiEndPoint['urls']['oid'].replace('<string:target>', validatedInput.group(1))
  apiCall = apiCall.replace('<string:oid>', validatedInput.group(2))
  r = requests.delete(apiCall)
  rJson = json.loads(r.text)

  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      print 'OK'
    else:
      print 'Error: %s' % rJson['response']['err']
  else:
    print 'Error: Unknown response - %s' % r.text