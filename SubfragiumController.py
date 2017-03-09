from app import db
import app
import SubfragiumDBLib
import SubfragiumUtilsLib
from flask import jsonify
from flask import request
import werkzeug
import SubfragiumControllerSchema

app = app.create_app()
db.init_app(app)


@app.before_request
def initDb():
    db.create_all()


@app.errorhandler(werkzeug.exceptions.MethodNotAllowed)
def badMethod(msg):
    response = jsonify(response={'success': False, 'err': 'Unsupported Method: %s' % msg})
    response.status_code = 405
    return response


@app.errorhandler(404)
def error404(msg):
    response = jsonify(response={'success': False, 'err': str(msg)})
    response.status_code = 404
    return response


@app.errorhandler(503)
def error503(msg):
    resp = jsonify(response={'success': False, 'err': str(msg)})
    resp.status_code = 503
    return resp


def getTarget(name):

    app.logger.info('getTarget() %s request from %s' % (name, request.remote_addr))

    tgt = SubfragiumDBLib.getTargetByName({'name': name})
    if not tgt['success']:
        app.logger.error('getTarget() - Failed: %s' % tgt['err'])
        return {'success': False, 'code': 503, 'err': 'getTarget() - Failed: %s' % tgt['err']}

    if not tgt['obj']:
        app.logger.info('getTarget() - No target %s found in DB' % name)
        return {'success': False, 'code': 404, 'err': 'No target %s found in DB' % name}

    return {'success': True, 'code': 200, 'obj': tgt['obj'][0]}


def putTarget(name, data):

    app.logger.info('putTarget() %s request from %s' % (name, request.remote_addr))

    if data is None:
        app.logger.info('putTarget() - No JSON provided')
        return {'success': False, 'code': 404, 'err': 'putTarget() - No JSON provided'}

    results = SubfragiumUtilsLib.validateJson(SubfragiumControllerSchema.PingTarget, data)
    if not results['success']:
        app.logger.error('putTarget() - Failed : %s' % results['err'])
        return {'success': False, 'code': 404, 'err': results['err']}

    # Check if the target is already defined
    existingTarget = SubfragiumDBLib.getTargetByName({'name': name})
    if not existingTarget['success']:
        app.logger.error('putTarget() - Failed : %s' % existingTarget['err'])
        return {'success': False, 'code': 503, 'err': 'putTarget() Failure: %s' % existingTarget['err']}

    if existingTarget['obj']:
        app.logger.info('putTarget() %s update' % name)
        result = SubfragiumDBLib.updateTargetByName({'name': name,
                                                     'snmpString': data['snmpString'],
                                                     'timeout': data['timeout']})
        if not result['success']:
            return {'success': False, 'code': 503, 'err': 'putTarget() - Failed: %s' % result['err']}
        else:
            return {'success': True, 'code': 200}

    results = SubfragiumDBLib.putTargetByName({'name': name,
                                               'snmpString': data['snmpString'],
                                               'timeout': data['timeout']})
    if not results['success']:
        app.logger.error('putTarget() - Failed : %s' % results['err'])
        return {'success': False, 'code': 503, 'err': 'putTarget() Failed: %s ' % results['err']}

    return {'success': True, 'code': 200}


def deleteTarget(name):

    app.logger.info('deleteTarget() %s request from %s' % (name, request.remote_addr))

    existingTarget = SubfragiumDBLib.getTargetByName({'name': name})
    if not existingTarget['success']:
        app.logger.error('deleteTarget() - Failed : %s' % existingTarget['err'])
        return {'success': False, 'code': 503, 'err': 'deleteTarget() Failed: %s' % existingTarget['err']}

    if not existingTarget['obj']:
        app.logger.info('deleteTarget() - Target %s not found' % name)
        return {'success': False, 'code': 404, 'err': 'Target %s not found' % name}

    existingOids = SubfragiumDBLib.getOidsByTarget({'target': name})
    if not existingOids['success']:
        app.logger.error('deleteTarget() - Failed : %s' % existingOids['err'])
        return {'success': False, 'code': 503, 'err': 'deleteTarget() Failed: %s' % existingOids['err']}

    if len(existingOids['obj']) > 0:
        app.logger.info('deleteTarget() - Target %s in use for oids' % name)
        return {'success': False, 'code': 404, 'err': 'deleteTarget() Failed: Target %s in use for oids' % name}

    result = SubfragiumDBLib.deleteTargetByName({'name': name})
    if not result['success']:
        app.logger.error('deleteTarget() Failed: %s' % result['err'])
        return{'success': False, 'code': 503, 'err': 'deleteTarget() Failed: %s' % result['err']}

    return {'success': True, 'code': 200}


@app.route('/target/<string:name>', methods=['GET', 'PUT', 'DELETE'])
def target(name):

    result = SubfragiumUtilsLib.validateTargetName(name)
    if not result['success']:
        return error404(result['err'])

    if request.method == 'GET':
        result = getTarget(name)
        if result['success']:
            return jsonify(response={'success': True, 'obj': result['obj']})
        else:
            if result['code'] == 404:
                return error404(result['err'])
            else:
                return error503(result['err'])

    elif request.method == 'PUT':
        result = putTarget(name, request.json)
        if result['success']:
            return jsonify(response={'success': True})
        else:
            if result['code'] == 404:
                return error404(result['err'])
            else:
                return error503(result['err'])

    elif request.method == 'DELETE':
        result = deleteTarget(name)
        if result['success']:
            return jsonify(response={'success': True})
        else:
            if result['code'] == 404:
                return error404(result['err'])
            else:
                return error503(result['err'])
    else:
        app.logger.info('Unsupported HTTP method in request')
        return error404('Unsupported HTTP method')


@app.route('/targets', methods=['GET'])
def targets():

    app.logger.info('getAllTargets() request from %s' % request.remote_addr)

    targetList = SubfragiumDBLib.getTargetsAll()
    if not targetList['success']:
        error = 'getTargetsAll() - Failed: %s' % targetList['err']
        app.logger.error('getTargetsAll() - Failed %s' % targetList['err'])
        return error503(error)

    return jsonify(response={'success': True, 'obj': targetList['obj']})


def putPoller(name, data):

    app.logger.info('putPoller() %s request from %s' % (name, request.remote_addr))

    results = SubfragiumUtilsLib.validateJson(SubfragiumControllerSchema.Poller, data)
    if not results['success']:
        app.logger.info('putPoller() - Failure: %s' % results['err'])
        return {'success': False, 'code': 404, 'err': 'putPoller() - Failure: %s' % results['err']}

    # Check that the maxProcesses is greater than the minProcesses
    if data['maxProcesses'] < data['minProcesses']:
        return {'success': False, 'code': 404, 'err': 'putPoller() - minProcesses must be less than maxProcesses'}

    # Check that the numProcesses is not less than the minProcesses
    if data['numProcesses'] < data['minProcesses']:
        return {'success': False, 'code': 404, 'err': 'putPoller() - numProcesses must be greater than minProcesses'}

    # Check that the numProcesses is not greater than the maxProcesses
    if data['numProcesses'] > data['maxProcesses']:
        return {'success': False, 'code': 404, 'err': 'putPoller() - numProcesses must be less than maxProcesses'}

    existingPoller = SubfragiumDBLib.getPollerByName({'name': name})
    if not existingPoller['success']:
        app.logger.error('putPoller() - Failure:  %s' % existingPoller['err'])
        return {'success': False, 'code': 503, 'err': 'putPoller() - Failure: %s' % existingPoller['err']}

    if existingPoller['obj']:
        app.logger.info('putPoller() %s update' % name)
        data['name'] = name
        print data
        result = SubfragiumDBLib.modifyPollerByName(data)
        if not result['success']:
            return {'success': False, 'code': 503, 'err': 'putPoller() - Failed: %s' % result['err']}
        else:
            return {'success': True, 'code': 200}

    data['name'] = name
    results = SubfragiumDBLib.putPollerByName(data)
    if not results['success']:
        app.logger.error('putPoller() - Failed %s' % results['err'])
        return {'success': False, 'code': 503, 'err': 'putPoller() Failed: %s' % results['err']}

    return {'success': True, 'code': 200}


def getPoller(name):

    app.logger.info('getPoller() %s request from %s' % (name, request.remote_addr))

    existingPoller = SubfragiumDBLib.getPollerByName({'name': name})
    if not existingPoller['success']:
        app.logger.error('getPoller() - Failed %s' % existingPoller['err'])
        return {'success': False, 'code': 503, 'err': 'getPoller() - Failed: %s' % existingPoller['err']}

    if not existingPoller['obj']:
        app.logger.info('getPoller() - No poller %s found in DB' % name)
        return {'success': False, 'code': 404, 'err': 'No poller %s found in DB' % name}

    return {'success': True, 'code': 200, 'obj': existingPoller['obj'][0]}


def deletePoller(name):

    app.logger.info('deletePoller() %s request from %s' % (name, request.remote_addr))

    existingPoller = SubfragiumDBLib.getPollerByName({'name': name})
    if not existingPoller['success']:
        app.logger.error('deletePoller() - Failed %s' % existingPoller['err'])
        return {'success': False, 'code': 503, 'err': 'deletePoller() Failed: %s' % existingPoller['err']}

    if not existingPoller['obj']:
        app.logger.info('deletePoller() - Poller %s not found' % name)
        return {'success': False, 'code': 404, 'err': 'Poller %s not found' % name}

    existingOids = SubfragiumDBLib.getOidsByPoller({'poller': name})
    if not existingOids['success']:
        app.logger.error('deletePoller() - Failed %s' % existingOids['err'])
        return {'success': False, 'code': 503, 'err': 'deletePoller() Failed: %s' % existingOids['err']}

    if len(existingOids['obj']) > 0:
        app.logger.info('deletePoller() - Poller %s in use for oids' % name)
        return {'success': False, 'code': 404, 'err': 'Poller %s in use for oids' % name}

    result = SubfragiumDBLib.deletePollerByName({'name': name})
    if not result['success']:
        app.logger.error('deletePoller() Failed: %s' % result['err'])
        return {'success': False, 'code': 503, 'err': 'deletePoller() Failed: %s' % result['err']}

    return {'success': True, 'code': 200}


@app.route('/poller/<string:name>', methods=['GET', 'PUT', 'DELETE'])
def poller(name):

    if request.method == 'GET':
        result = getPoller(name)
        if result['success']:
            return jsonify(response={'success': True, 'obj': result['obj']})
        else:
            if result['code'] == 404:
                return error404(result['err'])
            else:
                return error503(result['err'])

    elif request.method == 'PUT':

        result = putPoller(name, request.json)
        if result['success']:
            return jsonify(response={'success': True})
        else:
            if result['code'] == 404:
                return error404(result['err'])
            else:
                return error503(result['err'])

    elif request.method == 'DELETE':
        result = deletePoller(name)
        if result['success']:
            return jsonify(response={'success': True})
        else:
            if result['code'] == 404:
                return error404(result['err'])
            else:
                return error503(result['err'])

    else:
        app.logger.info('Unsupported HTTP method in request')
        return error404('Unsupported HTTP method')


@app.route('/pollers', methods=['GET'])
def pollers():

    app.logger.info('getPollersAll() request from %s' % request.remote_addr)

    pollerList = SubfragiumDBLib.getPollersAll()
    if not pollerList['success']:
        app.logger.error('getPollersAll() Failed: %s' % pollerList['err'])
        error = 'getPollersAll() Failed: %s' % pollerList['err']
        return error503(error)

    return jsonify(response={'success': True, 'obj': pollerList['obj']})


def putOid(tgt, oidInfo, data):

    app.logger.info('putOid() %s:%s request from %s' % (tgt, oidInfo, request.remote_addr))

    results = SubfragiumUtilsLib.validateJson(SubfragiumControllerSchema.Oid, data)
    if not results['success']:
        app.logger.error('putOid() Failed: %s' % results['err'])
        return {'success': False, 'code': 404, 'err': results['err']}

    # Check for existence of poller
    resPoller = SubfragiumDBLib.getPollerByName({'name': data['poller']})
    if not resPoller['success']:
        app.logger.error('putOid() Failure: %s ' % resPoller['err'])
        return {'success': False, 'code': 503, 'err': 'putOid() Failure: %s' % resPoller['err']}

    if not resPoller['obj']:
        app.logger.info('putOid() - Poller %s does not exist' % data['poller'])
        return {'success': False, 'code': 404, 'err': 'Poller %s does not exist' % data['poller']}

    # Check the poller isn't disabled
    if resPoller['obj'][0]['disabled']:
        return {'success': False, 'code': 404, 'err': 'Poller %s is disabled' % data['poller']}

    # Check for existence of - Separate SubfragiumCli into a CLI tool and a SubfragiumClientLib.pytarget
    resTarget = SubfragiumDBLib.getTargetByName({'name': tgt})
    if not resTarget['success']:
        app.logger.error('putOid() Failure: %s ' % resTarget['err'])
        return {'success': False, 'code': 503, 'err': 'putOid() Failure: %s' % resTarget['err']}

    if not resTarget['obj']:
        app.logger.info('putOid() - Target %s does not exist' % target)
        return {'success': False, 'code': 404, 'err': 'Target %s does not exist' % tgt}

    data['target'] = tgt
    data['oid'] = oidInfo

    # Check for existence of oid
    existingOid = SubfragiumDBLib.getOidByOid({'target': tgt, 'oid': oidInfo})
    if not existingOid['success']:
        app.logger.error('putOid() Failure: %s ' % existingOid['err'])
        return {'success': False, 'code': 503, 'err': 'putOid() Failure: %s' % existingOid['err']}

    if not existingOid['obj'] == []:
        app.logger.info('putOid() %s:%s update' % (tgt, oidInfo))
        result = SubfragiumDBLib.modifyOidByOid(data)
        if not result['success']:
            return {'success': False, 'code': 503, 'err': 'putOid() - Failed: %s' % result['err']}
        else:
            return {'success': True, 'code': 200}

    results = SubfragiumDBLib.putOidByOid(data)
    if not results['success']:
        app.logger.error('addOid() Failure: %s ' % results['err'])
        return {'success': False, 'code': 503, 'err': 'putPoller() Failed: %s' % results['err']}

    return {'success': True, 'code': 200}


def deleteOid(tgt, oidInfo):

    app.logger.info('deleteOid() %s:%s request from %s' % (tgt, oidInfo, request.remote_addr))

    existingOid = SubfragiumDBLib.getOidByOid({'target': tgt, 'oid': oidInfo})
    if not existingOid['success']:
        app.logger.error('deleteOid() Failure: %s ' % existingOid['err'])
        return {'success': False, 'code': 503, 'err': 'deleteOid() Failure: %s' % existingOid['err']}

    if len(existingOid['obj']) == 0:
        app.logger.info('deleteOid() - No such OID %s:%s' % (tgt, oidInfo))
        return {'success': False, 'code': 404, 'err': 'deleteOid() - No such OID %s:%s' % (tgt, oidInfo)}

    results = SubfragiumDBLib.deleteOidByOid({'target': tgt, 'oid': oidInfo})
    if not results['success']:
        app.logger.error('deleteOid() Failure: %s ' % results['err'])
        return {'success': False, 'code': 503, 'err': 'deleteOid() Failed: %s' % results['err']}

    return {'success': True, 'code': 200}


def getOid(tgt, oidInfo):

    app.logger.info('getOid() %s:%s request from %s' % (tgt, oidInfo, request.remote_addr))

    existingOid = SubfragiumDBLib.getOidByOid({'target': tgt, 'oid': oidInfo})
    if not existingOid['success']:
        app.logger.error('getOid() Failure: %s ' % existingOid['err'])
        return {'success': False, 'code': 503, 'err': 'getOid() Failure: %s' % existingOid['err']}

    if len(existingOid['obj']) == 0:
        app.logger.info('deleteOid() - No such OID %s:%s' % (target, oidInfo))
        return {'success': False, 'code': 404, 'err': 'getOid() - No such OID %s:%s' % (tgt, oidInfo)}

    return {'success': True, 'code': 200, 'obj': existingOid['obj'][0]}


@app.route('/oid/<string:tgt>/<string:oidInfo>', methods=['GET', 'PUT', 'DELETE'])
def oid(tgt, oidInfo):

    if request.method == 'GET':
        result = getOid(tgt, oidInfo)
        if result['success']:
            return jsonify(response={'success': True, 'obj': result['obj']})
        else:
            if result['code'] == 404:
                return error404(result['err'])
            else:
                return error503(result['err'])

    elif request.method == 'PUT':
        result = putOid(tgt, oidInfo, request.json)
        if result['success']:
            return jsonify(response={'success': True})
        else:
            if result['code'] == 404:
                return error404(result['err'])
            else:
                return error503(result['err'])

    elif request.method == 'DELETE':
        result = deleteOid(tgt, oidInfo)
        if result['success']:
            return jsonify(response={'success': True})
        else:
            if result['code'] == 404:
                return error404(result['err'])
            else:
                return error503(result['err'])

    else:
        app.logger.info('Unsupported HTTP method in request')
        return error404('Unsupported HTTP method')


@app.route('/oids', methods=['GET'])
def oids():

    if len(request.args) == 0:
        app.logger.info('getOidsQuery() request from %s' % request.remote_addr)
        oidList = SubfragiumDBLib.getOidsAll()

    else:
        queryParameters = {}

        if 'target' in request.args:
            queryParameters['target'] = '%' + request.args['target'] + '%'
        else:
            queryParameters['target'] = '%'

        if 'poller' in request.args:
            queryParameters['poller'] = '%' + request.args['poller'] + '%'
        else:
            queryParameters['poller'] = '%'

        if 'name' in request.args:
            queryParameters['name'] = '%' + request.args['name'] + '%'
        else:
            queryParameters['name'] = '%'

        if 'oid' in request.args:
            queryParameters['oid'] = '%' + request.args['oid'] + '%'
        else:
            queryParameters['oid'] = '%'

        if 'enabled' in request.args:
            if request.args['enabled'] == 'True' or request.args['enabled'] == 'true':
                queryParameters['enabled'] = True
            else:
                queryParameters['enabled'] = False
            # Otherwise leave out so we don't search on it

        app.logger.info('getOidsQuery() request from %s' % request.remote_addr)
        oidList = SubfragiumDBLib.getOidsQuery(queryParameters)

    if not oidList['success']:
        error = 'getOids..() Failed: %s' % oidList['err']
        app.logger.error(error)
        return error503(error)

    return jsonify(response={'success': True, 'obj': oidList['obj']})


@app.route('/', methods=['GET'])
def index():

    app.logger.info('getIndex() request from %s' % request.remote_addr)

    indexList = {}

    urls = app.url_map.iter_rules()
    for url in urls:
        indexList[url.endpoint] = '%s' % url

    return jsonify(response={'success': True, 'obj': indexList})

if __name__ == '__main__':

    app.logger.info('Subfragium Controller Starting')

    app.run(host='0.0.0.0', debug=True)
