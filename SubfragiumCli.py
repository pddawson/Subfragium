import argparse
import json
import requests
import re
import SubfragiumClientLib
import SubfragiumUtilsLib

apiServer = 'localhost:5000'

# SubfragiumCli.py add target ip,name,snmpstring
# SubfragiumCli.py <action> <type> <data>


def actionAdd(type, data, apiEndPoint):
    if type == 'target':
        results = SubfragiumClientLib.addTypeTarget(data, apiEndPoint)
    elif type == 'poller':
        results = SubfragiumClientLib.addTypePoller(data, apiEndPoint)
    elif type == 'oid':
        results = SubfragiumClientLib.addTypeOid(data, apiEndpoint)
    else:
        return {'success': False, 'err': 'Bad type input: %s' % type}

    return results

def printTargets(targets):

    print 'Name'
    print '----'
    for target in targets:
        print target['name']

def printTarget(target):

    print 'Name: %s' % (target['name'])
    print 'SnmpString: %s' % (target['snmpString'])
    print 'Timeout (msec): %s' % (target['timeout'])

def printPollers(pollers):

    print 'name\t\tDisabled'
    print '----\t\t--------'
    for poller in pollers:
        print '%s\t\t%s' % (poller['name'], poller['disabled'])

def printPoller(poller):
    print 'Name: %s' % (poller[ 'name' ])
    print 'Disabled: %s' % (poller[ 'disabled' ])
    print 'Min Num Processes: %s' % (poller[ 'minProcesses' ])
    print 'Max Num Processes: %s' % (poller[ 'maxProcesses' ])
    print 'Start Num Processes: %s' % (poller[ 'numProcesses' ])
    print 'Num Process Hold Time (sec): %s' % (poller[ 'holdDown' ])
    print 'Poller Cycle Time (sec): %s' % (poller[ 'cycleTime' ])
    print 'Data Storage Type: %s' % (poller[ 'storageType' ])
    print 'Data Storage Location: %s' % (poller[ 'storageLocation' ])
    print 'Error Threshold: %s' % (poller[ 'errorThreshold' ])
    print 'Error Hold Time (sec): %s' % (poller[ 'errorHoldTime' ])

def printOids(oids):

    print 'ID\t\t\t\t\tName'
    print '--\t\t\t\t\t----'
    for oid in oids:
        print '%s\t%s' % (oid['id'], oid['name'])

def printOid(oid):

    print 'Name: %s' % oid['name']
    print 'Target: %s' % oid['target']
    print 'OID: %s' % oid['oid']
    print 'ID: %s' % oid['id']
    print 'Enabled: %s' % oid['enabled']
    print 'Poller: %s' % oid['poller']
    print 'SnmpString: %s' % oid['snmpString']
    #print 'Timeout: %s' % oid['timeout']

def actionList(type, data, apiEndPoint):

    if type == 'target':
        results = SubfragiumClientLib.listTypeTarget(data, apiEndPoint)
        if results['success']:
            printTarget(results['obj'])
            exit(0)
        else:
            print 'ERROR - %s' % results['err']
            exit(1)
    elif type == 'targets':
        results = SubfragiumClientLib.listTypeTargets(data, apiEndPoint)
        if results['success']:
            printTargets(results['obj'])
            exit(0)
        else:
            print 'ERROR - %s' % results['err']
            exit(1)
    elif type == 'poller':
        results = SubfragiumClientLib.listTypePoller(data, apiEndPoint)
        if results['success']:
            printPoller(results['obj'])
            exit(0)
        else:
            print 'ERROR - %s' % results['err']
            exit(1)
    elif type == 'pollers':
        results = SubfragiumClientLib.listTypePollers(data, apiEndPoint)
        if results['success']:
            printPollers(results['obj'])
            exit(0)
        else:
            print 'ERROR - %s' % results['err']
            exit(1)
    elif type == 'oid':
        results = SubfragiumClientLib.listTypeOid(data, apiEndPoint)
        if results['success']:
            printOid(results['obj'])
            exit(0)
        else:
            print 'ERROR - %s' % results['err']
            exit(1)
    elif type == 'oids':
        results = SubfragiumClientLib.listTypeOids(data, apiEndPoint)
        if results['success']:
            printOids(results['obj'])
            exit(0)
        else:
            print 'ERROR - %s' % results['err']
            exit(1)
    else:
        print 'Bad type input: %s' % type


def actionDelete(type, data, apiEndPoint):
    if type == 'target':
        results = SubfragiumClientLib.deleteTypeTarget(data, apiEndPoint)
    elif type == 'poller':
        results = SubfragiumClientLib.deleteTypePoller(data, apiEndPoint)
    elif type == 'oid':
        SubfragiumClientLib.deleteTypeOid(data, apiEndPoint)
    else:
        return {'success': False, 'err': 'Bad type input: %s' % type}

    return results


def actionModify(type, data, apiEndPoint):
    if type == 'target':
        SubfragiumClientLib.modifyTypeTarget(data, apiEndPoint)
    elif type == 'poller':
        SubfragiumClientLib.modifyTypePoller(data, apiEndPoint)
    elif type == 'oid':
        SubfragiumClientLib.modifyTypeOid(data, apiEndPoint)
    else:
        print 'Unsupported modification of type %s' % type

if __name__ == '__main__':

    apiEndpoint = SubfragiumClientLib.getApiEndPoint(apiServer)
    if not apiEndpoint['success']:
        print 'Error: Can not get API endpoints from server'
        exit(1)

    parser = argparse.ArgumentParser()

    actions = ['add', 'list', 'delete', 'modify']
    types = ['target', 'targets', 'poller', 'pollers', 'oid', 'oids']

    parser.add_argument('action', action='store', nargs=1, choices=actions, help='Action to take on controller')
    parser.add_argument('type', action='store', nargs=1, choices=types, help='Type of item to apply action to')
    parser.add_argument('parameters', action='store', default='', help='Parameters for item e.g. help')

    args = parser.parse_args()

    if args.action[0] == 'add':
        results = actionAdd(args.type[0], args.parameters, apiEndpoint)
        if args.parameters == 'help':
            print results['help']
            exit(0)
        if results['success']:
            print 'OK'
            exit(0)
        else:
            print 'ERROR'
            print  results['err']
            exit(1)

    elif args.action[0] == 'list':
        actionList(args.type[0], args.parameters, apiEndpoint)

    elif args.action[0] == 'delete':
        results = actionDelete(args.type[0], args.parameters, apiEndpoint)
        if results['success']:
            print 'OK'
            exit(0)
        else:
            print 'ERROR'
            print results['err']
            exit(1)

    elif args.action[0] == 'modify':
        actionModify(args.type[0], args.parameters, apiEndpoint)

    else:
        print 'Bad action input'
        exit(1)