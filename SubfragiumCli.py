import argparse
import json
import requests
import re
import SubfragiumClientLib
import SubfragiumUtilsLib

#apiServer = 'localhost:5000'


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
        if data == 'help':
            print results['helpMsg']
            exit(0)
        if results['success']:
            printTarget(results['obj'])
            exit(0)
        else:
            print 'ERROR - %s' % results['err']
            exit(1)
    elif type == 'targets':
        results = SubfragiumClientLib.listTypeTargets(data, apiEndPoint)
        if data == 'help':
            print results['helpMsg']
            exit(0)
        if results['success']:
            printTargets(results['obj'])
            exit(0)
        else:
            print 'ERROR - %s' % results['err']
            exit(1)
    elif type == 'poller':
        results = SubfragiumClientLib.listTypePoller(data, apiEndPoint)
        if data == 'help':
            print results['helpMsg']
            exit(0)
        if results['success']:
            printPoller(results['obj'])
            exit(0)
        else:
            print 'ERROR - %s' % results['err']
            exit(1)
    elif type == 'pollers':
        results = SubfragiumClientLib.listTypePollers(data, apiEndPoint)
        if data == 'help':
            print results['helpMsg']
            exit(0)
        if results['success']:
            printPollers(results['obj'])
            exit(0)
        else:
            print 'ERROR - %s' % results['err']
            exit(1)
    elif type == 'oid':
        results = SubfragiumClientLib.listTypeOid(data, apiEndPoint)
        if data == 'help':
            print results['helpMsg']
            exit(0)
        if results['success']:
            printOid(results['obj'])
            exit(0)
        else:
            print 'ERROR - %s' % results['err']
            exit(1)
    elif type == 'oids':
        results = SubfragiumClientLib.listTypeOids(data, apiEndPoint)
        if data == 'help':
            print results['helpMsg']
            exit(0)
        if results['success']:
            printOids(results['obj'])
            exit(0)
        else:
            print 'ERROR - %s' % results['err']
            exit(1)
    else:
        print 'Bad type input: %s' % type
        exit(1)


def actionDelete(type, data, apiEndPoint):
    if type == 'target':
        results = SubfragiumClientLib.deleteTypeTarget(data, apiEndPoint)
    elif type == 'poller':
        results = SubfragiumClientLib.deleteTypePoller(data, apiEndPoint)
    elif type == 'oid':
        results = SubfragiumClientLib.deleteTypeOid(data, apiEndPoint)
    else:
        return {'success': False, 'err': 'Bad type input: %s' % type}

    return results


def actionModify(type, data, apiEndPoint):
    if type == 'target':
        results = SubfragiumClientLib.modifyTypeTarget(data, apiEndPoint)
    elif type == 'poller':
        results = SubfragiumClientLib.modifyTypePoller(data, apiEndPoint)
    elif type == 'oid':
        results = SubfragiumClientLib.modifyTypeOid(data, apiEndPoint)
    else:
        return {'success': False, 'err': 'Unsupported modification of type %s' % type}

    return results

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    actions = ['add', 'list', 'delete', 'modify']
    types = ['target', 'targets', 'poller', 'pollers', 'oid', 'oids']

    parser.add_argument('controller', action='store', nargs=1, help='Define controller')
    parser.add_argument('action', action='store', nargs=1, choices=actions, help='Action to take on controller')
    parser.add_argument('type', action='store', nargs=1, choices=types, help='Type of item to apply action to')
    parser.add_argument('parameters', action='store', default='', help='Parameters for item e.g. help')

    args = parser.parse_args()

    apiEndpoint = SubfragiumClientLib.getApiEndPoint(args.controller[0])
    if not apiEndpoint['success']:
        print 'Error: %s' % apiEndpoint['err']
        exit(1)

    if args.action[0] == 'add':
        results = actionAdd(args.type[0], args.parameters, apiEndpoint)
        if results['success']:
            if args.parameters == 'help':
                print results[ 'helpMsg' ]
                exit(0)
            else:
                print 'OK'
                exit(0)
        else:
            print 'ERROR'
            print  results['err']
            exit(1)

    elif args.action[0] == 'list':
        results = actionList(args.type[0], args.parameters, apiEndpoint)
        # Variable types of data so handled in specific functions above

    elif args.action[0] == 'delete':
        results = actionDelete(args.type[0], args.parameters, apiEndpoint)
        if results['success']:
            if args.parameters == 'help':
                print results[ 'helpMsg' ]
                exit(0)
            else:
                print 'OK'
                exit(0)
        else:
            print 'ERROR'
            print results['err']
            exit(1)

    elif args.action[0] == 'modify':
        results = actionModify(args.type[0], args.parameters, apiEndpoint)
        if results['success']:
            if args.parameters == 'help':
                print results[ 'helpMsg' ]
                exit(0)
            else:
                print 'OK'
                exit(0)
        else:
            print 'ERROR'
            print results['err']
            exit(1)
    else:
        print 'Bad action input'
        exit(1)