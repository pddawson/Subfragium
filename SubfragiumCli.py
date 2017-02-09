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
        SubfragiumClientLib.addTypePoller(data, apiEndPoint)
    elif type == 'oid':
        SubfragiumClientLib.addTypeOid(data, apiEndpoint)
    else:
        return {'success': False, 'err': 'Bad type input: %s' % type}

    return results

def actionList(type, data, apiEndPoint):
    if type == 'target':
        SubfragiumClientLib.listTypeTarget(data, apiEndPoint)
    elif type == 'targets':
        SubfragiumClientLib.listTypeTargets(data, apiEndPoint)
    elif type == 'poller':
        SubfragiumClientLib.listTypePoller(data, apiEndPoint)
    elif type == 'pollers':
        SubfragiumClientLib.listTypePollers(data, apiEndPoint)
    elif type == 'oid':
        SubfragiumClientLib.listTypeOid(data, apiEndPoint)
    elif type == 'oids':
        SubfragiumClientLib.listTypeOids(data, apiEndPoint)
    else:
        print 'Bad type input: %s' % type


def actionDelete(type, data, apiEndPoint):
    if type == 'target':
        SubfragiumClientLib.deleteTypeTarget(data, apiEndPoint)
    elif type == 'poller':
        SubfragiumClientLib.deleteTypePoller(data, apiEndPoint)
    elif type == 'oid':
        SubfragiumClientLib.deleteTypeOid(data, apiEndPoint)
    else:
        print 'Bad type input: %s' % type


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
        actionDelete(args.type[0], args.parameters, apiEndpoint)

    elif args.action[0] == 'modify':
        actionModify(args.type[0], args.parameters, apiEndpoint)

    else:
        print 'Bad action input'
        exit(1)