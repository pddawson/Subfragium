##
## Target Schema
##

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
  'cycleTime': int
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
  'cycleTime': int
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

modifyOidByOid = {
  'name': basestring,
  'oid': basestring,
  'target': basestring,
  'poller': basestring
}