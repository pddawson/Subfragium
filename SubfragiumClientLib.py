import requests
import json
import re
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
    except urllib2.URLError:
        return {'success': False, 'err': 'Could not get API End Points from %s' % apiServer}


def validateResponse(response, getResponse):

    try:
      payload = response.text
    except AttributeError:
      return {'success': False, 'err': 'Error: No text in response'}
  
    rJson = json.loads(payload)
    if 'response' in rJson:
        if 'success' in rJson['response'] and rJson['response']['success']:
            if getResponse:
                return {'success': True, 'obj': rJson['response']['obj']}
            else:
                return {'success': True}
        elif 'err' in rJson['response']:
            return {'success': False, 'err': rJson['response']['err']}
        else:
            return {'success': False, 'err': 'Error: Missing success/err field - %s' % rJson}
    else:
        return {'success': False, 'err': 'Error: Unknown response - %s' % response.text}


def addTypeTarget(data, apiEndpoint):

    if data == 'help':
        helpMsg = 'Parameter format must be:\n'
        helpMsg += '\tpython SubfragiumCli.py add target name={name|ip},snmpString=<string>,timeout=<int>\n'
        helpMsg += '\n'
        helpMsg += '\n'
        helpMsg += '\te.g.\n'
        helpMsg += '\tpython SubfragiumCli.py add target name=123.123.11.10,snmpString=123,timeout=10\n'
        helpMsg += '\tpython SubfragiumCli.py add target name=host.test.com,snmpString=abc,timeout=25\n'
        return {'success': True, 'helpMsg': helpMsg}

    validInput = 'name=([\w\.]+)\,snmpString=(\w+),timeout=(\d+)'
    reValidator = re.compile(validInput)
    validatedInput = reValidator.match(data)
    if validatedInput is None:
        errMsg = 'Parameter format must be:\n'
        errMsg += '\tpython SubfragiumCli.py add target name={name|ip},snmpString=<string>,timeout=<int>\n'
        errMsg += '\n'
        errMsg += '\te.g.\n'
        errMsg += '\tpython SubfragiumCli.py add target name=123.123.11.10,snmpString=123,timeout=10\n'
        errMsg += '\tpython SubfragiumCli.py add target name=host.test.com,snmpString=abc,timeout=25\n'
        return {'success': False, 'err': errMsg}

    apiCall = {'snmpString': validatedInput.group(2), 'timeout': int(validatedInput.group(3))}
    jsonCall = json.dumps(apiCall)

    headers = {'content-type': 'application/json'}
    apiCall = apiEndpoint['urls']['target'].replace('<string:name>', '')
    apiCall += validatedInput.group(1)
    r = requests.put(apiCall, data=jsonCall, headers=headers)
    return validateResponse(r, False)


def listTypeTargets(data, apiEndpoint):

    if data == 'help':
        helpMsg = 'Parameter format must be:\n'
        helpMsg += '\tpython SubfragiumCli.py list targets all\n'
        helpMsg += '\n'
        helpMsg += '\te.g.\n'
        helpMsg += '\tpython SubfragiumCli.py list targets all\n'
        helpMsg += '\tpython SubfragiumCli.py list targets all\n'
        return {'success': True, 'helpMsg': helpMsg}

    apiCall = apiEndpoint['urls']['targets']
    r = requests.get(apiCall)
    return validateResponse(r, True)


def listTypeTarget(data, apiEndpoint):

    if data == 'help':
        helpMsg = 'Parameter format must be:\n'
        helpMsg += '\tpython SubfragiumCli.py list target name={name|ip}\n'
        helpMsg += '\n'
        helpMsg += '\te.g.\n'
        helpMsg += '\tpython SubfragiumCli.py list target name=123.123.1.10\n'
        helpMsg += '\tpython SubfragiumCli.py list target name=test.host.com\n'
        return {'success': True, 'helpMsg': helpMsg}

    validInput = 'name=([\w\.]+)'
    reValidator = re.compile(validInput)
    validatedInput = reValidator.match(data)
    if validatedInput is None:
        errorMsg = 'Error  - Parameter format must be:\n'
        errorMsg += '\tpython SubfragiumCli.py list target name={name|ip}\n'
        errorMsg += '\n'
        errorMsg += '\te.g.\n'
        errorMsg += '\tpython SubfragiumCli.py list target name=123.123.1.10\n'
        errorMsg += '\tpython SubfragiumCli.py list target name=test.host.com\n'
        return {'success': False, 'err': errorMsg}

    apiCall = apiEndpoint['urls']['target'].replace('<string:name>', '')
    apiCall += validatedInput.group(1)
    r = requests.get(apiCall)
    return validateResponse(r, True)


def deleteTypeTarget(data, apiEndpoint):

    if data == 'help':
        helpMsg = 'Parameter format must be:\n'
        helpMsg += '\tpython SubfragiumCli.py delete target name={name|ip}\n'
        helpMsg += '\n'
        helpMsg += '\te.g.\n'
        helpMsg += '\tpython SubfragiumCli.py delete target name=123.123.1.10\n'
        helpMsg += '\tpython SubfragiumCli.py delete target name=test.host.com\n'
        return {'success': True, 'helpMsg': helpMsg}

    validInput = 'name=([\w\.]+)'
    reValidator = re.compile(validInput)
    validatedInput = reValidator.match(data)
    if validatedInput is None:
        errorMsg = 'Error Parameter format must be:\n'
        errorMsg += '\tpython SubfragiumCli.py delete target name={name|ip}\n'
        errorMsg += '\n'
        errorMsg += '\te.g.\n'
        errorMsg += '\tpython SubfragiumCli.py delete target name=123.123.1.10\n'
        errorMsg += '\tpython SubfragiumCli.py delete target name=test.host.com\n'
        return {'success': False, 'err': errorMsg}

    apiCall = apiEndpoint['urls']['target'].replace('<string:name>', '')
    apiCall += validatedInput.group(1)
    r = requests.delete(apiCall)
    return validateResponse(r, False)


def modifyTypeTarget(data, apiEndpoint):

    if data == 'help':
        helpMsg = 'Parameter format must be:\n'
        helpMsg += '\tpython SubfragiumCli.py modify target name={name|ip},{snmpString={string}|timeout={number}\n'
        helpMsg += '\n'
        helpMsg += '\te.g.\n'
        helpMsg += '\tpython SubfragiumCli.py modify target name=123.123.1.10,snmpString=123abc\n'
        helpMsg += '\tpython SubfragiumCli.py modify target name=host.test.com,timeout=600\n'
        return {'success': True, 'helpMsg': helpMsg}

    validInput = 'name=([\w\.]+)\,(snmpString=(\w+)|timeout=(\d+))'
    reValidator = re.compile(validInput)
    validatedInput = reValidator.match(data)
    if validatedInput is None:
        errorMsg = 'Error - Parameter format must be:\n'
        errorMsg += '\tpython SubfragiumCli.py modify target name={name|ip},{snmpString={string}|timeout={number}\n'
        errorMsg += '\n'
        errorMsg += '\te.g.\n'
        errorMsg += '\tpython SubfragiumCli.py modify target name=123.123.1.10,snmpString=123abc\n'
        errorMsg += '\tpython SubfragiumCli.py modify target name=host.test.com,timeout=600\n'
        return {'success': False, 'err': errorMsg}

    (field, value) = validatedInput.group(2).split('=')

    apiCall = apiEndpoint['urls']['target'].replace('<string:name>', '')
    apiCall += validatedInput.group(1)
    r = requests.get(apiCall)
    rJson = json.loads(r.text)
    if 'response' not in rJson:
        return {'success': False, 'err': 'Error: Unknown response %s' % r.text}

    if 'success' not in rJson['response']:
        return {'success': False, 'err': 'Error: Bad response %s' % rJson['response']}

    if not rJson['response']['success']:
        return {'success': False, 'err': 'Error: Failed %s' % rJson['response']['err']}

    modifiedTarget = rJson['response']['obj']
    if field == 'timeout':
        modifiedTarget[field] = int(value)
    else:
        modifiedTarget[field] = value

    del (modifiedTarget['name'])
    jsonCall = json.dumps(modifiedTarget)

    headers = {'content-type': 'application/json'}
    apiCall = apiEndpoint['urls']['target'].replace('<string:name>', '')
    apiCall += validatedInput.group(1)
    r = requests.put(apiCall, data=jsonCall, headers=headers)
    return validateResponse(r, False)


def addTypePoller(data, apiEndPoint):

    if data == 'help':
        helpMsg = 'Parameter format must be:\n'
        helpMsg += '\tpython SubfragiumCli.py add poller name={name},minProcesses={num},maxProcesses={num},numProcesses={num},holdDown={num},cycleTime={num},storageType={graphite},storageLocation=pickle://{string},disabled={True|False},errorThreshold=<num>,errorHoldTime=<num>\n'
        helpMsg += '\n'
        helpMsg += '\te.g.\n'
        helpMsg += '\tpython SubfragiumCli.py add poller name=poller1,minProcesses=1,maxProcesses=10,numProcesses=5,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://graphite:5000,disabled=True,errorThreshold=3,errorHoldTime=1800\n'
        helpMsg += '\tpython SubfragiumCli.py add poller name=poller2,minProcesses=1,maxProcesses=10,numProcesses=5,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=3,errorHoldTime=1800\n'
        return {'success': True, 'helpMsg': helpMsg}

    validInput = 'name=([\w\.]+)\,minProcesses=(\d+)\,maxProcesses=(\d+)\,numProcesses=(\d+)\,holdDown=(\d+),cycleTime=(\d+),storageType=(\w+),storageLocation=(\w+\:\/\/[\w\-\.]+\:\d+),disabled=(True|False),errorThreshold=(\d+),errorHoldTime=(\d+)'
    reValidator = re.compile(validInput)
    validatedInput = reValidator.match(data)
    if validatedInput is None:
        errMsg = 'Error - Parameter format must be:\n'
        errMsg += '\tpython SubfragiumCli.py add poller name={name},minProcesses={num},maxProcesses={num},numProcesses={num},holdDown={num},cycleTime={num},storageType={graphite},storageLocation=pickle://{string},disabled={True|False},errorThreshold=<num>,errorHoldTime=<num>\n'
        errMsg += '\n'
        errMsg += '\te.g.\n'
        errMsg += '\tpython SubfragiumCli.py add poller name=poller1,minProcesses=1,maxProcesses=10,numProcesses=5,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://graphite:5000,disabled=True,errorThreshold=3,errorHoldTime=1800\n'
        errMsg += '\tpython SubfragiumCli.py add poller name=poller2,minProcesses=1,maxProcesses=10,numProcesses=5,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=3,errorHoldTime=1800\n'
        return {'success': False, 'err': errMsg}

    payload = {
        'minProcesses': int(validatedInput.group(2)),
        'maxProcesses': int(validatedInput.group(3)),
        'numProcesses': int(validatedInput.group(4)),
        'holdDown': int(validatedInput.group(5)),
        'cycleTime': int(validatedInput.group(6)),
        'storageType': validatedInput.group(7),
        'storageLocation': validatedInput.group(8),
        'disabled': validatedInput.group(9),
        'errorThreshold': int(validatedInput.group(10)),
        'errorHoldTime': int(validatedInput.group(11))
    }
    if validatedInput.group(9):
        payload['disabled'] = True
    else:
        payload['disabled'] = False

    jsonStr = json.dumps(payload)

    apiCall = apiEndPoint['urls']['poller'].replace('<string:name>', '')
    apiCall += validatedInput.group(1)

    headers = {'content-type': 'application/json'}
    r = requests.put(apiCall, data=jsonStr, headers=headers)
    return validateResponse(r, False)


def listTypePollers(data, apiEndPoint):

    if data == 'help':
        helpMsg = 'Parameter format must be:\n'
        helpMsg += '\tpython SubfragiumCli.py list pollers all\n'
        helpMsg += '\n'
        helpMsg += '\te.g.\n'
        helpMsg += '\tpython SubfragiumCli.py list pollers all\n'
        helpMsg += '\tpython SubfragiumCli.py list pollers all\n'
        return {'success': True, 'helpMsg': helpMsg}

    apiCall = apiEndPoint['urls']['pollers']
    r = requests.get(apiCall)
    return validateResponse(r, True)


def listTypePoller(data, apiEndPoint):

    if data == 'help':
        helpMsg = 'Parameter format must be:\n'
        helpMsg += '\tpython SubfragiumCli.py list poller name={name}\n'
        helpMsg += '\n'
        helpMsg += '\te.g.\n'
        helpMsg += '\tpython SubfragiumCli.py list poller name=poller1\n'
        return {'success': True, 'helpMsg': helpMsg}

    validInput = 'name=([\w\.]+)'
    reValidator = re.compile(validInput)
    validatedInput = reValidator.match(data)
    if validatedInput is None:
        errorMsg = 'Error - Parameter format must be:\n'
        errorMsg += '\tpython SubfragiumCli.py list poller name={name}\n'
        errorMsg += '\n'
        errorMsg += '\te.g.\n'
        errorMsg += '\tpython SubfragiumCli.py list poller name=poller1\n'
        return {'success': False, 'err': errorMsg}

    apiCall = apiEndPoint['urls']['poller'].replace('<string:name>', '')
    apiCall += validatedInput.group(1)
    r = requests.get(apiCall)
    return validateResponse(r, True)


def deleteTypePoller(data, apiEndPoint):

    if data == 'help':
        helpMsg = 'Parameter format must be:\n'
        helpMsg += '\tpython SubfragiumCli.py delete poller name={name}\n'
        helpMsg += '\n'
        helpMsg += '\te.g.\n'
        helpMsg += '\tpython SubfragiumCli.py delete poller name=poller1\n'
        return {'success': True, 'helpMsg': helpMsg}

    validInput = 'name=([\w\.]+)'
    reValidator = re.compile(validInput)
    validatedInput = reValidator.match(data)
    if validatedInput is None:
        errorMsg = 'Error - Parameter format must be:\n'
        errorMsg += '\tpython SubfragiumCli.py delete poller name={name}\n'
        errorMsg += '\n'
        errorMsg += '\te.g.\n'
        errorMsg += '\tpython SubfragiumCli.py delete poller name=poller1\n'
        return {'success': False, 'err': errorMsg}

    apiCall = apiEndPoint['urls']['poller'].replace('<string:name>', '')
    apiCall += validatedInput.group(1)
    r = requests.delete(apiCall)
    return validateResponse(r, False)


def modifyTypePoller(data, apiEndPoint):

    if data == 'help':
        helpMsg = 'Parameter format must be:\n'
        helpMsg += '\tpython SubfragiumCli.py modify poller name={name},{minProcesses=<num>|maxProcesses=<num>|numProcesses=<num>|holdDown=<num>|cycleTime=<num>|storageType=<name>|storageLocation=<location>|disabled={True|False}|errorThreshold=<num>|errorHoldTime=<num>\n'
        helpMsg += '\n'
        helpMsg += '\te.g.\n'
        helpMsg += '\tpython SubfragiumCli.py modify poller name=poller1,minProcesses=10\n'
        helpMsg += '\tpython SubfragiumCli.py modify poller name=poller1,maxProcesses=50\n'
        helpMsg += '\tpython SubfragiumCli.py modify poller name=poller1,numProcesses=2\n'
        helpMsg += '\tpython SubfragiumCli.py modify poller name=poller1,holdDown=20\n'
        helpMsg += '\tpython SubfragiumCli.py modify poller name=poller1,cycleTime=60\n'
        helpMsg += '\tpython SubfragiumCli.py modify poller name=poller1,storageType=graphite\n'
        helpMsg += '\tpython SubfragiumCli.py modify poller name=poller1,storageType=pickle://graphite:5000\n'
        helpMsg += '\tpython SubfragiumCli.py modify poller name=poller1,disabled=True\n'
        helpMsg += '\tpython SubfragiumCli.py modify poller name=poller1,errorThreshold=4\n'
        helpMsg += '\tpython SubfragiumCli.py modify poller name=poller1,errorHoldTime=1800\n'
        return {'success': True, 'helpMsg': helpMsg}

    validInput = '^(name=([\w\.]+)),(minProcesses=\d+|maxProcesses=\d+|numProcesses=\d+|holdDown=\d+|cycleTime=\d+|storageType=\w+|storageLocation=[\w\.\:\/]+|disabled=(True|False)|errorThreshold=\d+|errorHoldTime=\d+)$'
    reValidator = re.compile(validInput)
    validatedInput = reValidator.match(data)
    if validatedInput is None:
        errorMsg = 'Error - Parameter format must be:\n'
        errorMsg += '\tpython SubfragiumCli.py modify poller name={name},{minProcesses=<num>|maxProcesses=<num>|numProcesses=<num>|holdDown=<num>|cycleTime=<num>|storageType=<name>|storageLocation=<location>|disabled={True|False}|errorThreshold=<num>|errorHoldTime=<num>\n'
        errorMsg += '\n'
        errorMsg += '\te.g.\n'
        errorMsg += '\tpython SubfragiumCli.py modify poller name=poller1,minProcesses=10\n'
        errorMsg += '\tpython SubfragiumCli.py modify poller name=poller1,maxProcesses=50\n'
        errorMsg += '\tpython SubfragiumCli.py modify poller name=poller1,numProcesses=2\n'
        errorMsg += '\tpython SubfragiumCli.py modify poller name=poller1,holdDown=20\n'
        errorMsg += '\tpython SubfragiumCli.py modify poller name=poller1,cycleTime=60\n'
        errorMsg += '\tpython SubfragiumCli.py modify poller name=poller1,storageType=graphite\n'
        errorMsg += '\tpython SubfragiumCli.py modify poller name=poller1,storageType=pickle://graphite:5000\n'
        errorMsg += '\tpython SubfragiumCli.py modify poller name=poller1,errorThreshold=4\n'
        errorMsg += '\tpython SubfragiumCli.py modify poller name=poller1,errorHoldTime=1800\n'
        errorMsg += '\tpython SubfragiumCli.py modify poller name=poller1,disabled=True\n'
        return {'success': False, 'err': errorMsg}

    (field, value) = validatedInput.group(3).split('=')

    apiCall = apiEndPoint['urls']['poller'].replace('<string:name>', '')
    apiCall += validatedInput.group(2)
    r = requests.get(apiCall)
    rJson = json.loads(r.text)
    if 'response' not in rJson:
        return {'success': False, 'err': 'Error: Unknown response %s' % r.text}

    if 'success' not in rJson['response']:
        return {'success': False, 'err': 'Error: Bad response %s' % rJson['response']}

    if not rJson['response']['success']:
        return {'success': False, 'err': 'Error: Failed %s' % rJson['response']['err']}

    modifiedPoller = rJson['response']['obj']
    del(modifiedPoller['name'])

    if field == 'disabled' and value == 'True':
        modifiedPoller[field] = True
    elif field == 'disabled' and value == 'False':
        modifiedPoller[field] = False
    elif field != 'storageType' and field != 'storageLocation':
        modifiedPoller[field] = int(value)
    else:
        modifiedPoller[field] = value

    jsonStr = json.dumps(modifiedPoller)

    apiCall = apiEndPoint['urls']['poller'].replace('<string:name>', '')
    apiCall += validatedInput.group(2)

    headers = {'content-type': 'application/json'}
    r = requests.put(apiCall, data=jsonStr, headers=headers)
    return validateResponse(r, False)


def addTypeOid(data, apiEndPoint):

    if data == 'help':
        helpMsg = 'Parameter format must be:\n'
        helpMsg += '\tpython SubfragiumCli.py add oid target={name|ip},oid=<oid>,poller={poller},name={name},enabled={True|False}\n'
        helpMsg += '\n'
        helpMsg += '\te.g.\n'
        helpMsg += '\tpython SubfragiumCli.py add oid target=host.test.com,oid=1.3.6.1.2.1,poller=poller1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0,enabled=False\n'
        helpMsg += '\tpython SubfragiumCli.py add oid target=123.123.1.10,oid=1.3.6.1.2.1,poller=poller1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0,enabled=True\n'
        return {'success': True, 'helpMsg': helpMsg}

    validInput = 'target=([\w\.]+)\,oid=([\d\.]+)\,poller=(\w+)\,name=([\w\.\/\-]+)\,enabled=(True|False)'
    reValidator = re.compile(validInput)
    validatedInput = reValidator.match(data)
    if validatedInput is None:
        errMsg = 'Error - Parameter format must be:\n'
        errMsg += '\tpython SubfragiumCli.py add oid target={name|ip},oid=<oid>,poller={poller},name={name},enabled={True|False}\n'
        errMsg += '\n'
        errMsg += '\te.g.\n'
        errMsg += '\tpython SubfragiumCli.py add oid target=host.test.com,oid=1.3.6.1.2.1,poller=poller1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0,enabled=False\n'
        errMsg += '\tpython SubfragiumCli.py add oid target=123.123.1.10,oid=1.3.6.1.2.1,poller=poller1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0,enabled=True\n'
        return {'success': False, 'err': errMsg}

    if validatedInput.group(5) == 'True':
        enabled = True
    else:
        enabled = False

    payload = {'poller': validatedInput.group(3), 'name': validatedInput.group(4), 'enabled': enabled}
    jsonStr = json.dumps(payload)

    apiCall = apiEndPoint['urls']['oid'].replace('<string:tgt>', validatedInput.group(1))
    apiCall = apiCall.replace('<string:oidInfo>', validatedInput.group(2))
    headers = {'content-type': 'application/json'}
    r = requests.put(apiCall, data=jsonStr, headers=headers)
    return validateResponse(r, False)


def modifyTypeOid(data, apiEndPoint):

    if data == 'help':
        helpMsg = 'Parameter format must be:\n'
        helpMsg += '\tpython SubfragiumCli.py modify oid target={name|ip},oid=<oid>,{poller={poller}|name={name}|enabled={True|False}}\n'
        helpMsg += '\n'
        helpMsg += '\te.g.\n'
        helpMsg += '\tpython SubfragiumCli.py modify oid target=host.test.com,oid=1.3.6.1.2.1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0,enabled=True\n'
        helpMsg += '\tpython SubfragiumCli.py modify oid target=123.123.1.10,oid=1.3.6.1.2.1,poller=poller1,enabled=True\n'
        return {'success': True, 'helpMsg': helpMsg}

    validInput = 'target=([\w\.]+),oid=([\d\.]+),(poller=(\w+)|name=([\w\.]+)|enabled=(True|False))'
    reValidator = re.compile(validInput)
    validatedInput = reValidator.match(data)
    if validatedInput is None:
        errorMsg = 'Error - Parameter format must be:\n'
        errorMsg += '\tpython SubfragiumCli.py modify oid target={name|ip},oid=<oid>,{poller={poller}|name={name}|enabled={True|False}}\n'
        errorMsg += '\n'
        errorMsg += '\te.g.\n'
        errorMsg += '\tpython SubfragiumCli.py modify oid target=host.test.com,oid=1.3.6.1.2.1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0,enabled=True\n'
        errorMsg += '\tpython SubfragiumCli.py modify oid target=123.123.1.10,oid=1.3.6.1.2.1,poller=poller1,enabled=True\n'
        return {'success': False, 'err': errorMsg}

    (field, value) = validatedInput.group(3).split('=')

    if field == 'enabled':
        if value == 'True':
            value = True
        else:
            value = False

    apiCall = apiEndPoint['urls']['oid'].replace('<string:tgt>', validatedInput.group(1))
    apiCall = apiCall.replace('<string:oidInfo>', validatedInput.group(2))
    r = requests.get(apiCall)
    rJson = json.loads(r.text)
    if 'response' not in rJson:
        return {'success': False, 'err': 'Error: Unknown response %s' % r.text}

    if 'success' not in rJson['response']:
        return {'success': False, 'err': 'Error: Bad response %s' % rJson['response']}

    if not rJson['response']['success']:
        return {'success': False, 'err': 'Error: Failed %s' % rJson['response']['err']}

    modifiedOid = rJson['response']['obj']
    del (modifiedOid['id'])
    del (modifiedOid['snmpString'])
    del (modifiedOid['target'])
    del (modifiedOid['oid'])
    del (modifiedOid['timeout'])
    modifiedOid[field] = value

    jsonStr = json.dumps(modifiedOid)

    apiCall = apiEndPoint['urls']['oid'].replace('<string:tgt>', validatedInput.group(1))
    apiCall = apiCall.replace('<string:oidInfo>', validatedInput.group(2))

    headers = {'content-type': 'application/json'}
    r = requests.put(apiCall, data=jsonStr, headers=headers)
    return validateResponse(r, False)


def listTypeOids(data, apiEndPoint):

    if data == 'help':
        helpMsg = 'Parameter format must be:\n'
        helpMsg += '\tpython SubfragiumCli.py list oids target={name|ip}|oid=<oid>,|poller={poller}|name={name}|enabled={True|False}\n'
        helpMsg += '\n'
        helpMsg += '\te.g.\n'
        helpMsg += '\tpython SubfragiumCli.py list oids target=host.test.com,oid=1.3.6.1.2.1,poller=poller1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0,enabled=True\n'
        helpMsg += '\tpython SubfragiumCli.py list oids target=123.123.1.10,oid=1.3.6.1.2.1,poller=poller1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0,enabled=True\n'
        return {'success': True, 'helpMsg': helpMsg}

    validInput = 'all|target=([\w\.]+)|oid=([\d\.]+)|poller=(\w+)|name=([\w\.]+)|enabled=(True|False)'
    reValidator = re.compile(validInput)
    validatedInput = reValidator.match(data)

    if validatedInput is None:
        errorMsg = 'Error - Parameter format must be:\n'
        errorMsg += '\tpython SubfragiumCli.py list oids target={name|ip}|oid=<oid>,|poller={poller}|name={name}|enabled={True|False}\n'
        errorMsg += '\n'
        errorMsg += '\te.g.\n'
        errorMsg += '\tpython SubfragiumCli.py list oids target=host.test.com,oid=1.3.6.1.2.1,poller=poller1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0,enabled=True\n'
        errorMsg += '\tpython SubfragiumCli.py list oids target=123.123.1.10,oid=1.3.6.1.2.1,poller=poller1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0,enabled=True\n'
        return {'success': True, 'err': errorMsg}

    apiCall = apiEndPoint['urls']['oids']

    if validatedInput.group(0) != 'all':

        (field, value) = validatedInput.group(0).split('=')
        apiCall += '?%s=%s' % (field, value)

    r = requests.get(apiCall)
    return validateResponse(r, True)


def listTypeOid(data, apiEndPoint):

    if data == 'help':
        helpMsg = 'Parameter format must be:\n'
        helpMsg += '\tpython SubfragiumCli.py list oid target={name|ip},oid=<oid>\n'
        helpMsg += '\n'
        helpMsg += '\te.g.\n'
        helpMsg += '\tpython SubfragiumCli.py list oid target=host.test.com,oid=1.3.6.1.2.1\n'
        helpMsg += '\tpython SubfragiumCli.py list oid target=123.123.1.10,oid=1.3.6.1.2.1\n'
        return {'success': True, 'helpMsg': helpMsg}

    validInput = 'target=([\w\.]+)\,oid=([\d\.]+)'
    reValidator = re.compile(validInput)
    validatedInput = reValidator.match(data)
    if validatedInput is None:
        errorMsg = 'Error - Parameter format must be:\n'
        errorMsg += '\tpython SubfragiumCli.py list oid target={name|ip},oid=<oid>\n'
        errorMsg += '\n'
        errorMsg += '\te.g.\n'
        errorMsg += '\tpython SubfragiumCli.py list oid target=host.test.com,oid=1.3.6.1.2.1\n'
        errorMsg += '\tpython SubfragiumCli.py list oid target=123.123.1.10,oid=1.3.6.1.2.1\n'
        return {'success': False, 'err': errorMsg}

    apiCall = apiEndPoint['urls']['oid'].replace('<string:tgt>', validatedInput.group(1))
    apiCall = apiCall.replace('<string:oidInfo>', validatedInput.group(2))
    r = requests.get(apiCall)
    return validateResponse(r, True)


def deleteTypeOid(data, apiEndPoint):

    if data == 'help':
        helpMsg = 'Parameter format must be:\n'
        helpMsg += '\tpython SubfragiumCli.py delete oid target={name|ip},oid=<oid>\n'
        helpMsg += '\n'
        helpMsg += '\te.g.\n'
        helpMsg += '\tpython SubfragiumCli.py delete oid target=host.test.com,oid=1.3.6.1.2.1\n'
        helpMsg += '\tpython SubfragiumCli.py delete oid target=123.123.1.10,oid=1.3.6.1.2.1\n'
        return {'success': True, 'helpMsg': helpMsg}

    validInput = 'target=([\w\.]+)\,oid=([\d\.]+)'
    reValidator = re.compile(validInput)
    validatedInput = reValidator.match(data)
    if validatedInput is None:
        errorMsg = 'Error - Parameter format must be:\n'
        errorMsg += '\tpython SubfragiumCli.py delete oid target={name|ip},oid=<oid>\n'
        errorMsg += '\n'
        errorMsg += '\te.g.\n'
        errorMsg += '\tpython SubfragiumCli.py delete oid target=host.test.com,oid=1.3.6.1.2.1\n'
        errorMsg += '\tpython SubfragiumCli.py delete oid target=123.123.1.10,oid=1.3.6.1.2.1\n'
        return {'success': False, 'err': errorMsg}

    apiCall = apiEndPoint['urls']['oid'].replace('<string:tgt>', validatedInput.group(1))
    apiCall = apiCall.replace('<string:oidInfo>', validatedInput.group(2))
    r = requests.delete(apiCall)
    return validateResponse(r, False)
