##
## Target Schema
##

from schema import Optional

putTargetByName = {
  'name': basestring,
  'snmpString': basestring
}

updateTargetByName = {
  'name': basestring,
  'snmpString': basestring
}

deleteTargetByName = {
  'name': basestring
}

getTargetByName = {
  'name': basestring
}

modifyTargetByName = {
  'name': basestring,
  'snmpString': basestring
}

##
## Poller Schema
##

putPollerByName = {
  'name': basestring,
  'minProcesses': int,
  'maxProcesses': int,
  'numProcesses': int,
  'holdDown': int,
  'cycleTime': int,
  'storageType': basestring,
  'storageLocation': basestring
}

deletePollerByName = {
  'name': basestring
}

getPollerByName = {
  'name': basestring
}

modifyPollerByName = {
  'name': basestring,
  'minProcesses': int,
  'maxProcesses': int,
  'numProcesses': int,
  'holdDown': int,
  'cycleTime': int,
  'storageType': basestring,
  'storageLocation': basestring
}

##
## Oid Schema
##

putOidByOid = {
  'name': basestring,
  'oid': basestring,
  'target': basestring,
  'poller': basestring
}

deleteOidByOid = {
  'target': basestring,
  'oid': basestring
}

getOidsByTarget = {
  'target': basestring
}

getOidsByPoller = {
  'poller': basestring
}

getOidByOid = {
  'target': basestring,
  'oid': basestring
}

getOidsQuery = {
  Optional('target'): basestring,
  Optional('name'): basestring,
  Optional('poller'): basestring,
  Optional('oid'): basestring,
  # Add all parameters as optional
}

modifyOidByOid = {
  'name': basestring,
  'oid': basestring,
  'target': basestring,
  'poller': basestring
}