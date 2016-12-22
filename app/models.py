from app import db

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

class Target(db.Model):
  __tablename__ = 'Targets'

  name = db.Column(db.String, primary_key=True)
  snmpString = db.Column(db.String)

  def __init__(self, name, snmpString):
    self.name = name
    self.snmpString = snmpString

  def __str__(self):
    return 'name: %s, snmpString: %s' % (self.name, self.snmpString)


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

  def __init__(self, name, minProcesses, maxProcesses, numProcesses, holdDown, cycleTime, storageType, storageLocation):
    self.name = name
    self.minProcesses = minProcesses
    self.maxProcesses = maxProcesses
    self.numProcesses = numProcesses
    self.holdDown = holdDown
    self.cycleTime = cycleTime
    self.storageType = storageType
    self.storageLocation = storageLocation

  def __str__(self):
      return 'name: %s, ' \
             'minProc: %s, ' \
             'maxProc: %s, ' \
             'numProc: %s, ' \
             'holdDown: %s, ' \
             'cycleTime: %s' \
             'storageType: %s' \
             'storageLocation: %s' % \
             (self.name,
              self.minProcesses,
              self.maxProcesses,
              self.numProcesses,
              self.holdDown,
              self.cycleTime,
              self.storageType,
              self.storageLocation)


class Oid(db.Model):

  __tablename__ = 'Oids'

  id = db.Column(db.String, primary_key=True)
  name = db.Column(db.String)
  oid = db.Column(db.String)
  target = db.Column(db.String, ForeignKey('Targets.name'))
  poller = db.Column(db.String, ForeignKey('Pollers.name')) # Do we need this?
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
