
PingTarget = {
  'type': 'object',
  'properties': {
    'snmpString': {
      'type': 'string',
    },
    'timeout': {
      'type': 'number',
      'minimum': 1
    }
  },
  'required': ['snmpString', 'timeout'],
  'additionalProperties': False
}

Poller = {
  'type': 'object',
  'properties': {
    'minProcesses': {
      'type': 'number',
      'minimum': 1
    },
    'maxProcesses': {
      'type': 'number',
      'minimum': 2
    },
    'numProcesses': {
      'type': 'number',
      'minimum': 1
    },
    'holdDown': {
      'type': 'number',
      'minimum': 1
    },
    'cycleTime': {
      'type': 'number',
      'minimum': 1
    },
    'storageType': {
      'type': 'string'
    },
    'storageLocation': {
      'type': 'string'
    },
    'disabled': {
      'type': 'boolean'
    },
    'errorThreshold': {
      'type': 'number'
    },
    'errorHoldTime': {
      'type': 'number'
    }
  },
  'required': ['minProcesses',
               'maxProcesses',
               'numProcesses',
               'holdDown',
               'cycleTime',
               'storageType',
               'storageLocation',
               'disabled',
               'errorThreshold',
               'errorHoldTime'],
  'additionalProperties': False
}

Oid = {
  'type': 'object',
  'properties': {
    'poller': {
      'type': 'string'
    },
    'name': {
      'type': 'string'
    },
    'enabled': {
      'type': 'boolean'
    }
  },
  'required': ['poller', 'name', 'enabled'],
  'additionalProperties': False
}
