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

  if data == 'help':
    print 'Parameter format must be:'
    print '\tpython SubfragiumCli.py add target name={name|ip},snmpString=<string>'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py add target name=123.123.11.10,snmpString=123'
    print '\tpython SubfragiumCli.py add target name=host.test.com,snmpString=abc'
    exit(0);

  validInput = 'name=([\w\.]+)\,snmpString=(\w+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error - Parameter format must be:'
    print '\tpython SubfragiumCli.py add target name={name|ip},snmpString=<string>'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py add target name=123.123.11.10,snmpString=123'
    print '\tpython SubfragiumCli.py add target name=host.test.com,snmpString=abc'
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


def listTypeTargets(data, apiEndpoint):

  if data == 'help':
    print 'Parameter format must be:'
    print '\tpython SubfragiumCli.py list targets all'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py list targets all'
    print '\tpython SubfragiumCli.py list targets all'
    exit(0);

  apiCall = apiEndpoint['urls']['targets']
  r = requests.get(apiCall)
  rJson = json.loads(r.text)
  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      print 'Name\t\tSnmpString'
      print '----\t\t----------'
      for target in rJson['response']['obj']:
        print '%s\t%s' % (target['name'], target['snmpString'])
    else:
      print 'Error: %s' % rJson['response']['err']
  else:
    print 'Error: Unknown response - %s ' % r.text


def listTypeTarget(data, apiEndpoint):

  if data == 'help':
    print 'Parameter format must be:'
    print '\tpython SubfragiumCli.py list target name={name|ip}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py list target name=123.123.1.10'
    print '\tpython SubfragiumCli.py list target name=test.host.com'
    exit(0);

  validInput = 'name=([\w\.]+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error  - Parameter format must be:'
    print '\tpython SubfragiumCli.py list target name={name|ip}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py list target name=123.123.1.10'
    print '\tpython SubfragiumCli.py list target name=test.host.com'
    exit(1)

  apiCall = apiEndpoint['urls']['target'].replace('<string:name>', '')
  apiCall = apiCall + validatedInput.group(1)
  r = requests.get(apiCall)
  rJson = json.loads(r.text)

  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      print 'Name\t\tSnmpString'
      print '----\t\t----------'
      res = rJson['response']['obj']
      print '%s\t%s' % (res['name'], res['snmpString'])
    else:
      print 'Error: %s' % rJson['response']['err']
  else:
    print 'Error: Unknown response - %s ' % r.text


def deleteTypeTarget(data, apiEndpoint):

  if data == 'help':
    print 'Parameter format must be:'
    print '\tpython SubfragiumCli.py delete target name={name|ip}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py delete target name=123.123.1.10'
    print '\tpython SubfragiumCli.py delete target name=test.host.com'
    exit(0);

  validInput = 'name=([\w\.]+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error Parameter format must be:'
    print '\tpython SubfragiumCli.py delete target name={name|ip}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py delete target name=123.123.1.10'
    print '\tpython SubfragiumCli.py delete target name=test.host.com'
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

  if data == 'help':
    print 'Parameter format must be:'
    print '\tpython SubfragiumCli.py modify target name={name|ip},snmpString={string}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py modify target name=123.123.1.10,snmpString=123abc'
    print '\tpython SubfragiumCli.py modify target name=host.test.com,snmpString=123abc'
    exit(0)

  validInput = 'name=([\w\.]+)\,snmpString=(\w+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error - Parameter format must be:'
    print '\tpython SubfragiumCli.py modify target name={name|ip},snmpString={string}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py modify target name=123.123.1.10,snmpString=123abc'
    print '\tpython SubfragiumCli.py modify target name=host.test.com,snmpString=123ab'
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

  if data == 'help':
    print 'Parameter format must be:'
    print '\tpython SubfragiumCli.py add poller name={name},minProcesses={num},maxProcesses={num},numProcesses={num},holdDown={num},cycleTime={num},storageType={graphite},storageLocation=pickle://{string}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py add poller name=poller1,minProcesses=1,maxProcesses=10,numProcesses=5,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://graphite:5000'
    print '\tpython SubfragiumCli.py add poller name=poller2,minProcesses=1,maxProcesses=10,numProcesses=5,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000'
    exit(0)

  validInput = 'name=([\w\.]+)\,minProcesses=(\d+)\,maxProcesses=(\d+)\,numProcesses=(\d+)\,holdDown=(\d+),cycleTime=(\d+),storageType=(\w+),storageLocation=([\w\.\:\/]+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error - Parameter format must be:'
    print '\tpython SubfragiumCli.py add poller name={name},minProcesses={num},maxProcesses={num},numProcesses={num},holdDown={num},cycleTime={num},storageType={graphite},storageLocation=pickle://{string}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py add poller name=poller1,minProcesses=1,maxProcesses=10,numProcesses=5,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://graphite:5000'
    print '\tpython SubfragiumCli.py add poller name=poller2,minProcesses=1,maxProcesses=10,numProcesses=5,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000'
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


def listTypePollers(data, apiEndPoint):

  if data == 'help':
    print 'Parameter format must be:'
    print '\tpython SubfragiumCli.py list pollers all'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py list pollers all'
    print '\tpython SubfragiumCli.py list pollers all'
    exit(0)

  apiCall = apiEndPoint['urls']['pollers']
  r = requests.get(apiCall)
  rJson = json.loads(r.text)
  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      print 'name\t\tminProcesses\tmaxProcesses\tnumProcesses\tholdDown\tcycleTime\tstorageType\tstorageLocation'
      print '----\t\t------------\t------------\t------------\t--------\t---------\t-----------\t---------------'
      for poller in rJson['response']['obj']:
        print '%s\t\t%s\t\t%s\t\t%s\t\t%s\t\t%s\t\t%s\t%s' % (poller['name'],
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

  if data == 'help':
    print 'Parameter format must be:'
    print '\tpython SubfragiumCli.py list poller name={name}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py list poller name=poller1'
    exit(0)

  validInput = 'name=([\w\.]+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error - Parameter format must be:'
    print '\tpython SubfragiumCli.py list poller name={name}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py list poller name=poller1'
    exit(1)

  apiCall = apiEndPoint['urls']['poller'].replace('<string:name>', '')
  apiCall = apiCall + validatedInput.group(1)
  r = requests.get(apiCall)
  rJson = json.loads(r.text)

  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      res = rJson['response']['obj']
      print 'name\t\tminProcesses\tmaxProcesses\tnumProcesses\tholdDown\tcycleTime\tstorageType\tstorageLocation'
      print '----\t\t------------\t------------\t------------\t--------\t---------\t-----------\t---------------'
      print '%s\t\t%s\t\t%s\t\t%s\t\t%s\t\t%s\t\t%s\t%s' % (res['name'],
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

  if data == 'help':
    print 'Parameter format must be:'
    print '\tpython SubfragiumCli.py delete poller name={name}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py delete poller name=poller1'
    exit(0)

  validInput = 'name=([\w\.]+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error - Parameter format must be:'
    print '\tpython SubfragiumCli.py delete poller name={name}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py delete poller name=poller1'
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

  if data == 'help':
    print 'Parameter format must be:'
    print '\tpython SubfragiumCli.py modify poller name={name},{minProcesses=<num>|maxProcesses=<num>|numProcesses=<num>|holdDown=<num>|cycleTime=<num>|storageType=<name>|storageLocation=<location>}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py modify poller name=poller1,minProcesses=10'
    print '\tpython SubfragiumCli.py modify poller name=poller1,maxProcesses=50'
    print '\tpython SubfragiumCli.py modify poller name=poller1,numProcesses=2'
    print '\tpython SubfragiumCli.py modify poller name=poller1,holdDown=20'
    print '\tpython SubfragiumCli.py modify poller name=poller1,cycleTime=60'
    print '\tpython SubfragiumCli.py modify poller name=poller1,storageType=graphite'
    print '\tpython SubfragiumCli.py modify poller name=poller1,storageType=pickle://graphite:5000'
    exit(0)

  validInput = '^(name=([\w\.]+)),(minProcesses=\d+|maxProcesses=\d+|numProcesses=\d+|holdDown=\d+|cycleTime=\d+|storageType=\w+|storageLocation=[\w\.\:\/]+)$'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error - Parameter format must be:'
    print '\tpython SubfragiumCli.py modify poller name={name},{minProcesses=<num>|maxProcesses=<num>|numProcesses=<num>|holdDown=<num>|cycleTime=<num>|storageType=<name>|storageLocation=<location>}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py modify poller name=poller1,minProcesses=10'
    print '\tpython SubfragiumCli.py modify poller name=poller1,maxProcesses=50'
    print '\tpython SubfragiumCli.py modify poller name=poller1,numProcesses=2'
    print '\tpython SubfragiumCli.py modify poller name=poller1,holdDown=20'
    print '\tpython SubfragiumCli.py modify poller name=poller1,cycleTime=60'
    print '\tpython SubfragiumCli.py modify poller name=poller1,storageType=graphite'
    print '\tpython SubfragiumCli.py modify poller name=poller1,storageType=pickle://graphite:5000'
    exit(1)

  (field, value) = validatedInput.group(3).split('=')

  apiCall = apiEndPoint['urls']['poller'].replace('<string:name>', '')
  apiCall = apiCall + validatedInput.group(2)
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

  if field != 'storageType' and field != 'storageLocation':
    modifiedPoller[field] = int(value)
  else:
    modifiedPoller[field] = value

  jsonStr = json.dumps(modifiedPoller)

  apiCall = apiEndPoint['urls']['poller'].replace('<string:name>', '')
  apiCall = apiCall + validatedInput.group(2)

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

  if data == 'help':
    print 'Parameter format must be:'
    print '\tpython SubfragiumCli.py add oid target={name|ip},oid=<oid>,poller={poller},name={name}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py add oid target=host.test.com,oid=1.3.6.1.2.1,poller=poller1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0'
    print '\tpython SubfragiumCli.py add oid target=123.123.1.10,oid=1.3.6.1.2.1,poller=poller1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0'
    exit(0)

  validInput = 'target=([\w\.]+)\,oid=([\d\.]+)\,poller=(\w+)\,name=([\w\.\/\-]+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error - Parameter format must be:'
    print '\tpython SubfragiumCli.py add oid target={name|ip},oid=<oid>,poller={poller},name={name}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py add oid target=host.test.com,oid=1.3.6.1.2.1,poller=poller1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0'
    print '\tpython SubfragiumCli.py add oid target=123.123.1.10,oid=1.3.6.1.2.1,poller=poller1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0'
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

  if data == 'help':
    print 'Parameter format must be:'
    print '\tpython SubfragiumCli.py modify oid target={name|ip},oid=<oid>,{poller={poller}|name={name}}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py modify oid target=host.test.com,oid=1.3.6.1.2.1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0'
    print '\tpython SubfragiumCli.py modify oid target=123.123.1.10,oid=1.3.6.1.2.1,poller=poller1'
    exit(0)

  validInput = 'target=([\w\.]+),oid=([\d\.]+),(poller=(\w+)|name=([\w\.]+))'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error - Parameter format must be:'
    print '\tpython SubfragiumCli.py modify oid target={name|ip},oid=<oid>,{poller={poller}|name={name}}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py modify oid target=host.test.com,oid=1.3.6.1.2.1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0'
    print '\tpython SubfragiumCli.py modify oid target=123.123.1.10,oid=1.3.6.1.2.1,poller=poller1'
    exit(1)

  print validatedInput.group(0)
  print validatedInput.group(1)
  print validatedInput.group(2)
  print validatedInput.group(3)
  (field, value) = validatedInput.group(3).split('=')

  apiCall = apiEndPoint['urls']['oid'].replace('<string:target>', validatedInput.group(1))
  apiCall = apiCall.replace('<string:oid>', validatedInput.group(2))
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

  modifiedOid = rJson['response']['obj']
  del (modifiedOid['id'])
  del (modifiedOid['snmpString'])
  del (modifiedOid['target'])
  del (modifiedOid['oid'])
  modifiedOid[field] = value

  jsonStr = json.dumps(modifiedOid)

  apiCall = apiEndPoint['urls']['oid'].replace('<string:target>', validatedInput.group(1))
  apiCall = apiCall.replace('<string:oid>', validatedInput.group(2))

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


def listTypeOids(data, apiEndPoint):

  if data == 'help':
    print 'Parameter format must be:'
    print '\tpython SubfragiumCli.py list oids target={name|ip},oid=<oid>,poller={poller},name={name}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py list oids target=host.test.com,oid=1.3.6.1.2.1,poller=poller1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0'
    print '\tpython SubfragiumCli.py list oids target=123.123.1.10,oid=1.3.6.1.2.1,poller=poller1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0'
    exit(0)

  validInput = 'all|target=([\w\.]+)|oid=([\d\.]+)|poller=(\w+)|name=([\w\.]+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)

  if validatedInput == None:
    print 'Error - Parameter format must be:'
    print '\tpython SubfragiumCli.py list oids target={name|ip},oid=<oid>,poller={poller},name={name}'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py list oids target=host.test.com,oid=1.3.6.1.2.1,poller=poller1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0'
    print '\tpython SubfragiumCli.py list oids target=123.123.1.10,oid=1.3.6.1.2.1,poller=poller1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0'
    exit(1)


  apiCall = apiEndPoint['urls']['oids']

  if validatedInput.group(0) != 'all':

    (field, value) = validatedInput.group(0).split('=')
    apiCall = apiCall + '?%s=%s' % (field, value)

  r = requests.get(apiCall)
  rJson = json.loads(r.text)

  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      print 'ID\t\t\tName\t\tOID\t\tTarget\t\tPoller\t\tSnmpString'
      print '--\t\t\t----\t\t---\t\t------\t\t------\t\t----------'
      for oid in rJson['response']['obj']:
        print '%s\t%s\t%s\t%s\t%s\t\t%s' % (oid['id'],
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

  if data == 'help':
    print 'Parameter format must be:'
    print '\tpython SubfragiumCli.py list oid target={name|ip},oid=<oid>'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py list oid target=host.test.com,oid=1.3.6.1.2.1'
    print '\tpython SubfragiumCli.py list oid target=123.123.1.10,oid=1.3.6.1.2.1'
    exit(0)

  validInput = 'target=([\w\.]+)\,oid=([\d\.]+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error - Parameter format must be:'
    print '\tpython SubfragiumCli.py list oid target={name|ip},oid=<oid>'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py list oid target=host.test.com,oid=1.3.6.1.2.1'
    print '\tpython SubfragiumCli.py list oid target=123.123.1.10,oid=1.3.6.1.2.1'
    exit(1)

  apiCall = apiEndPoint['urls']['oid'].replace('<string:target>', validatedInput.group(1))
  apiCall = apiCall.replace('<string:oid>', validatedInput.group(2))
  r = requests.get(apiCall)
  rJson = json.loads(r.text)

  if 'response' in rJson:
    if 'success' in rJson['response'] and rJson['response']['success']:
      print 'ID\t\t\t\tTarget\t\tOID\t\t\tPoller\t\tName'
      print '--\t\t\t\t------\t\t---\t\t\t------\t\t-----'
      res = rJson['response']['obj']
      print '%s\t%s\t%s\t\t%s\t\t%s' % (res['id'],
                                res['target'],
                                res['oid'],
                                res['poller'],
                                res['name'])
    else:
      print 'Error: %s' % rJson['response']['err']
  else:
    print 'Error: Unknown response - %s ' % r.text


def deleteTypeOid(data, apiEndPoint):

  if data == 'help':
    print 'Parameter format must be:'
    print '\tpython SubfragiumCli.py delete oid target={name|ip},oid=<oid>'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py delete oid target=host.test.com,oid=1.3.6.1.2.1'
    print '\tpython SubfragiumCli.py delete oid target=123.123.1.10,oid=1.3.6.1.2.1'
    exit(0)

  validInput = 'target=([\w\.]+)\,oid=([\d\.]+)'
  reValidator = re.compile(validInput)
  validatedInput = reValidator.match(data)
  if validatedInput == None:
    print 'Error - Parameter format must be:'
    print '\tpython SubfragiumCli.py delete oid target={name|ip},oid=<oid>'
    print
    print '\te.g.'
    print '\tpython SubfragiumCli.py delete oid target=host.test.com,oid=1.3.6.1.2.1'
    print '\tpython SubfragiumCli.py delete oid target=123.123.1.10,oid=1.3.6.1.2.1'
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