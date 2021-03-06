from SubfragiumControllerApp import models
from SubfragiumControllerApp import db
import SubfragiumUtilsLib
import SubfragiumDBLibSchema

import logging


# Targets
def putTargetByName(data):

    logger = logging.getLogger('SubfragiumDBLib')

    logger.info('putTargetByName')

    result = SubfragiumUtilsLib.validateObj(SubfragiumDBLibSchema.putTargetByName, data)
    if not result['success']:
        return {'success': False, 'err': 'DBAPI putTargetByName() invalid data'}

    newTarget = models.Target(data['name'], data['snmpString'], data['timeout'])

    try:
        db.session.add(newTarget)
        db.session.commit()
        return {'success': True}
    except Exception, e:
        logger.error('ABC DBAPI putTarget() DB put operation failed %s' % e)
        return {'success': False, 'err': 'DBAPI putTarget() DB put operation failed: %s' % e}


def updateTargetByName(data):

    logger = logging.getLogger('SubfragiumDBLib')

    result = SubfragiumUtilsLib.validateObj(SubfragiumDBLibSchema.putTargetByName, data)
    if not result['success']:
        return {'success': False, 'err': 'DBAPI updateTargetByName() invalid data: %s' % result['err']}

    try:
        existingTarget = models.Target.query.filter(models.Target.name == data['name']).first()
        existingTarget.snmpString = data['snmpString']
        existingTarget.timeout = data['timeout']
        db.session.commit()
        return {'success': True}
    except Exception, e:
        logger.error('DBAPI updateTargetByName() DB put operation failed: %s' % e)
        return {'success': False, 'err': 'DBAPI updateTargetByName() DB put operation failed: %s' % e}


def deleteTargetByName(data):

    logger = logging.getLogger('SubfragiumDBLib')

    result = SubfragiumUtilsLib.validateObj(SubfragiumDBLibSchema.deleteTargetByName, data)
    if not result['success']:
        return {'success': False, 'err': 'DBAPI deleteTargetByName() invalid data: %s' % result['err']}

    try:
        existingTarget = models.Target.query.filter(models.Target.name == data['name']).first()
        db.session.delete(existingTarget)
        db.session.commit()
        return {'success': True}
    except Exception, e:
        logger.error('DBAPI deleteTargetByName() Failed: %s' % e)
        return {'success': False, 'err': 'DBAPI deleteTargetByName() Failed: %s' % e}


def getTargetByName(data):

    logger = logging.getLogger('SubfragiumDBLib')

    result = SubfragiumUtilsLib.validateObj(SubfragiumDBLibSchema.getTargetByName, data)
    if not result['success']:
        return {'success': False, 'err': 'DBAPI getTargetByName() invalid data: %s' % result['err']}

    try:
        target = models.Target.query.filter(models.Target.name == data['name']).first()
        if target is None:
            return {'success': True, 'obj': []}
        else:
            return {'success': True,
                    'obj': [
                        {'name': target.name,
                         'snmpString': target.snmpString,
                         'timeout': target.timeout}
                        ]
                    }
    except Exception, e:
        logger.error('DBAPI getTargetByName() Failed: %s' % e)
        return {'success': False, 'err': 'DBAPI getTargetByName() Failed: %s' % e}


def getTargetsAll():

    logger = logging.getLogger('SubfragiumDBLib')

    try:
        targets = models.Target.query.filter().all()
        targetList = []
        for target in targets:
            item = {'name': target.name, 'snmpString': target.snmpString, 'timeout': target.timeout}
            targetList.append(item)
        return {'success': True, 'obj': targetList}
    except Exception, e:
        logger.error('DBAPI getTargetsAll() Failed: %s' % e)
        return {'success': False, 'err': 'DBAPI getTargetsAll() Failed: %s' % e}


# Pollers
def putPollerByName(data):

    logger = logging.getLogger('SubfragiumDBLib')

    result = SubfragiumUtilsLib.validateObj(SubfragiumDBLibSchema.putPollerByName, data)
    if not result['success']:
        return {'success': False, 'err': 'DBAPI putPollerByName() invalid data: %s' % result['err']}

    newPoller = models.Poller(data)
    try:
        db.session.add(newPoller)
        db.session.commit()
        return {'success': True}
    except Exception, e:
        logger.error('DBAPI putPollerByName() DB put operation failed %s' % e)
        return {'success': False, 'err': 'DBAPI putPollerByName() DB put operation failed %s' % e}


def deletePollerByName(data):

    logger = logging.getLogger('SubfragiumDBLib')

    result = SubfragiumUtilsLib.validateObj(SubfragiumDBLibSchema.deletePollerByName, data)
    if not result['success']:
        return {'success': False, 'err': 'DBAPI deletePollerByName() invalid data: %s' % result['err']}

    try:
        poller = models.Poller.query.filter(models.Poller.name == data['name']).first()
        db.session.delete(poller)
        db.session.commit()
        return {'success': True}
    except Exception, e:
        logger.error('DBAPI deletePollerByName() Failed: %s' % e)
        return {'success': False, 'err': 'DBAPI deletePollerByName() Failed: %s' % e}


def getPollerByName(data):

    logger = logging.getLogger('SubfragiumDBLib')

    result = SubfragiumUtilsLib.validateObj(SubfragiumDBLibSchema.getPollerByName, data)
    if not result['success']:
        return {'success': False, 'err': 'DBAPI getPollerByName() invalid data: %s' % result['err']}

    try:
        poller = models.Poller.query.filter(models.Poller.name == data['name']).first()
        if poller is None:
            return {'success': True, 'obj': []}
        else:
            return {'success': True, 'obj': [{
                'name': poller.name,
                'minProcesses': poller.minProcesses,
                'maxProcesses': poller.maxProcesses,
                'numProcesses': poller.numProcesses,
                'holdDown': poller.holdDown,
                'cycleTime': poller.cycleTime,
                'storageType': poller.storageType,
                'storageLocation': poller.storageLocation,
                'disabled': poller.disabled,
                'errorThreshold': poller.errorThreshold,
                'errorHoldTime': poller.errorHoldTime}]}
    except Exception, e:
        logger.error('DBAPI getPollerByName() Failed: %s' % e)
        return {'success': False, 'err': 'DBAPI getPollerByName() Failed: %s' % e}


def modifyPollerByName(data):

    logger = logging.getLogger('SubfragiumDBLib')

    result = SubfragiumUtilsLib.validateObj(SubfragiumDBLibSchema.modifyPollerByName, data)
    if not result['success']:
        return {'success': False, 'err': 'DBAPI modifyPollerByName() invalid data: %s' % result['err']}

    try:
        existingPoller = models.Poller.query.filter(models.Poller.name == data['name']).first()
        existingPoller.minProcesses = data['minProcesses']
        existingPoller.maxProcesses = data['maxProcesses']
        existingPoller.numProcesses = data['numProcesses']
        existingPoller.holdDown = data['holdDown']
        existingPoller.cycleTime = data['cycleTime']
        existingPoller.storageType = data['storageType']
        existingPoller.storageLocation = data['storageLocation']
        existingPoller.disabled = data['disabled']
        existingPoller.errorThreshold = data['errorThreshold']
        existingPoller.errorHoldTime = data['errorHoldTime']
        db.session.commit()
        return {'success': True}
    except Exception, e:
        logger.error('DBAPI modifyPollerByName() DB put operation failed: %s' % e)
        return {'success': False, 'err': 'DBAPI modifyPollerByName() DB put operation failed: %s' % e}


def getPollersAll():

    logger = logging.getLogger('SubfragiumDBLib')

    try:
        pollers = models.Poller.query.filter().all()
        pollerList = []
        for poller in pollers:
            item = {'name': poller.name,
                    'minProcesses': poller.minProcesses,
                    'maxProcesses': poller.maxProcesses,
                    'numProcesses': poller.numProcesses,
                    'holdDown': poller.holdDown,
                    'cycleTime': poller.cycleTime,
                    'storageType': poller.storageType,
                    'storageLocation': poller.storageLocation,
                    'disabled': poller.disabled,
                    'errorThreshold': poller.errorThreshold,
                    'errorHoldTime': poller.errorHoldTime}
            pollerList.append(item)
        return {'success': True, 'obj': pollerList}
    except Exception, e:
        logger.error('DBAPI getTargetsAll() Failed: %s' % e)
        return {'success': False, 'err': 'DBAPI getTargetsAll() Failed: %s' % e}


# Oids
def putOidByOid(data):

    logger = logging.getLogger('SubfragiumDBLib')

    result = SubfragiumUtilsLib.validateObj(SubfragiumDBLibSchema.putOidByOid, data)
    if not result['success']:
        return {'success': False, 'err': 'DBAPI putOidByOid() invalid data: %s' % result['err']}

    newOid = models.Oid(data['target'],
                        data['name'],
                        data['oid'],
                        data['poller'],
                        data['enabled'])
    try:
        db.session.add(newOid)
        db.session.commit()
        return {'success': True}
    except Exception, e:
        logger.error('DBAPI putOidByOid() DB put operation failed: %s' % e)
        return {'success': False, 'err': 'DBAPI putOidByOid() DB put operation failed: %s' % e}


def deleteOidByOid(data):

    logger = logging.getLogger('SubfragiumDBLib')

    result = SubfragiumUtilsLib.validateObj(SubfragiumDBLibSchema.deleteOidByOid, data)
    if not result['success']:
        return {'success': False, 'err': 'DBAPI deleteOidByOid() invalid data: %s' % result['err']}

    oidId = data['target'] + ':' + data['oid']

    try:
        existingOid = models.Oid.query.filter(models.Oid.id == oidId).first()
        db.session.delete(existingOid)
        db.session.commit()
        return {'success': True}
    except Exception, e:
        logger.error('DBAPI deleteOidByOid() Failed: %s' % e)
        return {'success': False, 'err': 'DBAPI deleteOidByOid() Failed: %s' % e}


def getOidsByTarget(data):

    logger = logging.getLogger('SubfragiumDBLib')

    result = SubfragiumUtilsLib.validateObj(SubfragiumDBLibSchema.getOidsByTarget, data)
    if not result['success']:
        return {'success': False, 'err': 'DBAPI getOidByTarget() invalid data: %s' % result['err']}

    try:
        existingOids = models.Oid.query.filter(models.Oid.target == data['target']).all()
        if existingOids is []:
            return {'success': True, 'obj': []}

        oidList = []
        for oid in existingOids:
            item = {'id': oid.id,
                    'oid': oid.oid,
                    'name': oid.name,
                    'target': oid.target,
                    'poller': oid.poller,
                    'enabled': oid.enabled,
                    'snmpString': oid.targetInfo.snmpString,
                    'timeout': oid.targetInfo.timeout
                    }
            oidList.append(item)
        return {'success': True, 'obj': oidList}

    except Exception, e:
        logger.error('DBAPI getOidsByTarget() Failed: %s' % e)
        return {'success': False, 'err': 'DBAPI getOidsByTarget() Failed: %s' % e}


def getOidsByPoller(data):

    logger = logging.getLogger('SubfragiumDBLib')

    result = SubfragiumUtilsLib.validateObj(SubfragiumDBLibSchema.getOidsByPoller, data)
    if not result['success']:
        return {'success': False, 'err': 'DBAPI getOidByPoller() invalid data: %s' % result['err']}

    try:
        existingOids = models.Oid.query.filter(models.Oid.poller == data['poller']).all()
        if existingOids is []:
            return {'success': True, 'obj': []}

        oidList = []
        for oid in existingOids:
            item = {'id': oid.id,
                    'oid': oid.oid,
                    'name': oid.name,
                    'target': oid.target,
                    'poller': oid.poller,
                    'enabled': oid.enabled,
                    'snmpString': oid.targetInfo.snmpString,
                    'timeout': oid.targetInfo.timeout
                    }
            oidList.append(item)
        return {'success': True, 'obj': oidList}

    except Exception, e:
        logger.error('DBAPI getOidsByPoller() Failed: %s' % e)
        return {'success': False, 'err': 'DBAPI getOidsByPoller() Failed: %s' % e}


def getOidByOid(data):

    logger = logging.getLogger('SubfragiumDBLib')

    result = SubfragiumUtilsLib.validateObj(SubfragiumDBLibSchema.getOidByOid, data)
    if not result['success']:
        return {'success': False, 'err': 'DBAPI getOidByOid() invalid data: %s' % result['err']}

    oidId = data['target'] + ':' + data['oid']
    try:
        existingOid = models.Oid.query.filter(models.Oid.id == oidId).first()
        if existingOid is None:
            return {'success': True, 'obj': []}
        else:
            return {'success': True, 'obj': [{
                'id': existingOid.id,
                'name': existingOid.name,
                'oid': existingOid.oid,
                'target': existingOid.target,
                'poller': existingOid.poller,
                'enabled': existingOid.enabled,
                'snmpString': existingOid.targetInfo.snmpString,
                'timeout': existingOid.targetInfo.timeout}]}
    except Exception, e:
        logger.error('DBAPI getOidByOid() Failed: %s' % e)
        return {'success': False, 'err': 'DBAPI getOidByOid() Failed: %s' % e}


def getOidsQuery(queryParameters):

    logger = logging.getLogger('SubfragiumDBLib')

    result = SubfragiumUtilsLib.validateObj(SubfragiumDBLibSchema.getOidsQuery, queryParameters)
    if not result['success']:
        return {'success': False, 'err': 'DBAPI getOidQuery() invalid data: %s' % result['err']}

    if 'poller' in queryParameters:
        queryParameters['poller'] = '%' + queryParameters['poller'] + '%'
    else:
        queryParameters['poller'] = '%'

    if 'oid' in queryParameters:
        queryParameters['oid'] = '%' + queryParameters['oid'] + '%'
    else:
        queryParameters['oid'] = '%'

    if 'target' in queryParameters:
        queryParameters['target'] = '%' + queryParameters['target'] + '%'
    else:
        queryParameters['target'] = '%'

    if 'name' in queryParameters:
        queryParameters['name'] = '%' + queryParameters['name'] + '%'
    else:
        queryParameters['name'] = '%'

    # Don't need to modify queryParameters for 'enabled' its a boolean field

    try:

        if 'enabled' in queryParameters:
            print 'Running with enabled match'
            oids = models.Oid.query.filter(
              models.Oid.poller.like(queryParameters['poller']),
              models.Oid.oid.like(queryParameters['oid']),
              models.Oid.target.like(queryParameters['target']),
              models.Oid.name.like(queryParameters['name']),
              models.Oid.enabled.is_(queryParameters['enabled'])).all()
        else:
            oids = models.Oid.query.filter(
                models.Oid.poller.like(queryParameters['poller']),
                models.Oid.oid.like(queryParameters['oid']),
                models.Oid.target.like(queryParameters['target']),
                models.Oid.name.like(queryParameters['name'])).all()

        oidList = []
        for oid in oids:
            item = {'id': oid.id,
                    'oid': oid.oid,
                    'name': oid.name,
                    'target': oid.target,
                    'poller': oid.poller,
                    'snmpString': oid.targetInfo.snmpString,
                    'enabled': oid.enabled,
                    'timeout': oid.targetInfo.timeout
                    }
            oidList.append(item)
        return {'success': True, 'obj': oidList}

    except Exception, e:
        logger.error('DBAPI getOidsQuery() Failed: %s' % e)
        return {'success': False, 'err': 'DBAPI getOidsQuery() Failed: %s' % e}


def modifyOidByOid(data):

    logger = logging.getLogger('SubfragiumDBLib')

    result = SubfragiumUtilsLib.validateObj(SubfragiumDBLibSchema.modifyOidByOid, data)
    if not result['success']:
        return {'success': False, 'err': 'DBAPI modifyOidByName() invalid data: %s' % result['err']}

    oidId = data['target'] + ':' + data['oid']

    try:
        existingOid = models.Oid.query.filter(models.Oid.id == oidId).first()
        existingOid.name = data['name']
        existingOid.oid = data['oid']
        existingOid.target = data['target']
        existingOid.poller = data['poller']
        existingOid.enabled = data['enabled']
        db.session.commit()
        return {'success': True}
    except Exception, e:
        logger.error('DBAPI modifyOidByName() DB put operation failed: %s' % e)
        return {'success': False, 'err': 'DBAPI modifyOidByName() DB put operation failed: %s' % e}


def getOidsAll():

    logger = logging.getLogger( 'SubfragiumDBLib' )

    try:
        oids = models.Oid.query.filter().all()
        oidList = []
        for oid in oids:
            item = {'id': oid.id,
                    'oid': oid.oid,
                    'name': oid.name,
                    'target': oid.target,
                    'poller': oid.poller,
                    'snmpString': oid.targetInfo.snmpString,
                    'enabled': oid.enabled,
                    'timeout': oid.targetInfo.timeout
                    }
            oidList.append(item)
        return {'success': True, 'obj': oidList}
    except Exception, e:
        logger.error('DBAPI getOidsAll() Failed: %s' % e)
        return {'success': False, 'err': 'DBAPI getOidsAll() Failed: %s' % e}
