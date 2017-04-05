PutDeleteOutput = {
    'type': 'object',
    'oneOf': [
        {'$ref': '#/definitions/success'},
        {'$ref': '#/definitions/failure'}
    ],
    'definitions': {
        'success': {
            'type': 'object',
            'properties': {
                'success': {
                    'type': 'boolean'
                }
            },
            'required': ['success'],
            'additionalProperties': False
        },
        'failure': {
            'type': 'object',
            'properties': {
                'err': {
                    'type': 'string'
                }
            },
            'required': ['err'],
            'additionalProperties': False
        }
    }
}

PutTargetInput = {
  'type': 'object',
  'properties': {
    'snmpString': {
      'type': 'string'
    },
    'timeout': {
      'type': 'number'
    },
  },
  'required': ['snmpString', 'timeout'],
  'additionalProperties': False
}

GetTargetOutput = {
  'type': 'object',
  'oneOf': [
    {'$ref': '#/definitions/success'},
    {'$ref': '#/definitions/failure'}
  ],
  'definitions': {
    'success': {
      'type': 'object',
      'properties': {
        'success': {
          'type': 'boolean'
        },
        'obj': {
          'type': 'object',
          'properties': {
            'snmpString': {
                'type': 'string',
            },
            'name': {
              'type': 'string'
            },
            'timeout': {
              'type': 'number',
              'minimum': 1
            }
          },
          'required': ['snmpString', 'timeout', 'name'],
          'additionalProperties': False
        }
      },
      'required': ['success', 'obj'],
      'additionalProperties': False,
    },
    'failure': {
      'type': 'object',
      'properties': {
        'err': {
          'type': 'string'
        }
      },
      'required': ['err'],
      'additionalProperties': False
    }
  }
}

GetTargetsOutput = {
  'type': 'object',
  'oneOf': [
    {'$ref': '#/definitions/success'},
    {'$ref': '#/definitions/failure'}
  ],
  'definitions': {
    'success': {
      'type': 'object',
      'properties': {
        'success': {
          'type': 'boolean'
        },
        'obj': {
          'type': 'array',
          'items': {'type': 'object'},
          'properties': {
            'snmpString': {
                'type': 'string',
            },
            'name': {
              'type': 'string'
            },
            'timeout': {
              'type': 'number',
              'minimum': 1
            }
          },
          'required': ['snmpString', 'timeout', 'name'],
          'additionalProperties': False
        }
      },
      'required': ['success', 'obj'],
      'additionalProperties': False,
    },
    'failure': {
      'type': 'object',
      'properties': {
        'err': {
          'type': 'string'
        }
      },
      'required': ['err'],
      'additionalProperties': False
    }
  }
}

PutPollerInput = {
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

GetPollerOutput = {
  'type': 'object',
  'oneOf': [
    {'$ref': '#/definitions/success'},
    {'$ref': '#/definitions/failure'}
  ],
  'definitions': {
    'success': {
      'type': 'object',
      'properties': {
        'success': {
          'type': 'boolean'
        },
        'obj': {
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
          'required': [
            'minProcesses',
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
      },
      'required': ['success', 'obj'],
      'additionalProperties': False,
    },
    'failure': {
      'type': 'object',
      'properties': {
        'err': {
          'type': 'string'
        }
      },
      'required': ['err'],
      'additionalProperties': False
    }
  }
}

GetPollersOutput = {
  'type': 'object',
  'oneOf': [
    {'$ref': '#/definitions/success'},
    {'$ref': '#/definitions/failure'}
  ],
  'definitions': {
    'success': {
      'type': 'object',
      'properties': {
        'success': {
          'type': 'boolean'
        },
        'obj': {
          'type': 'array',
          'items': {'type': 'object'},
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
          'required': [
            'minProcesses',
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
      },
      'required': ['success', 'obj'],
      'additionalProperties': False,
    },
    'failure': {
      'type': 'object',
      'properties': {
        'err': {
          'type': 'string'
        }
      },
      'required': ['err'],
      'additionalProperties': False
    }
  }
}


PutOidInput = {
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

GetOidOutput = {
  'type': 'object',
  'oneOf': [
    {'$ref': '#/definitions/success'},
    {'$ref': '#/definitions/failure'}
  ],
  'definitions': {
    'success': {
      'type': 'object',
      'properties': {
        'success': {
          'type': 'boolean'
        },
        'obj': {
          'type': 'object',
          'properties': {
              'enabled': {
                'type': 'boolean'
              },
              'id': {
                'type': 'string'
              },
              'name': {
                'type': 'string'
              },
              'oid': {
                'type': 'string'
              },
              'poller': {
                'type': 'string'
              },
              'snmpString': {
                'type': 'string'
              },
              'target': {
                'type': 'string'
              },
              'timeout': {
                'type': 'number'
              }
          },
          'required': [
            'enabled',
            'id',
            'name',
            'oid',
            'poller',
            'snmpString',
            'target',
            'timeout'
          ],
          'additionalProperties': False
        }
      },
      'required': ['success', 'obj'],
      'additionalProperties': False,
    },
    'failure': {
      'type': 'object',
      'properties': {
        'err': {
          'type': 'string'
        }
      },
      'required': ['err'],
      'additionalProperties': False
    }
  }
}

GetOidsOutput = {
  'type': 'object',
  'oneOf': [
    {'$ref': '#/definitions/success'},
    {'$ref': '#/definitions/failure'}
  ],
  'definitions': {
    'success': {
      'type': 'object',
      'properties': {
        'success': {
          'type': 'boolean'
        },
        'obj': {
          'type': 'array',
          'items': {'type': 'object'},
          'properties': {
              'enabled': {
                'type': 'boolean'
              },
              'id': {
                'type': 'string'
              },
              'name': {
                'type': 'string'
              },
              'oid': {
                'type': 'string'
              },
              'poller': {
                'type': 'string'
              },
              'snmpString': {
                'type': 'string'
              },
              'target': {
                'type': 'string'
              },
              'timeout': {
                'type': 'number'
              }
          },
          'required': [
            'enabled',
            'id',
            'name',
            'oid',
            'poller',
            'snmpString',
            'target',
            'timeout'
          ],
          'additionalProperties': False
        }
      },
      'required': ['success', 'obj'],
      'additionalProperties': False,
    },
    'failure': {
      'type': 'object',
      'properties': {
        'err': {
          'type': 'string'
        }
      },
      'required': ['err'],
      'additionalProperties': False
    }
  }
}
