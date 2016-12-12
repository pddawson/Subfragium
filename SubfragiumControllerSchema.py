
PingTarget = {
  'type': 'object',
  'properties': {
    'snmpString': {
      'type': 'string',
    }
  },
  'required': ['snmpString'],
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
    }
  },
  'required': ['minProcesses',
               'maxProcesses',
               'numProcesses',
               'holdDown',
               'cycleTime',
               'storageType',
               'storageLocation'],
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
    }
  },
  'required': ['poller','name'],
  'additionalProperties': False
}