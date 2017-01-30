from app import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref


class Target(db.Model):
    __tablename__ = 'Targets'

    name = db.Column(db.String, primary_key=True)
    snmpString = db.Column(db.String)
    timeout = db.Column(db.Integer)

    def __init__(self, name, snmpString, timeout):
        self.name = name
        self.snmpString = snmpString
        self.timeout = timeout

    def __str__(self):
        return 'name: %s, snmpString: %s, timeout: %s' % (self.name, self.snmpString, self.timeout)


class Poller(db.Model):

    __tablename__ = 'Pollers'

    name = db.Column(db.String, primary_key=True)
    minProcesses = db.Column(db.Integer)
    maxProcesses = db.Column(db.Integer)
    numProcesses = db.Column(db.Integer)
    holdDown = db.Column(db.Integer)
    cycleTime = db.Column(db.Integer)
    storageType = db.Column(db.String)
    storageLocation = db.Column(db.String)
    disabled = db.Column(db.Boolean)

    def __init__(self, name, minProcesses, maxProcesses, numProcesses,
                 holdDown, cycleTime, storageType, storageLocation, disabled):
        self.name = name
        self.minProcesses = minProcesses
        self.maxProcesses = maxProcesses
        self.numProcesses = numProcesses
        self.holdDown = holdDown
        self.cycleTime = cycleTime
        self.storageType = storageType
        self.storageLocation = storageLocation
        self.disabled = disabled

    def __str__(self):
        return 'name: %s, ' \
               'minProc: %s, ' \
               'maxProc: %s, ' \
               'numProc: %s, ' \
               'holdDown: %s, ' \
               'cycleTime: %s' \
               'storageType: %s' \
               'storageLocation: %s' \
               'disabled: %s' % \
               (self.name,
                self.minProcesses,
                self.maxProcesses,
                self.numProcesses,
                self.holdDown,
                self.cycleTime,
                self.storageType,
                self.storageLocation,
                self.disabled)


class Oid(db.Model):

    __tablename__ = 'Oids'

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    oid = db.Column(db.String)
    target = db.Column(db.String, ForeignKey('Targets.name'))
    poller = db.Column(db.String, ForeignKey('Pollers.name'))
    enabled = db.Column(db.Boolean)

    targetInfo = relationship('Target', backref=backref('Targets', order_by=target))

    def __init__(self, target, name, oid, poller, enabled):
        self.id = str(target) + ':' + str(oid)
        self.name = name
        self.oid = oid
        self.target = target
        self.poller = poller
        self.enabled = enabled

    def __str__(self):
        return 'id: %s, name: %s, oid: %s, target: %s, poller: %s, enabled: %s' % (self.id,
                                                                                   self.name,
                                                                                   self.oid,
                                                                                   self.target,
                                                                                   self.poller,
                                                                                   self.enabled)
