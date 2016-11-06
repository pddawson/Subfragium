putTargetByNameInput = {
  'type': 'object',
    'properties': {
      'name': {
        'type': 'string'
        # 'rquired': True
      },
      'snmpString': {
        'type': 'string',
        # 'required': True
      }
    },
    'additionalProperties': False
}

getTargetByNameInput = {
  'type': 'object',
    'properties': {
      'name': {
        'type': 'string'
      }
    }
}