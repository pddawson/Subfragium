from app import models
from app import db


# Targets
def putTargetByName(name, snmpString):

    if name == '' or snmpString == '':
        return {'success': False, 'err': 'DBAPI putTargetByName() incorrect arguments'}

    newTarget = models.Target(name, snmpString)

    try:
        db.session.add(newTarget)
        db.session.commit()
        return {'success': True}
    except Exception, e:
        return {'success': False, 'err': 'DBAPI putTarget() DB put operation failed %s' % e}


def updateTargetByName(name, data):

    if name == '' or data['snmpString'] == '':
        return {'success': False, 'err': 'DBAPI updateTargetByName() incorrect arguments'}

    try:
        existingTarget = models.Target.query.filter(models.Target.name == name).first()
        existingTarget.snmpString = data['snmpString']
        db.session.commit()
        return {'success': True}
    except Exception, e:
        return {'success': False, 'err': 'DBAPI updateTargetByName() DB put operation failed %s' % e}


def deleteTargetByName(name):

    if name == '':
        return {'success': False, 'err': 'DBAPI deleteTargetByName() no target provided'}

    try:
        existingTarget = models.Target.query.filter(models.Target.name == name).first()
        db.session.delete(existingTarget)
        db.session.commit()
        return { 'success': True}
    except Exception, e:
        return {'success': False, 'err': 'DBAPI deleteTargetByName() Failed: %s' % e}


def getTargetByName(name):

    if name == '':
        return {'success': False, 'err': 'DBAPI getTargetByName() no target provided'}

    try:
        target = models.Target.query.filter(models.Target.name == name).first()
        if target == None:
            return {'success': True, 'obj': []}
        else:
            return {'success': True, 'obj': [{'name': target.name, 'snmpString': target.snmpString}]}
    except Exception, e:
        return {'success': False, 'err': 'DBAPI getTargetByName() Failed: %s' % e}


def modifyTargetByName(name, data):

    if name == '' or data['snmpString']:
      return {'success': False, 'err': 'DBAPI modifyTargetByName() incorrect arguments'}

    try:
      existingTarget = models.Target.query.filter(models.Target.name == name).first()
      existingTarget.snmpString = data['snmpString']
      db.session.commit()
      return {'success': True}
    except Exception, e:
      return {'success': False, 'err': 'DBAPI modifyTargetByName() DB put operation failed %s' % e}


def getTargetsAll():

    try:
        targets = models.Target.query.filter().all()
        targetList = []
        for target in targets:
            item = {'name': target.name, 'snmpString': target.snmpString}
            targetList.append(item)
        return {'success': True, 'obj': targetList}
    except Exception, e:
        return {'success': False, 'err': 'DBAPI getTargetsAll() Failed: %s' % e}

# Pollers
def putPollerByName(name, data):

    if name == '' or data == '':
        return {'success': False, 'err': 'DBAPI putPollerByName() incorrect arguments'}

    newPoller = models.Poller(name,
                              data['minProcesses'],
                              data['maxProcesses'],
                              data['numProcesses'],
                              data['holdDown'])
    try:
        db.session.add(newPoller)
        db.session.commit()
        return {'success': True}
    except Exception, e:
        return {'success': False, 'err': 'DBAPI putPollerByName() DB put operation failed %s' % e}

def deletePollerByName(name):

    if name == '':
        return {'success': False, 'err': 'DBAPI deletePollerByName() incorrect arguments'}

    try:
        poller = models.Poller.query.filter(models.Poller.name == name).first()
        db.session.delete(poller)
        db.session.commit()
        return {'success': True}
    except Exception, e:
        return {'success': False, 'err': 'DBAPI deletePollerByName() Failed: %s' % e}


def getPollerByName(name):

    if name == '':
        return {'success': False, 'err': 'DBAPI getPollerByName() no poller name provided'}

    try:
        poller = models.Poller.query.filter(models.Poller.name == name).first()
        if poller == None:
            return {'success': True, 'obj':[]}
        else:
            return {'success': True, 'obj': [ {
                'name': poller.name,
                'minProcesses': poller.minProcesses,
                'maxProcesses': poller.maxProcesses,
                'numProcesses': poller.numProcesses,
                'holdDown': poller.holdDown}]}
    except Exception, e:
        return {'success': False, 'err': 'DBAPI getPollerByNae() Failed: %s' % e}


def modifyPollerByName(name, data):

    if name == '' or data['minProcesses'] == '' or data['maxProcesses'] == '' or data['numProcesses'] == '' or data['holdDown'] == '':
        return {'success': False, 'err': 'DBAPI modifyPollerByName() incorrect arguments'}

    try:
        existingPoller = models.Poller.query.filter(models.Poller.name == name).first()
        existingPoller.minProcesses = data['minProcesses']
        existingPoller.maxProcesses = data['maxProcesses']
        existingPoller.numProcesses = data['numProcesses']
        existingPoller.holdDown = data['holdDown']
        db.session.commit()
        return {'success': True}
    except Exception, e:
        return {'success': False, 'err': 'DBAPI modifyPollerByName() DB put operation failed: %s' % e}

def getPollersAll():

    try:
        pollers = models.Poller.query.filter().all()
        pollerList = []
        for poller in pollers:
            item = {'name': poller.name,
                    'minProcesses': poller.minProcesses,
                    'maxProcesses': poller.maxProcesses,
                    'numProcesses': poller.numProcesses,
                    'holdDown': poller.holdDown}
            pollerList.append(item)
        return {'success': True, 'obj': pollerList}
    except Exception, e:
        return {'success': False, 'err': 'DBAPI getTargetsAll() Failed: %s' % e}

# Oids
def putOidByOid(target, oid, data):

    if target == '' or oid == '' or data['name'] == '' or data['poller'] == '':
        return {'success': False, 'err': 'DBAPI putOidByOid() incorrect arguments'}

    newOid = models.Oid(target,
                        data['name'],
                        oid,
                        data['poller'])
    try:
        db.session.add(newOid)
        db.session.commit()
        return {'success': True}
    except Exception, e:
        return {'success': False, 'err': 'DBAPI putOidByOid() DB put operation failed %s' % e}

def deleteOidByOid(target, oid):

    if target == '' or oid == '':
        return {'success': False, 'err': 'DBAPI deleteOidByOid() incorrect arguments'}

    oidId = target + ':' + oid

    try:
        existingOid = models.Oid.query.filter(models.Oid.id == oidId).first()
        db.session.delete(existingOid)
        db.session.commit()
        return {'success': True}
    except Exception, e:
        return {'success': False, 'err': 'DBAPI deleteOidByOid() Failed: %s' % e}


def getOidsByTarget(target):

    if target == '':
        return {'success': False, 'err': 'DBAPI getOidByTarget() no target provided'}

    try:
        existingOids = models.Oid.query.filter(models.Oid.target == target).all()
        if existingOids == []:
            return {'success': True, 'obj': []}

        oidList = []
        for oid in existingOids:
            item = {'id': oid.id,
                    'oid': oid.oid,
                    'name': oid.name,
                    'target': oid.target,
                    'poller': oid.poller
                    }
            oidList.append(item)
        return {'success': True, 'obj': oidList}

    except Exception, e:
        return {'success': False, 'err': 'DBAPI getOidsByTarget() Failed: %s' % e}


def getOidsByPoller(poller):

    if poller == '':
        return {'success': False, 'err': 'DBAPI getOidByPoller() no poller provided'}

    try:
        existingOids = models.Oid.query.filter(models.Oid.poller == poller).all()
        if existingOids == []:
            return {'success': True, 'obj': []}

        oidList = []
        for oid in existingOids:
            item = {'id': oid.id,
                    'oid': oid.oid,
                    'name': oid.name,
                    'target': oid.target,
                    'poller': oid.poller
                    }
            oidList.append(item)
        return {'success': True, 'obj': oidList}

    except Exception, e:
        return {'success': False, 'err': 'DBAPI getOidsByPoller() Failed: %s' % e}


def getOidByOid(target, oid):

    if target == '' or oid == '':
        return {'success': False, 'err': 'DBAPI getOidByOid() incorrect arguments'}

    oidId = target + ':' + oid
    try:
        existingOid = models.Oid.query.filter(models.Oid.id == oidId).first()
        if existingOid == None:
            return {'success': True, 'obj': []}
        else:
            return {'success': True, 'obj': [{
                'id': existingOid.id,
                'name': existingOid.name,
                'oid': existingOid.oid,
                'target': existingOid.target,
                'poller': existingOid.poller}]}
    except Exception, e:
        return {'success': False, 'err': 'DBAPI getOidByOid() Failed: %s' % e}


def getOidsQuery(queryParameters):

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

    try:
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
                  'poller': oid.poller
                  }
          oidList.append(item)
        return {'success': True, 'obj': oidList}

    except Exception, e:
        return {'success': False, 'err': 'DBAPI getOidsQuery() Failed: %s' % e}

def modifyOidByOid(target, oid, data):

    if target == '' or oid == '' or data['name'] == '' or data['poller'] == '':
        return {'success': False, 'err': 'DBAPI modifyOidByName() incorrect arguments'}

    oidId = target + ':' + oid

    try:
        existingOid = models.Oid.query.filter(models.Oid.id == oidId).first()
        existingOid.name = data['name']
        existingOid.oid = oid
        existingOid.target = target
        existingOid.poler = data['poller']
        db.session.commit()
        return {'success': True}
    except Exception, e:
        return {'success': False, 'err': 'DBAPI modifyOidByName() DB put operation failed %s' % e}


def getOidsAll():

    try:
        oids = models.Oid.query.filter().all()
        oidList = []
        for oid in oids:
            item = {'id': oid.id,
                    'oid': oid.oid,
                    'name': oid.name,
                    'target': oid.target,
                    'poller': oid.poller
                    }
            oidList.append(item)
        return {'success': True, 'obj': oidList}
    except Exception, e:
        return {'success': False, 'err': 'DBAPI getOidsAll() Failed: %s' % e}