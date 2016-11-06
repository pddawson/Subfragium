import unittest
import tempfile
import os
import json
import mock

import SubfragiumDBAPI
import SubfragiumController
from app import db

class TestTargetApi(unittest.TestCase):

  def setUp(self):

    (fd, fileName) = tempfile.mkstemp()
    SubfragiumController.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + fileName
    SubfragiumController.app.config['SQLALCHEMY_DATABASE_PATH'] = fileName
    SubfragiumController.app.config['TESTING'] = True
    self.app = SubfragiumController.app.test_client()
    self.maxDiff = None

  def tearDown(self):
    os.unlink(SubfragiumController.app.config['SQLALCHEMY_DATABASE_PATH'])

  def testTargetMethod(self):
    res = self.app.post('/target/1.1.1.1')
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 405)

    resRequired = {'response': {'success': False, 'err': 'Unsupported Method'}}
    self.assertEqual(resJson, resRequired)

  def testTargetMissingName(self):
    res = self.app.get('/target')
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 404)

    resRequired = {
      'response': {
        'success': False,
        'err': '404: Not Found'
      }
    }
    self.assertEquals(resJson, resRequired)

  def testTargetInvalidName(self):
    res = self.app.get('/target/name=1234&')
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 404)

    resRequired = {
      'response': {
        'success': False,
        'err': 'Invalid hostname or IP address'
      }
    }
    self.assertEquals(resJson, resRequired)

  def testGetTargetNoSuchTarget(self):
    res = self.app.get('/target/1.1.1.1')
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 404)

    resRequired = {
      'response': {
        'success': False,
        'err': 'No target 1.1.1.1 found in DB'
      }
    }

    self.assertEquals(resJson, resRequired)

  @mock.patch('SubfragiumDBAPI.getTargetByName')
  def testGetTargetDbFailure(self, mockGet):
    mockGet.return_value = {
      'success': False,
      'code': 503,
      'err': 'DBAPI getTargetByName() Failed: Generic Error'
    }
    res = self.app.get('/target/1.1.1.1')
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 503)

    resRequired = {
      'response': {
        'success': False,
        'err': 'getTarget() - Failed: DBAPI getTargetByName() Failed: Generic Error'
      }
    }

    self.assertEquals(resJson, resRequired)

  def testGetTargetSuccess(self):
    res = self.app.put('/target/1.1.1.1',
                       data=json.dumps({'snmpString': 'eur'}),
                       content_type = 'application/json')
    res = self.app.get('/target/1.1.1.1')
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 200)

    resRequired = {
      'response': {
        'success': True,
        'obj': {
          'name': '1.1.1.1',
          'snmpString': 'eur'
        }
      }
    }

    self.assertEquals(resJson, resRequired)

  def testPutTargetNoJson(self):
    res = self.app.put('/target/1.1.1.1')
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 404)

    resRequired = {
      'response': {
        'success': False,
        'err': 'putTarget() - No JSON provided'
      }
    }

    self.assertEquals(resJson, resRequired)

  def testPutTargetBadJson(self):
    res = self.app.put('/target/1.1.1.1',
                       data=json.dumps({'snmp': 'eur'}),
                       content_type='application/json')
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 404)
    self.assertEquals(resJson['response']['success'], False)

  # Need to mock the SubfragiumDBAPI call
  @mock.patch('SubfragiumDBAPI.getTargetByName')
  def testPutTargetDbFailureInGetTarget(self, mockDB):
    mockDB.return_value = {
      'success': False,
      'code': 503,
      'err': 'DBAPI getTargetByName() Failed: Generic Error'
    }
    res = self.app.put('/target/1.1.1.1',
                       data=json.dumps({'snmpString': 'eur'}),
                       content_type='application/json')
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 503)
    self.assertEquals(resJson['response']['success'], False)

  # Need to mock the SubfragiumDBAPI call
  @mock.patch('SubfragiumDBAPI.updateTargetByName')
  def testPutTargetDbFailureInUpdateTarget(self, mockUpdate):
    res = self.app.put('/target/1.1.1.1',
                       data=json.dumps({'snmpString': 'eur'}),
                       content_type='application/json')

    mockUpdate.return_value = {
      'success': False,
      'code': 503,
      'err': 'DBAPI updateTargetByName() DB put operation failed: Generic Error'
    }
    res = self.app.put('/target/1.1.1.1',
                       data=json.dumps({'snmpString': 'eur'}),
                       content_type='application/json')
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 503)
    self.assertEquals(resJson['response']['success'], False)

  def testPutTargetSuccessfully(self):
    res = self.app.put('/target/1.1.1.1',
                       data=json.dumps({'snmpString': 'eur'}),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': True
      }
    }

    self.assertEquals(resJson, resRequired)

  def testPutTargetSuccessfulModification(self):
    res = self.app.put('/target/1.1.1.1',
                       data=json.dumps({'snmpString': 'eur'}),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    res = self.app.put('/target/1.1.1.1',
                       data=json.dumps({'snmpString': 'usa'}),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    res = self.app.get('/target/1.1.1.1')
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 200)

    resRequired = {
      'response': {
        'success': True,
        'obj': {
          'name': '1.1.1.1',
          'snmpString': 'usa'
        }
      }
    }

    self.assertEquals(resJson, resRequired)

  # Need to mock the SubfragiumDBAPI call
  @mock.patch('SubfragiumDBAPI.updateTargetByName')
  def testPutTargetDbFailureModifyingExistingTarget(self, mockUpdate):
    res = self.app.put('/target/1.1.1.1',
                       data=json.dumps({'snmpString': 'eur'}),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    mockUpdate.return_value = {
      'success': False,
      'code': 503,
      'err': 'putTarget() - Failed: DBAPI updateTargetByName() DB put operation failed Generic Error'
    }

    res = self.app.put('/target/1.1.1.1',
                       data=json.dumps({'snmpString': 'usa'}),
                       content_type='application/json')
    self.assertEquals(res.status_code, 503)

  # Need to mock the SubfragiumDBAPI call
  @mock.patch('SubfragiumDBAPI.putTargetByName')
  def testPutTargetDbFailureAddingTarget(self, mockAdd):
    mockAdd.return_value = {
      'success': False,
      'code': 503,
      'err': 'putTarget() Failed: DBAPI putTarget() DB put operation failed Generic Error'
    }
    res = self.app.put('/target/1.1.1.1',
                       data=json.dumps({'snmpString': 'eur'}),
                       content_type='application/json')

    self.assertEquals(res.status_code, 503)

  def testPutTargetSuccess(self):
    res = self.app.put('/target/1.1.1.1',
                       data=json.dumps({'snmpString': 'eur'}),
                       content_type='application/json')

    self.assertEquals(res.status_code, 200)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': True,
      }
    }
    self.assertEquals(resJson, resRequired)

  @mock.patch('SubfragiumDBAPI.getTargetByName')
  def testDeleteTargetDbFailureGettingTarget(self, mockGetTarget):
    mockGetTarget.return_value = {
      'success': False,
      'code': 503,
      'err': 'DBAPI getTargetByName() Failed: Generic Error'
    }

    res = self.app.delete('/target/1.1.1.1')
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 503)

    resRequired = {
      'response': {
        'success': False,
        'err': 'deleteTarget() Failed: DBAPI getTargetByName() Failed: Generic Error'
      }
    }
    self.assertEquals(resJson, resRequired)

  @mock.patch('SubfragiumDBAPI.getTargetByName')
  def testDeleteTargetNoSuchTarget(self, mockGetTarget):
    mockGetTarget.return_value = {
      'success': True,
      'code': 404,
      'obj': []
    }

    res = self.app.delete('/target/1.1.1.1')
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 404)

    resRequired = {
      'response': {
        'success': False,
        'err': 'Target 1.1.1.1 not found'
      }
    }

    self.assertEquals(resJson, resRequired)

  @mock.patch('SubfragiumDBAPI.getOidsByTarget')
  def testDeleteTargetDbFailureGettingOids(self, mockGetOids):

    res = self.app.put('/target/1.1.1.1',
                       data=json.dumps({'snmpString': 'eur'}),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    mockGetOids.return_value = {
      'success': False,
      'err': 'DBAPI getOidsByTarget() Failed: Generic Error'
    }

    res = self.app.delete('/target/1.1.1.1')
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 503)

    resRequired = {
      'response': {
        'success': False,
        'err': 'deleteTarget() Failed: DBAPI getOidsByTarget() Failed: Generic Error'
      }
    }

    self.assertEquals(resJson, resRequired)

  @mock.patch('SubfragiumDBAPI.getOidsByTarget')
  def testDeleteTargetOidsExistOnTarget(self, mockGetOids):

    res = self.app.put('/poller/poller1',
                       data=json.dumps({'name': 'poller1', 'minProcesses': 1, 'maxProcesses': 50, 'numProcesses': 1, 'holdDown': 20}),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    res = self.app.put('/target/1.1.1.1',
                       data=json.dumps({'snmpString': 'eur'}),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    res = self.app.put('/oid/1.1.1.1/1.3.2.6.1',
                       data=json.dumps({'name': 'test', 'poller': 'poller1'}),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    mockGetOids.return_value = {
      'success': True,
      'obj': {
        ''
      }
    }


    # Delete Target : Failure - OIDs using target
  # Delete Target : Failure - DB Porblem Deleting Target
  # Delete Target : Success



if __name__ == '__main__':
  unittest.main()
