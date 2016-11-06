import argparse
import SubfragiumUtils
import json
import requests
import re

apiServer = 'localhost:5000'

# SubfragiumCli.py add target ip,name,snmpstring
# SubfragiumCli.py <action> <type> <data>


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
    apiCall = apiEndpoint['urls']['target'].replace('<string:name>','')
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

    validInput = 'name=([\w\.]+)\,minProcesses=(\d+)\,maxProcesses=(\d+)\,numProcesses=(\d+)\,holdDown=(\d+)'
    reValidator = re.compile(validInput)
    validatedInput = reValidator.match(data)
    if validatedInput == None:
        print 'Error: Format must be --data name=<name>,minProcesses=<num>,maxProcesses=<num>,numProcesses=<num>,holdDown=<num>'
        print 'e.g. --data name=poller1,minProcesses=1,maxProcesses=50,numProcesses=2,holdTime=20'
        exit(1)

    payload = {
        'minProcesses': validatedInput.group(2),
        'maxProcesses': validatedInput.group(3),
        'numProcesses': validatedInput.group(4),
        'holdDown': validatedInput.group(5)
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

    apiCall = apiEndpoint['urls']['pollers']
    r = requests.get(apiCall)
    rJson = json.loads(r.text)
    if 'response' in rJson:
        if 'success' in rJson['response'] and rJson['response']['success']:
            print 'name,minProcesses,maxProcesses,numProcesses,holdDown'
            for poller in rJson['response']['obj']:
                print '%s,%s,%s,%s,%s' % (poller['name'],
                                          poller['minProcesses'],
                                          poller['maxProcesses'],
                                          poller['numProcesses'],
                                          poller['holdDown'])

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
            print '%s,%s,%s,%s,%s' % (res['name'],
                                      res['minProcesses'],
                                      res['maxProcesses'],
                                      res['numProcesses'],
                                      res['holdDown'])
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

    validInput = 'name=([\w\.]+)(\,minProcesses=(\d+))*(\,maxProcesses=(\d+))*(\,numProcesses=(\d+))*(\,holdDown=(\d+))*'
    reValidator = re.compile(validInput)
    validatedInput = reValidator.match(data)
    if validatedInput == None:
        print 'Error: Format must be --data name=<name>,minProcesses=<num>,maxProcesses=<num>,numProcesses=<num>,holdDown=<num>'
        print 'e.g. --data name=poller1,minProcesses=1,maxProcesses=50,numProcesses=2,holdTime=20'
        exit(1)

    apiCall = apiEndpoint['urls']['poller'].replace('<string:name>', '')
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

    if validatedInput.group(3) != None:
        modifiedPoller['minProcesses'] = validatedInput.group(3)
    if validatedInput.group(5) != None:
        modifiedPoller['maxProcesses'] = validatedInput.group(5)
    if validatedInput.group(7) != None:
        modifiedPoller['numProcesses'] = validatedInput.group(7)
    if validatedInput.group(9) != None:
        modifiedPoller['holdDown'] = validatedInput.group(9)

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

    validInput = 'target=([\w\.]+)\,oid=([\d\.]+)\,poller=(\w+)\,name=(\w+)'
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

    validInput = 'target=([\w\.]+)(\,oid=([\d\.]+))(\,poller=(\w+))*(\,name=(\w+))*'
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

    modifiedOid = rJson['response']['obj']

    if validatedInput.group(5) != None:
        modifiedOid['poller'] = validatedInput.group(5)
    if validatedInput.group(7) != None:
        modifiedOid['name#'] = validatedInput.group(7)

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

    apiCall = apiEndpoint['urls']['oids']
    r = requests.get(apiCall)
    rJson = json.loads(r.text)
    if 'response' in rJson:
        if 'success' in rJson['response'] and rJson['response']['success']:
            print 'id,name,oid,target,poller'
            for oid in rJson['response']['obj']:
                print '%s,%s,%s,%s,%s' % (oid['id'],
                                          oid['name'],
                                          oid['oid'],
                                          oid['target'],
                                          oid['poller'])

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


def actionAdd(type, data, apiEndPoint):
    if type == 'target':
        addTypeTarget(data, apiEndPoint)
    elif type == 'poller':
        addTypePoller(data, apiEndPoint)
    elif type == 'oid':
        addTypeOid(data, apiEndpoint)
    else:
        print 'Bad type input: %s' % type

def actionList(type, data, apiEndPoint):
    if type == 'target':
        listTypeTarget(data, apiEndPoint)
    elif type == 'targets':
        listTypeTargets(apiEndPoint)
    elif type == 'poller':
        listTypePoller(data, apiEndPoint)
    elif type == 'pollers':
        listTypePollers(apiEndPoint)
    elif type == 'oid':
        listTypeOid(data, apiEndPoint)
    elif type == 'oids':
        listTypeOids(apiEndPoint)
    else:
        print 'Bad type input: %s' % type


def actionDelete(type, data, apiEndPoint):
    if type == 'target':
        deleteTypeTarget(data, apiEndPoint)
    elif type == 'poller':
        deleteTypePoller(data, apiEndPoint)
    elif type == 'oid':
        deleteTypeOid(data, apiEndPoint)
    else:
        print 'Bad type input: %s' % type


def actionModify(type, data, apiEndPoint):
    if type == 'target':
        modifyTypeTarget(data, apiEndPoint)
    elif type == 'poller':
        modifyTypePoller(data, apiEndPoint)
    elif type == 'oid':
        modifyTypeOid(data, apiEndPoint)
    else:
        print 'Unsupported modification of type %s' % type

if __name__ == '__main__':

    apiEndpoint = SubfragiumUtils.getApiEndPoint(apiServer)
    if not apiEndpoint['success']:
        print 'Error: Can not get API endpoints from server'
        exit(1)

    parser = argparse.ArgumentParser('CLI Utility to manipulate the PingListServer')

    actions = ['add', 'list', 'delete', 'modify']
    types = ['target', 'targets', 'poller', 'pollers', 'oid', 'oids']

    parser.add_argument('action', action='store', nargs=1, choices=actions, help='Action to take')
    parser.add_argument('type', action='store', nargs=1, choices=types, help='Type of item')
    parser.add_argument('--data', action='store', default='', help='Data to add')

    args = parser.parse_args()

    if args.action[0] == 'add':
        actionAdd(args.type[0], args.data, apiEndpoint)

    elif args.action[0] == 'list':
        actionList(args.type[0], args.data, apiEndpoint)

    elif args.action[0] == 'delete':
        actionDelete(args.type[0], args.data, apiEndpoint)

    elif args.action[0] == 'modify':
        actionModify(args.type[0], args.data, apiEndpoint)

    else:
        print 'Bad action input'
        exit(1)