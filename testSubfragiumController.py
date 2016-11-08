import unittest
import tempfile
import os
import json
import mock

import SubfragiumController

target = '1.1.1.1'
targetData = {
  'snmpString': 'eur'
}

poller = 'poller1'
pollerData = {
  'name': 'poller1',
  'minProcesses': 1,
  'maxProcesses': 50,
  'numProcesses': 1,
  'holdDown': 20
}

oid = '1.3.6.1.2.1'
oidData = {
  'poller': 'poller1',
  'name': 'network.interface.ifInHcOctets.GigabitEthernet0/0'
}

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

  def testTargetInvalidMethod(self):
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
    res = self.app.get('/target/' + target)
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 404)

    resRequired = {
      'response': {
        'success': False,
        'err': 'No target ' + target + ' found in DB'
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
    res = self.app.get('/target/' + target)
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
    res = self.app.put('/target/' + target,
                       data=json.dumps(targetData),
                       content_type = 'application/json')
    res = self.app.get('/target/1.1.1.1')
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 200)

    resRequired = {
      'response': {
        'success': True,
        'obj': {
          'name': target,
          'snmpString': targetData['snmpString']
        }
      }
    }

    self.assertEquals(resJson, resRequired)

  def testPutTargetNoJson(self):
    res = self.app.put('/target/' + target)
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

    newTargetData = targetData.copy()
    del(newTargetData['snmpString'])
    newTargetData['snmp'] =  'eur'

    res = self.app.put('/target/' + target,
                       data=json.dumps(newTargetData),
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
    res = self.app.put('/target/' + target,
                       data=json.dumps(targetData),
                       content_type='application/json')
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 503)
    self.assertEquals(resJson['response']['success'], False)

  # Need to mock the SubfragiumDBAPI call
  @mock.patch('SubfragiumDBAPI.updateTargetByName')
  def testPutTargetDbFailureInUpdateTarget(self, mockUpdate):
    res = self.app.put('/target/' + target,
                       data=json.dumps(targetData),
                       content_type='application/json')

    mockUpdate.return_value = {
      'success': False,
      'code': 503,
      'err': 'DBAPI updateTargetByName() DB put operation failed: Generic Error'
    }
    res = self.app.put('/target/' + target,
                       data=json.dumps(targetData),
                       content_type='application/json')
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 503)
    self.assertEquals(resJson['response']['success'], False)

  def testPutTargetSuccessfully(self):
    res = self.app.put('/target/' + target,
                       data=json.dumps(targetData),
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
    res = self.app.put('/target/' + target,
                       data=json.dumps(targetData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    res = self.app.put('/target/' + target,
                       data=json.dumps(targetData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    res = self.app.get('/target/' + target)
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 200)

    resRequired = {
      'response': {
        'success': True,
        'obj': {
          'name': target,
          'snmpString': targetData['snmpString']
        }
      }
    }

    self.assertEquals(resJson, resRequired)

  # Need to mock the SubfragiumDBAPI call
  @mock.patch('SubfragiumDBAPI.updateTargetByName')
  def testPutTargetDbFailureModifyingExistingTarget(self, mockUpdate):
    res = self.app.put('/target/' + target,
                       data=json.dumps(targetData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    mockUpdate.return_value = {
      'success': False,
      'code': 503,
      'err': 'putTarget() - Failed: DBAPI updateTargetByName() DB put operation failed Generic Error'
    }

    res = self.app.put('/target/' + target,
                       data=json.dumps(targetData),
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
    res = self.app.put('/target/' + target,
                       data=json.dumps(targetData),
                       content_type='application/json')

    self.assertEquals(res.status_code, 503)

  def testPutTargetSuccess(self):
    res = self.app.put('/target/' + target,
                       data=json.dumps(targetData),
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

    res = self.app.delete('/target/' + target)
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

    res = self.app.delete('/target/' + target)
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 404)

    resRequired = {
      'response': {
        'success': False,
        'err': 'Target ' + target + ' not found'
      }
    }

    self.assertEquals(resJson, resRequired)

  @mock.patch('SubfragiumDBAPI.getOidsByTarget')
  def testDeleteTargetDbFailureGettingOids(self, mockGetOids):

    res = self.app.put('/target/' + target,
                       data=json.dumps(targetData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    mockGetOids.return_value = {
      'success': False,
      'err': 'DBAPI getOidsByTarget() Failed: Generic Error'
    }

    res = self.app.delete('/target/' + target)
    resJson = json.loads(res.data)

    self.assertEquals(res.status_code, 503)

    resRequired = {
      'response': {
        'success': False,
        'err': 'deleteTarget() Failed: DBAPI getOidsByTarget() Failed: Generic Error'
      }
    }

    self.assertEquals(resJson, resRequired)

  def testDeleteTargetOidsExistOnTarget(self):

    res = self.app.put('/poller/' + poller,
                       data=json.dumps(pollerData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    res = self.app.put('/target/' + target,
                       data=json.dumps(targetData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    res = self.app.put('/oid/' + target + '/' + oid,
                       data=json.dumps(oidData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    res = self.app.delete('/target/' + target)
    self.assertEquals(res.status_code, 404)
    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': False,
        'err': 'deleteTarget() Failed: Target %s in use for oids'
      }
    }

  @mock.patch('SubfragiumDBAPI.deleteTargetByName')
  def testDeleteTargetDbFailureInDelete(self, mockDelete):
    res = self.app.put('/target/' + target,
                       data=json.dumps(targetData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    mockDelete.return_value = {
      'success': False,
      'err': 'DBAPI deleteTargetByName() Failed: Generic Error'
    }

    res = self.app.delete('/target/' + target)
    self.assertEquals(res.status_code, 503)
    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': False,
        'err': 'deleteTarget() Failed: DBAPI deleteTargetByName() Failed: Generic Error'
      }
    }
    self.assertEquals(resJson, resRequired)

  def testDeleteTargetSuccess(self):
    res = self.app.put('/target/' + target,
                       data=json.dumps(targetData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    res = self.app.delete('/target/' + target)
    self.assertEquals(res.status_code, 200)
    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': True
      }
    }

    self.assertEquals(resJson, resRequired)

  def testGetTargetsInvalidMethod(self):
    res = self.app.put('/targets')
    self.assertEquals(res.status_code, 405)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': False,
        'err': 'Unsupported Method'
      }
    }

    self.assertEquals(resJson, resRequired)

  @mock.patch('SubfragiumDBAPI.getTargetsAll')
  def testGetTargetsDbFailure(self, mockGet):

    mockGet.return_value = {
      'success': False,
      'err': 'DBAPI getTargetsAll() Failed: Generic Error'
    }

    res = self.app.get('/targets')
    self.assertEquals(res.status_code, 503)
    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': False,
        'err': 'getTargetsAll() - Failed: DBAPI getTargetsAll() Failed: Generic Error'
      }
    }
    self.assertEquals(resJson, resRequired)

  def testGetTargetsNoTargets(self):

    res = self.app.get('/targets')
    self.assertEquals(res.status_code, 200)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': True,
        'obj': []
      }
    }
    self.assertEquals(resJson, resRequired)

  def testGetTargetsSuccess(self):

    res = self.app.put('/target/' + target,
                       data=json.dumps(targetData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    res = self.app.get('/targets')
    self.assertEquals(res.status_code, 200)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': True,
        'obj': [
          {
            'name': target,
            'snmpString': targetData['snmpString']
          }
        ]
      }
    }
    self.assertEquals(resJson, resRequired)

  ############################################################################
  ############################################################################

  def testPollerInvalidMethod(self):
    res = self.app.post('/poller/' + poller)
    self.assertEquals(res.status_code, 405)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': False,
        'err': 'Unsupported Method'
      }
    }

    self.assertEquals(resJson, resRequired)

  def testPollerMissingName(self):
    res = self.app.get('/poller')
    self.assertEquals(res.status_code, 404)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': False,
        'err': '404: Not Found'
      }
    }

    self.assertEquals(resJson, resRequired)

  def testPutPollerNoJson(self):
    res = self.app.put('/poller/' + poller)
    self.assertEquals(res.status_code, 404)

  def testPutPollerInvalidJson(self):
    res = self.app.put('/poller/' + poller)
    self.assertEquals(res.status_code, 404)

  @mock.patch('SubfragiumDBAPI.getPollerByName')
  def testPutPollerDBFailureGetPoller(self, mockGet):
    mockGet.return_value = {
      'success': False,
      'err': 'DBAPI putPollerByName() DB put operation failed: Generic Error'
    }

    res = self.app.put('/poller/' + poller,
                       data=json.dumps(pollerData),
                       content_type='application/json')

    self.assertEquals(res.status_code, 503)

    resJson = json.loads(res.data)

    reqRequired = {
      'response': {
        'success': False,
        'err': 'putPoller() - Failure: DBAPI putPollerByName() DB put operation failed: Generic Error'
      }
    }

    self.assertEquals(resJson, reqRequired)

  @mock.patch('SubfragiumDBAPI.modifyPollerByName')
  def testPutPollerDbFailureInUpdatePoller(self, mockModify):
    res = self.app.put('/poller/' + poller,
                       data=json.dumps(pollerData),
                       content_type='application/json')

    mockModify.return_value = {
      'success': False,
      'err': 'DBAPI modifyPollerByName() DB put operation failed: Generic Error'
    }

    res = self.app.put('/poller/' + poller,
                       data=json.dumps(pollerData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 503)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': False,
        'err': 'putPoller() - Failed: DBAPI modifyPollerByName() DB put operation failed: Generic Error'
      }
    }

    self.assertEquals(resJson, resRequired)

  @mock.patch('SubfragiumDBAPI.putPollerByName')
  def testPutPollerDbFailurePut(self, mockPut):
    mockPut.return_value = {
      'success': False,
      'err': 'DBAPI deletePollerByName() Failed: Generic Error'
    }
    res = self.app.put('/poller/' + poller,
                       data=json.dumps(pollerData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 503)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': False,
        'err': 'putPoller() Failed: DBAPI deletePollerByName() Failed: Generic Error'
      }
    }
    self.assertEquals(resJson, resRequired)

  def testPutPollerSuccess(self):

    res = self.app.put('/poller/' + poller,
                       data=json.dumps(pollerData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': True
      }
    }
    self.assertEquals(resJson, resRequired)

    res = self.app.get('/poller/' + poller,
                       data=json.dumps(pollerData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': True,
        'obj': {
          'name': 'poller1',
          'minProcesses': 1,
          'maxProcesses': 50,
          'numProcesses': 1,
          'holdDown': 20
        }
      }
    }
    self.assertEquals(resJson, resRequired)

  def testPutPollerSuccess(self):
    res = self.app.put('/poller/' + poller,
                       data=json.dumps(pollerData),
                       content_type='application/json')
    print res.data
    self.assertEquals(res.status_code, 200)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': True
      }
    }
    self.assertEquals(resJson, resRequired)

  @mock.patch('SubfragiumDBAPI.getPollerByName')
  def testGetPollerDbFailure(self, mockGet):
    mockGet.return_value = {
      'success': False,
      'err': 'DBAPI getPollerByName() Failed: Generic Failure'
    }

    res = self.app.get('/poller/' + poller)
    self.assertEquals(res.status_code, 503)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': False,
        'err': 'getPoller() - Failed: DBAPI getPollerByName() Failed: Generic Failure'
      }
    }
    self.assertEquals(resJson, resRequired)

  def testGetPollerNoSuchPoller(self):
    res = self.app.get('/poller/' + poller)
    self.assertEquals(res.status_code, 404)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': False,
        'err': 'No poller poller1 found in DB'
      }
    }
    self.assertEquals(resJson, resRequired)

  def testGetPollerSuccess(self):
    res = self.app.put('/poller/' + poller,
                       data=json.dumps(pollerData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    res = self.app.get('/poller/' + poller)
    self.assertEquals(res.status_code, 200)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': True,
        'obj': {
          'name': 'poller1',
          'minProcesses': 1,
          'maxProcesses': 50,
          'numProcesses': 1,
          'holdDown': 20
        }
      }
    }
    self.assertEquals(resJson, resRequired)

  @mock.patch('SubfragiumDBAPI.getPollerByName')
  def testDeletePollerDbFailureGetPoller(self, mockGet):
    mockGet.return_value = {
      'success': False,
      'err': 'DBAPI deletePollerByName() Failed: Generic Error'
    }

    res = self.app.delete('/poller/' + poller)
    self.assertEquals(res.status_code, 503)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': False,
        'err': 'deletePoller() Failed: DBAPI deletePollerByName() Failed: Generic Error'
      }
    }
    self.assertEquals(resJson, resRequired)

  def testDeletePollerNoSuchPoller(self):
    res = self.app.delete('/poller/' + poller)
    self.assertEquals(res.status_code, 404)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': False,
        'err': 'Poller poller1 not found'
      }
    }

    self.assertEquals(resJson, resRequired)

  def testDeletePollerExistingOids(self):
    res = self.app.put('/target/' + target,
                       data=json.dumps(targetData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    res = self.app.put('/poller/' + poller,
                       data=json.dumps(pollerData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    res = self.app.put('/oid/' + target + '/' + oid,
                       data=json.dumps(oidData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    res = self.app.delete('/poller/' + poller)
    self.assertEquals(res.status_code, 404)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': False,
        'err': 'Poller poller1 in use for oids'
      }
    }
    self.assertEquals(resJson, resRequired)

  # DELETE /poller : DB Failure in getOids
  @mock.patch('SubfragiumDBAPI.getOidsByPoller')
  def testDeletePollerDbFailureGetoids(self, mockGet):
    res = self.app.put('/poller/' + poller,
                       data=json.dumps(pollerData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    mockGet.return_value = {
      'success': False,
      'err': 'DBAPI getOidsByPoller() Failed: Generic Failure'
    }
    res = self.app.delete('/poller/' + poller)
    self.assertEquals(res.status_code, 503)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': False,
        'err': 'deletePoller() Failed: DBAPI getOidsByPoller() Failed: Generic Failure'
      }
    }
    print resJson
    self.assertEquals(resJson, resRequired)

  # DELETE /poller : DB Failure in deletePollerByName()
  def testDeletePollerSuccess(self):
    res = self.app.put('/poller/' + poller,
                       data=json.dumps(pollerData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    res = self.app.delete('/poller/' + poller)
    self.assertEquals(res.status_code, 200)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': True
      }
    }
    self.assertEquals(resJson, resRequired)

  def testGetPollersInvalidMethod(self):
    res = self.app.post('/pollers')
    self.assertEquals(res.status_code, 405)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': False,
        'err': 'Unsupported Method'
      }
    }

    self.assertEquals(resJson, resRequired)

  @mock.patch('SubfragiumDBAPI.getPollersAll')
  def testGetPollersDbFailure(self, mockGet):
    mockGet.return_value = {
      'success': False,
      'err': 'DBAPI getTargetsAll() Failed: Generic Error'
    }

    res = self.app.get('/pollers');
    self.assertEquals(res.status_code, 503)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': False,
        'err': 'getPollersAll() Failed: DBAPI getTargetsAll() Failed: Generic Error'
      }
    }

    self.assertEquals(resJson, resRequired)

  def testGetPollersNoPollers(self):
    res = self.app.get('/pollers')
    self.assertEquals(res.status_code, 200)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': True,
        'obj': []
      }
    }

    self.assertEquals(resJson, resRequired)

  def testGetPollersSuccess(self):
    res = self.app.put('/poller/' + poller,
                       data=json.dumps(pollerData),
                       content_type='application/json')
    self.assertEquals(res.status_code, 200)

    res = self.app.get('/pollers')
    self.assertEquals(res.status_code, 200)

    resJson = json.loads(res.data)

    resRequired = {
      'response': {
        'success': True,
        'obj': [
          {
            'name': 'poller1',
            'minProcesses': 1,
            'maxProcesses': 50,
            'numProcesses': 1,
            'holdDown': 20
          }
        ]
      }
    }

    self.assertEquals(resJson, resRequired)

if __name__ == '__main__':
  unittest.main()
