
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
    'name': {
      'type': 'string'
    },
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
    }
  },
  'required': ['name', 'minProcesses', 'maxProcesses', 'numProcesses', 'holdDown'],
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