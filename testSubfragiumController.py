import unittest
import tempfile
import os
import json
import copy
import mock
from mock import Mock

import SubfragiumController
import SubfragiumDBLib

target = '1.1.1.1'
targetData = {
    'snmpString': 'eur',
    'timeout': 10
}

target2 = '2.2.2.2'
target2Data = {
    'snmpString': 'usa',
    'timeout': 10
}

poller = 'poller1'
pollerData = {
    'minProcesses': 1,
    'maxProcesses': 50,
    'numProcesses': 1,
    'holdDown': 20,
    'cycleTime': 5,
    'storageType': 'graphite',
    'storageLocation': 'pickle://graphite:5000',
    'disabled': False,
    'errorThreshold': 3,
    'errorHoldTime': 60
}

poller2 = 'poller2'
poller2Data = {
    'minProcesses': 1,
    'maxProcesses': 25,
    'numProcesses': 2,
    'holdDown': 40,
    'cycleTime': 5,
    'storageType': 'graphite',
    'storageLocation': 'pickle://graphite:5000',
    'disabled': False,
    'errorThreshold': 6,
    'errorHoldTime': 120
}

oid = '1.3.6.1.2.1'
oidData = {
    'poller': 'poller1',
    'name': 'network.interface.ifInHcOctets.GigabitEthernet0/0',
    'enabled': True
}

oid2 = '1.3.6.1.2.2'
oid2Data = {
    'poller': 'poller2',
    'name': 'network.interface.ifOutHcOctets.GigabitEthernet0/0',
    'enabled': False
}


class TestControllerApi(unittest.TestCase):

    def setUp(self):

        (fd, fileName) = tempfile.mkstemp()
        SubfragiumController.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + fileName
        SubfragiumController.app.config['SQLALCHEMY_DATABASE_PATH'] = fileName
        SubfragiumController.app.config['TESTING'] = True
        self.app = SubfragiumController.app.test_client()
        self.maxDiff = None

    def tearDown(self):
        os.unlink(SubfragiumController.app.config['SQLALCHEMY_DATABASE_PATH'])

    def addTestData(self):
        res = self.app.put('/target/' + target,
                           data=json.dumps(targetData),
                           content_type='application/json')
        self.assertEquals(res.status_code, 200)

        res = self.app.put('/target/' + target2,
                           data=json.dumps(target2Data),
                           content_type='application/json')
        self.assertEquals(res.status_code, 200)

        res = self.app.put('/poller/' + poller,
                           data=json.dumps(pollerData),
                           content_type='application/json')
        self.assertEquals(res.status_code, 200)

        res = self.app.put('/poller/' + poller2,
                           data=json.dumps(poller2Data),
                           content_type='application/json')
        self.assertEquals(res.status_code, 200)

        res = self.app.put('/oid/' + target + '/' + oid,
                           data=json.dumps(oidData),
                           content_type='application/json')
        self.assertEquals(res.status_code, 200)

        res = self.app.put('/oid/' + target2 + '/' + oid2,
                           data=json.dumps(oid2Data),
                           content_type='application/json')
        self.assertEquals(res.status_code, 200)

    def testTargetInvalidMethod(self):
        res = self.app.post('/target/1.1.1.1')
        resJson = json.loads(res.data)

        self.assertEquals(res.status_code, 405)

        resRequired = {'response': {'success': False, 'err': 'Unsupported Method: 405: Method Not Allowed'}}
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

    @mock.patch('SubfragiumDBLib.getTargetByName')
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
                           content_type='application/json')
        self.assertEquals(res.status_code, 200)

        res = self.app.get('/target/1.1.1.1')
        resJson = json.loads(res.data)

        self.assertEquals(res.status_code, 200)

        resRequired = {
            'response': {
                'success': True,
                'obj': {
                    'name': target,
                    'snmpString': targetData['snmpString'],
                    'timeout': 10
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
        newTargetData['snmp'] = 'eur'

        res = self.app.put('/target/' + target,
                           data=json.dumps(newTargetData),
                           content_type='application/json')
        resJson = json.loads(res.data)

        self.assertEquals(res.status_code, 404)
        self.assertEquals(resJson['response']['success'], False)

    @mock.patch('SubfragiumDBLib.getTargetByName')
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

    @mock.patch('SubfragiumDBLib.updateTargetByName')
    def testPutTargetDbFailureInUpdateTarget(self, mockUpdate):
        res = self.app.put('/target/' + target,
                           data=json.dumps(targetData),
                           content_type='application/json')

        self.assertEquals(res.status_code, 200)
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

    @mock.patch('SubfragiumDBLib.updateTargetByName')
    def testPutTargetDbFailureInUpdateTarget(self, mockUpdate):
        mockUpdate.return_value = {
            'success': False,
            'err': 'DBAPI updateTargetByName() DB put operation failed: Generic Error'
        }

        newTargetData = targetData.copy()
        del(newTargetData['snmpString'])
        newTargetData['snmpString'] = 'usa'

        res = self.app.put('/target/' + target,
                           data=json.dumps(targetData),
                           content_type='application/json')
        self.assertEquals(res.status_code, 200)

        res = self.app.put('/target/' + target,
                           data=json.dumps(newTargetData),
                           content_type='application/json')
        self.assertEquals(res.status_code, 503)

    def testPutTargetSuccessfulModification(self):
        res = self.app.put('/target/' + target,
                           data=json.dumps(targetData),
                           content_type='application/json')
        self.assertEquals(res.status_code, 200)

        newTargetData = targetData.copy()
        newTargetData['snmpString'] = 'usa'

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
                    'snmpString': targetData['snmpString'],
                    'timeout': 10
                }
            }
        }

        self.assertEquals(resJson, resRequired)

    # Need to mock the SubfragiumDBLib call
    @mock.patch('SubfragiumDBLib.updateTargetByName')
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

    # Need to mock the SubfragiumDBLib call
    @mock.patch('SubfragiumDBLib.putTargetByName')
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

    @mock.patch('SubfragiumDBLib.getTargetByName')
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

    @mock.patch('SubfragiumDBLib.getTargetByName')
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

    @mock.patch('SubfragiumDBLib.getOidsByTarget')
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
                'err': 'deleteTarget() Failed: Target %s in use for oids' % target
            }
        }
        self.assertEquals(resJson, resRequired)

    @mock.patch('SubfragiumDBLib.deleteTargetByName')
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
                'err': 'Unsupported Method: 405: Method Not Allowed'
            }
        }

        self.assertEquals(resJson, resRequired)

    @mock.patch('SubfragiumDBLib.getTargetsAll')
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
                        'snmpString': targetData['snmpString'],
                        'timeout': 10
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
                'err': 'Unsupported Method: 405: Method Not Allowed'
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

    @mock.patch('SubfragiumDBLib.getPollerByName')
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

    @mock.patch('SubfragiumDBLib.modifyPollerByName')
    def testPutPollerDbFailureInUpdatePoller(self, mockModify):
        res = self.app.put('/poller/' + poller,
                           data=json.dumps(pollerData),
                           content_type='application/json')

        self.assertEquals(res.status_code, 200)
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

    @mock.patch('SubfragiumDBLib.putPollerByName')
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

    def testPutPollerMinProcessGreaterThanMaxProcessesFailure(self):

        newPollerData = copy.deepcopy(pollerData)
        newPollerData[ 'minProcesses' ] = 51

        res = self.app.put('/poller/' + poller,
                           data=json.dumps(newPollerData),
                           content_type='application/json')
        self.assertEquals(res.status_code, 404)

        resJson = json.loads(res.data)
        reqRequired = {
            'response': {
                'success': False,
                'err': 'putPoller() - minProcesses must be less than maxProcesses'
            }
        }

        self.assertEquals(resJson, reqRequired)

    def testPutPollerNumProcessesLessThanMinProcessesFailure(self):

        newPollerData = copy.deepcopy(pollerData)
        newPollerData['minProcesses'] = 2
        newPollerData['numProcesses'] = 1

        res = self.app.put('/poller/' + poller,
                           data=json.dumps(newPollerData),
                           content_type='application/json')
        self.assertEquals(res.status_code, 404)

        resJson = json.loads(res.data)
        reqRequired = {
            'response': {
                'success': False,
                'err': 'putPoller() - numProcesses must be greater than minProcesses'
            }
        }

        self.assertEquals(resJson, reqRequired)

    def testPutPollerNumProcessesGreaterThanMaxProcessesFailure(self):

        newPollerData = copy.deepcopy(pollerData)
        newPollerData['numProcesses'] = 51

        res = self.app.put('/poller/' + poller,
                           data=json.dumps(newPollerData),
                           content_type='application/json')
        self.assertEquals(res.status_code, 404)

        resJson = json.loads(res.data)
        reqRequired = {
            'response': {
                'success': False,
                'err': 'putPoller() - numProcesses must be less than maxProcesses'
            }
        }

        self.assertEquals(resJson, reqRequired)

    def testPutPollerModifyExistingSuccess(self):

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

    @mock.patch('SubfragiumDBLib.getPollerByName')
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
                    'holdDown': 20,
                    'cycleTime': 5,
                    'storageType': 'graphite',
                    'storageLocation': 'pickle://graphite:5000',
                    'disabled': False,
                    'errorThreshold': 3,
                    'errorHoldTime': 60
                }
            }
        }
        self.assertEquals(resJson, resRequired)

    @mock.patch('SubfragiumDBLib.getPollerByName')
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
    @mock.patch('SubfragiumDBLib.getOidsByPoller')
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
        self.assertEquals(resJson, resRequired)

    # No test for deletePoller() DB failure in deletePoller
    @mock.patch('SubfragiumDBLib.deletePollerByName')
    def testDeletePollerDbFailureInDelete(self, mockDelete):
        mockDelete.return_value = {
            'success': False,
            'err': 'DBAPI deletePollerByName() Failed: Generic Error'
        }

        res = self.app.put('/poller/' + poller,
                           data=json.dumps(pollerData),
                           content_type='application/json')
        self.assertEquals(res.status_code, 200)

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
                'err': 'Unsupported Method: 405: Method Not Allowed'
            }
        }

        self.assertEquals(resJson, resRequired)

    @mock.patch('SubfragiumDBLib.getPollersAll')
    def testGetPollersDbFailure(self, mockGet):
        mockGet.return_value = {
            'success': False,
            'err': 'DBAPI getTargetsAll() Failed: Generic Error'
        }

        res = self.app.get('/pollers')
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
                        'holdDown': 20,
                        'cycleTime': 5,
                        'storageType': 'graphite',
                        'storageLocation': 'pickle://graphite:5000',
                        'disabled': False,
                        'errorThreshold': 3,
                        'errorHoldTime': 60
                    }
                ]
            }
        }

        self.assertEquals(resJson, resRequired)

    def testOidInvalidMethod(self):
        res = self.app.post('/oid/' + target + '/' + oid)
        self.assertEquals(res.status_code, 405)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': False,
                'err': 'Unsupported Method: 405: Method Not Allowed'
            }
        }
        self.assertEquals(resJson, resRequired)

    def testOidMissingTarget(self):
        res = self.app.get('/oid/')
        self.assertEquals(res.status_code, 404)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': False,
                'err': '404: Not Found'
            }
        }

        self.assertEquals(resJson, resRequired)

    def testOidMissingOid(self):
        res = self.app.get('/oid/' + target + '/')
        self.assertEquals(res.status_code, 404)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': False,
                'err': '404: Not Found'
            }
        }

        self.assertEquals(resJson, resRequired)

    def testPutOidMissingJson(self):
        res = self.app.put('/oid/' + target + '/' + oid)
        self.assertEquals(res.status_code, 404)

    def testPutOidInvalidJson(self):

        newOidData = oidData.copy()
        del(newOidData['poller'])

        res = self.app.put('/oid/' + target + '/' + oid,
                           data=json.dumps(newOidData),
                           content_type='application/json')
        self.assertEquals(res.status_code, 404)

    @mock.patch('SubfragiumDBLib.getPollerByName')
    def testPutOidDBFailureGetPoller(self, mockGet):
        mockGet.return_value = {
            'success': False,
            'err': 'DBAPI getPollerByName() Failed: Generic Error'
        }

        res = self.app.put('/oid/' + target + '/' + oid,
                           data=json.dumps(oidData),
                           content_type='application/json')
        self.assertEquals(res.status_code, 503)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': False,
                'err': 'putOid() Failure: DBAPI getPollerByName() Failed: Generic Error'
            }
        }

        self.assertEquals(resJson, resRequired)

    def testPutOidNoSuchPoller(self):
        res = self.app.put('/oid/' + target + '/' + oid,
                           data=json.dumps(oidData),
                           content_type='application/json')
        self.assertEquals(res.status_code, 404)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': False,
                'err': 'Poller poller1 does not exist'
            }
        }

        self.assertEquals(resJson, resRequired)

    @mock.patch('SubfragiumDBLib.getTargetByName')
    def testPutOidDBFailureGetTarget(self, mockGet):
        mockGet.return_value = {
            'success': False,
            'err': 'DBAPI getTargetByName() Failed: Generic Error'
        }

        res = self.app.put('/poller/' + poller,
                           data=json.dumps(pollerData),
                           content_type='application/json')
        self.assertEquals(res.status_code, 200)

        res = self.app.put('/oid/' + target + '/' + oid,
                           data=json.dumps(oidData),
                           content_type='application/json')
        self.assertEquals(res.status_code, 503)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': False,
                'err': 'putOid() Failure: DBAPI getTargetByName() Failed: Generic Error'
            }
        }

        self.assertEquals(resJson, resRequired)

    def testPutOidNoSuchTarget(self):
        res = self.app.put('/poller/' + poller,
                           data=json.dumps(pollerData),
                           content_type='application/json')
        self.assertEquals(res.status_code, 200)

        res = self.app.put('/oid/' + target + '/' + oid,
                           data=json.dumps(oidData),
                           content_type='application/json')
        self.assertEquals(res.status_code, 404)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': False,
                'err': 'Target 1.1.1.1 does not exist'
            }
        }
        self.assertEquals(resJson, resRequired)

    @mock.patch('SubfragiumDBLib.getOidByOid')
    def testPutOidDbFailureInGetOid(self, mockGet):
        mockGet.return_value = {
            'success': False,
            'err': 'DBAPI getOidByOid() Failed: Generic Error'
        }

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
        self.assertEquals(res.status_code, 503)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': False,
                'err': 'putOid() Failure: DBAPI getOidByOid() Failed: Generic Error'
            }
        }
        self.assertEquals(resJson, resRequired)

    @mock.patch('SubfragiumDBLib.putOidByOid')
    def testPutOidDbFailireInPutOid(self, mockPut):
        mockPut.return_value = {
            'success': False,
            'err': 'DBAPI putOidByOid() DB put operation failed: Generic Error'
        }

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
        self.assertEquals(res.status_code, 503)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': False,
                'err': 'putPoller() Failed: DBAPI putOidByOid() DB put operation failed: Generic Error'
            }
        }
        self.assertEquals(resJson, resRequired)

    @mock.patch('SubfragiumDBLib.modifyOidByOid')
    def testPutOidDbFailureUpdatingExistingOid(self, mockModify):
        mockModify.return_value = {
            'success': False,
            'err': 'DBAPI modifyOidByName() DB put operation failed: Generic Error'
        }

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

        newOid = oidData.copy()
        newOid['name'] = 'Test String'

        res = self.app.put('/oid/' + target + '/' + oid,
                           data=json.dumps(newOid),
                           content_type='application/json')
        self.assertEquals(res.status_code, 503)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': False,
                'err': 'putOid() - Failed: DBAPI modifyOidByName() DB put operation failed: Generic Error'
            }
        }

        self.assertEquals(resJson, resRequired)

    def testPutOidUpdateingExistingSuccess(self):
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

        newOid = oidData.copy()
        newOid['name'] = 'Test String'

        res = self.app.put('/oid/' + target + '/' + oid,
                           data=json.dumps(newOid),
                           content_type='application/json')
        self.assertEquals(res.status_code, 200)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': True
            }
        }

        self.assertEquals(resJson, resRequired)

    def testPutOidSuccess(self):
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

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': True
            }
        }
        self.assertEquals(resJson, resRequired)

    @mock.patch('SubfragiumDBLib.getOidByOid')
    def testGetOidDbFailureInGetOid(self, mockGet):
        mockGet.return_value = {
            'success': False,
            'err': 'DBAPI getOidsByTarget() Failed: Generic Error'
        }

        res = self.app.get('/oid/' + target + '/' + oid)
        self.assertEquals(res.status_code, 503)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': False,
                'err': 'getOid() Failure: DBAPI getOidsByTarget() Failed: Generic Error'
            }
        }
        self.assertEquals(resJson, resRequired)

    def testGetOidNoSuchOid(self):
        res = self.app.get('/oid/' + target + '/' + oid)
        self.assertEquals(res.status_code, 404)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': False,
                'err': 'getOid() - No such OID ' + target + ':' + oid
            }
        }
        self.assertEquals(resJson, resRequired)

    def testGetOidSuccess(self):
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

        res = self.app.get('/oid/' + target + '/' + oid)
        self.assertEquals(res.status_code, 200)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': True,
                'obj': {
                    'id': target + ':' + oid,
                    'name': oidData['name'],
                    'oid': oid,
                    'target': target,
                    'poller': poller,
                    'enabled': True,
                    'snmpString': targetData['snmpString'],
                    'timeout': targetData['timeout']
                }
            }
        }

        self.assertEquals(resJson, resRequired)

    def testDeleteOidDbFailureInGetOid(self):
        savedDbCall = SubfragiumDBLib.getOidByOid
        SubfragiumDBLib.getOidByOid = Mock(wraps=SubfragiumDBLib.getOidByOid)
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

        SubfragiumDBLib.getOidByOid.return_value = {
            'success': False,
            'err': 'DBAPI getOidByOid() Failed: Generic Error'
        }

        res = self.app.delete('/oid/' + target + '/' + oid)
        self.assertEquals(res.status_code, 503)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': False,
                'err': 'deleteOid() Failure: DBAPI getOidByOid() Failed: Generic Error'
            }
        }

        self.assertEquals(resJson, resRequired)

        SubfragiumDBLib.getOidByOid = savedDbCall

    def testDeleteOidNoSuchOid(self):
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

        res = self.app.delete('/oid/' + target + '/' + '1.2.3.6.1.1.1.1')
        self.assertEquals(res.status_code, 404)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': False,
                'err': 'deleteOid() - No such OID ' + target + ':' + '1.2.3.6.1.1.1.1'
            }
        }

        self.assertEquals(resJson, resRequired)

    @mock.patch('SubfragiumDBLib.deleteOidByOid')
    def testDeleteOidDbFailureInDeleteOid(self, mockDelete):
        mockDelete.return_value = {
            'success': False,
            'err': 'DBAPI deleteOidByOid() Failed: Generic Error'
        }
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

        res = self.app.delete('/oid/' + target + '/' + oid)
        self.assertEquals(res.status_code, 503)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': False,
                'err': 'deleteOid() Failed: DBAPI deleteOidByOid() Failed: Generic Error'
            }
        }
        self.assertEquals(resJson, resRequired)

    def testDeleteOidSuccess(self):

        # DELETE /oid : Success
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

        res = self.app.delete('/oid/' + target + '/' + oid)
        self.assertEquals(res.status_code, 200)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': True
            }
        }

        self.assertEquals(resJson, resRequired)

    @mock.patch('SubfragiumDBLib.getOidsAll')
    def testGetOidsDbFailureGetAllOids(self, mockGet):
        mockGet.return_value = {
            'success': False,
            'err': 'DBAPI getOidsAll() Failed: Generic Error'
        }

        TestControllerApi.addTestData(self)

        res = self.app.get('/oids')
        self.assertEquals(res.status_code, 503)

    @mock.patch('SubfragiumDBLib.getOidsQuery')
    def testGetOidsDbFailreGetOidQuery(self, mockGet):
        mockGet.return_value = {
            'success': False,
            'err': 'DBAPI getOidsQuery() Failed: Generic Error'
        }

        res = self.app.get('/oids?target=' + target)
        self.assertEquals(res.status_code, 503)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': False,
                'err': 'getOids..() Failed: DBAPI getOidsQuery() Failed: Generic Error'
            }
        }
        self.assertEquals(resJson, resRequired)

    def testGetOidsSuccessNoParameters(self):
        TestControllerApi.addTestData(self)

        res = self.app.get('/oids')
        self.assertEquals(res.status_code, 200)

        resJson = json.loads(res.data)

        self.assertEquals(len(resJson['response']['obj']), 2)

    def testGetOidsSuccessByTarget(self):
        TestControllerApi.addTestData(self)

        res = self.app.get('/oids?target=' + target)
        self.assertEquals(res.status_code, 200)

        resJson = json.loads(res.data)

        self.assertEquals(len(resJson['response']['obj']), 1)
        self.assertEquals(resJson['response']['obj'][0]['target'], target)

    def testGetOidsSuccessByPoller(self):
        TestControllerApi.addTestData(self)

        res = self.app.get('/oids?poller=' + poller)
        self.assertEquals(res.status_code, 200)

        resJson = json.loads(res.data)

        self.assertEquals(len(resJson['response']['obj']), 1)
        self.assertEquals(resJson['response']['obj'][0]['poller'], poller)

    def testGetOidsSuccessByName(self):
        TestControllerApi.addTestData(self)

        res = self.app.get('/oids?name=' + oidData['name'])
        self.assertEquals(res.status_code, 200)

        resJson = json.loads(res.data)

        self.assertEquals(len(resJson['response']['obj']), 1)
        self.assertEquals(resJson['response']['obj'][0]['name'], oidData['name'])

    def testGetOidsSuccessByOid(self):
        TestControllerApi.addTestData(self)

        res = self.app.get('/oids?oid=' + oid)
        self.assertEquals(res.status_code, 200)

        resJson = json.loads(res.data)

        self.assertEquals(len(resJson['response']['obj']), 1)
        self.assertEquals(resJson['response']['obj'][0]['oid'], oid)

    def testGetOidsSuccessByEnabled(self):
        TestControllerApi.addTestData(self)

        res = self.app.get('/oids?enabled=' + 'True')
        self.assertEquals(res.status_code, 200)

        resJson = json.loads(res.data)

        self.assertEquals(len(resJson['response']['obj']), 1)
        self.assertEquals(resJson['response']['obj'][0]['oid'], oid)

    ############################################################
    ############################################################

    def testGetIndexInvalidMethod(self):
        res = self.app.put('/')
        self.assertEquals(res.status_code, 405)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': False,
                'err': 'Unsupported Method: 405: Method Not Allowed'
            }
        }

        self.assertEquals(resJson, resRequired)

    # Get /index: Success
    def testGetIndexSuccess(self):
        res = self.app.get('/')
        self.assertEquals(res.status_code, 200)

        resJson = json.loads(res.data)

        resRequired = {
            'response': {
                'success': True,
                'obj': {
                    'index': '/',
                    'target': '/target/<string:name>',
                    'targets': '/targets',
                    'poller': '/poller/<string:name>',
                    'pollers': '/pollers',
                    'oid': '/oid/<string:tgt>/<string:oidInfo>',
                    'oids': '/oids',
                    'static': '/static/<path:filename>'
                }
            }
        }

        self.assertEquals(resJson, resRequired)

if __name__ == '__main__':
    unittest.main()
