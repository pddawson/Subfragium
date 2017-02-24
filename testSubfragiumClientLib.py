import unittest
import mock
import SubfragiumControllerSchema
import jsonschema
import json

import SubfragiumClientLib

getApiEndpointSuccess = {
  "response": {
    "obj": {
      "index": "/",
      "oid": "/oid/<string:target>/<string:oid>",
      "oids": "/oids",
      "poller": "/poller/<string:name>",
      "pollers": "/pollers",
      "static": "/static/<path:filename>",
      "target": "/target/<string:name>",
      "targets": "/targets"
    },
    "success": 'true'
  }
}

poller1 = 'poller1'
poller1Data = {
    'snmpString': 'eur',
    'timeout': '200'
}


def validateJson(jsonSchema, jsonInput):

    try:
        jsonschema.validate(jsonInput, jsonSchema)
        return {'success': True}
    except jsonschema.ValidationError, e:
        return {'success': False, 'err': 'Invalid JSON: %s' % e}
    except jsonschema.exceptions.SchemaError, e:
        for ei in e:
            print ei
        return {'success': False, 'err': 'Invalid Json Schema: %s' % e}


class requestResponse():

    def __init__(self, text, statusCode):
        self.text = text
        self.status_code = statusCode

getApiEndPointUrls = {
    'urls': {
        "index": "/",
         "oid": "/oid/<string:target>/<string:oid>",
         "oids": "/oids",
         "poller": "/poller/<string:name>",
         "pollers": "/pollers",
         "static": "/static/<path:filename>",
         "target": "/target/<string:name>",
         "targets": "/targets"
    }
}


class TestControllerApi(unittest.TestCase):

    ##
    ## Testing Target API
    ##

    def testAddTargetHelp(self):

        results = SubfragiumClientLib.addTypeTarget('help', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('help', results)

    def testAddTargetMissingName(self):

        results = SubfragiumClientLib.addTypeTarget('', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddTargetMissingSnmpString(self):

        inputString = 'name=' + poller1
        results = SubfragiumClientLib.addTypeTarget(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddTargetMissingTimeout(self):

        inputString = 'name=' + poller1
        inputString += 'snmpString=' + poller1Data['snmpString']
        results = SubfragiumClientLib.addTypeTarget(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddTargetBadName(self):

        inputString = 'name=' + '\n'
        inputString += 'snmpString=' + poller1Data['snmpString']
        inputString += 'timeout=' + poller1Data['timeout']
        results = SubfragiumClientLib.addTypeTarget('name=\n,snmpString=eur', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddTargetSnmpString(self):

        inputString = 'name=' + poller1
        inputString += 'snmpString=' + '\n'
        inputString += 'timeout=' + poller1Data['timeout']
        results = SubfragiumClientLib.addTypeTarget('name=poller1,snmpString=\n', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddTargetTimeout(self):

        inputString = 'name=' + poller1
        inputString += 'snmpString=' + poller1Data['snmpString']
        inputString += 'timeout=' + 'abc'
        results = SubfragiumClientLib.addTypeTarget('name=poller1,snmpString=eur,timeout=abc', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.put')
    def testAddTargetSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": "True" } }', 200)
        mockRequestResponse.return_value = requestObj

        inputString = 'name=123.123.1.10,snmpString=eur,timeout=200'
        results = SubfragiumClientLib.addTypeTarget(inputString, getApiEndPointUrls)
        reqPayload = mockRequestResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PingTarget, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    def testListTargetsHelp(self):

        results = SubfragiumClientLib.listTypeTargets('help', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    @mock.patch('SubfragiumClientLib.requests.get')
    def testListTargetsSucess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": "True", "obj": [ { "name": "123.123.1.10", "snmpString": "eur", "timeout": 20 } ] } }', 200)
        mockRequestResponse.return_value = requestObj

        results = SubfragiumClientLib.listTypeTargets('all', getApiEndPointUrls)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    def testListTargetHelp(self):

        results = SubfragiumClientLib.listTypeTarget('help', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testListTargetMissingName(self):

        results = SubfragiumClientLib.listTypeTarget('', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testListTargetBadName(self):

        results = SubfragiumClientLib.listTypeTarget('name=^', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.get')
    def testListTargetSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": "True", "obj": [ { "name": "123.123.1.10", "snmpString": "eur", "timeout": 20 } ] } }', 200)
        mockRequestResponse.return_value = requestObj

        results = SubfragiumClientLib.listTypeTargets('name=123.123.1.10', getApiEndPointUrls)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    def testDeleteTargetHelp(self):

        results = SubfragiumClientLib.deleteTypeTarget('help', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testDeleteTargetMissingName(self):

        results = SubfragiumClientLib.deleteTypeTarget('', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testDeleteTargetBadname(self):

        results = SubfragiumClientLib.deleteTypeTarget('name=^', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.delete')
    def testDeleteTargetSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": true} }', 200)
        mockRequestResponse.return_value = requestObj

        results = SubfragiumClientLib.deleteTypeTarget('name=123.123.1.10', getApiEndPointUrls)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    ##
    ## Testing Poller API
    ##

    def testAddPollerHelp(self):

        results = SubfragiumClientLib.addTypePoller('help', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('help', results)

    def testAddPollerMissingName(self):

        results = SubfragiumClientLib.addTypePoller('', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingMinProcesses(self):

        inputString = 'name=poller1'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingMaxProcesses(self):

        inputString = 'name=poller1,minProcesses=1'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingNumProcesses(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingHoldTime(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,NumProcesses=1'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingCycleTime(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,NumProcesses=1,holdDown=20'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingStorageType(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=20,cycleTime=60'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingStorageLocation(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=20,cycleTime=60,storageType=graphite'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingDisabled(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingErrorThreshold(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingErrorHoldTime(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=4'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadName(self):

        inputString = 'name=abc>234,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadMinProcesses(self):

        inputString = 'name=poller1,minProcesses=a,maxProcesses=10,numProcesses=1,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadMaxProcesses(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=a,numProcesses=1,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadNumProcesses(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=a,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadHoldDown(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=a,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadCycleTime(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=2,cycleTime=a,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadStorageType(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=2,cycleTime=60,storageType=(,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadStorageLocation(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=2,cycleTime=60,storageType=graphite,storageLocation=pickle:,disabled=False,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadDisabledStatus(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=2,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=yes,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadErrorThreshold(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=2,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=a,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadErrorHoldTime(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=2,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=3,errorHoldTime=abc'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.put')
    def testAddPollerSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": "True" } }', 200)
        mockRequestResponse.return_value = requestObj

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=4,errorHoldTime=300'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        reqPayload = mockRequestResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.Poller, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    def testListPollersHelp(self):

        results = SubfragiumClientLib.listTypePollers('help', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    @mock.patch('SubfragiumClientLib.requests.get')
    def testListPollerSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": "True", "obj": [ { "cycleTime": 3, "disable": False, "errorHoldTime": 60, "errorThreshold": 10, "holdDown": 20, "maxProcesses": 10, "minProcesses": 1, "name": "poller1", "numProcesses": 1, "storageLocation": "pickle://graphite:5000", "storageType": "graphite"} ] } }', 200)
        mockRequestResponse.return_value = requestObj

        results = SubfragiumClientLib.listTypePollers('all', getApiEndPointUrls)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    def testListPollerHelp(self):

        results = SubfragiumClientLib.listTypePoller('help', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testListPollerNoName(self):

        results = SubfragiumClientLib.listTypePoller('', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testListPollerBadName(self):

        results = SubfragiumClientLib.listTypePoller('name=^', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.get')
    def testListPollerSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": "True", "obj": [ { "cycleTime": 3, "disable": false, "errorHoldTime": 60, "errorThreshold": 10, "holdDown": 20, "maxProcesses": 10, "minProcesses": 1, "name": "poller1", "numProcesses": 1, "storageLocation": "pickle://graphite:5000", "storageType": "graphite"} ] } }', 200)
        mockRequestResponse.return_value = requestObj

        results = SubfragiumClientLib.listTypePoller('name=poller1', getApiEndPointUrls)

        # Now check the function returned the correct results
        self.assertIn('success', results )
        self.assertEquals(results['success'], True)

    def testDeletePollerHelp(self):

        results = SubfragiumClientLib.deleteTypePoller('help', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testDeletePollerMissingName(self):

        results = SubfragiumClientLib.deleteTypePoller('', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testDeletePollerBadname(self):

        results = SubfragiumClientLib.deleteTypePoller('name=^', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.delete')
    def testDeletePollerSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": "True" } }', 200)
        mockRequestResponse.return_value = requestObj

        results = SubfragiumClientLib.deleteTypePoller('name=poller1', getApiEndPointUrls)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    ##
    ## Testing OID API
    ##

    def testAddOidHelp(self):

        results = SubfragiumClientLib.addTypeOid('help', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('help', results)

    def testAddOidMissingTarget(self):

        results = SubfragiumClientLib.addTypeOid('', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidMissingOid(self):

        inputString = 'target=123.123.10.1'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidMissingPoller(self):

        inputString = 'target=123.123.10.1,oid=1.3.6.1.2'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidMissingName(self):

        inputString = 'target=123.123.10.1,oid=1.3.6.1.2,poller=poller1'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidMissingEnabled(self):

        inputString = 'target=123.123.10.1,oid=1.3.6.1.2,poller=poller1,name=TestOid1'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidBadTarget(self):

        inputString = 'target=abc,oid=1.3.6.1.2,poller=poller1,name=TestOid1'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidBadOid(self):

        inputString = 'target=123.123.1.10,oid=abc,poller=poller1,name=TestOid1'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidBadPoller(self):

        inputString = 'target=123.123.1.10,oid=1.3.6.1,poller=^,name=TestOid1'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidBadName(self):

        inputString = 'target=123.123.1.10,oid=1.3.6.1,poller=poller1,name=^'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidBadEnabled(self):

        inputString = 'target=123.123.1.10,oid=1.3.6.1,poller=poller1,name=TestOid1,enabled=Yes'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.put')
    def testAddOidSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": "True" } }', 200)
        mockRequestResponse.return_value = requestObj

        inputString = 'target=123.123.1.10,oid=1.3.6.1,poller=poller1,name=TestOid1,enabled=True'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndPointUrls)
        reqPayload = mockRequestResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.Oid, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    def testListOidsHelp(self):

        results = SubfragiumClientLib.listTypeOids('help', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    @mock.patch('SubfragiumClientLib.requests.get')
    def testListOidsSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": true, "obj": [ { "enabled": true, "id": "123.123.1.10:1.3.6.1.2.1.2.2.1.10.2", "name": "network.interface.IfInOctets.router1.FastEthernet0/0", "oid": "1.3.6.1.2.1.2.2.1.10.2", "poller": "poller1", "snmpString": "eur", "target": "123.123.1.10", "timeout": 200} ] } }', 200)
        mockRequestResponse.return_value = requestObj

        results = SubfragiumClientLib.listTypeOids('', getApiEndPointUrls)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    def testListOidHelp(self):

        results = SubfragiumClientLib.listTypeOid('help', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testListOidMissingTarget(self):

        results = SubfragiumClientLib.listTypeOid('', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testListOidMissingOid(self):

        results = SubfragiumClientLib.listTypeOid('target=123.123.1.10', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.get')
    def testListOidSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": true, "obj": [ { "enabled": true, "id": "123.123.1.10:1.3.6.1.2.1.2.2.1.10.2", "name": "network.interface.IfInOctets.router1.FastEthernet0/0", "oid": "1.3.6.1.2.1.2.2.1.10.2", "poller": "poller1", "snmpString": "eur", "target": "123.123.1.10", "timeout": 200} ] } }', 200)
        mockRequestResponse.return_value = requestObj

        results = SubfragiumClientLib.listTypeOid('target=123.123.1.10,oid=1.3.6.1', getApiEndPointUrls)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    def testDeleteOidHelp(self):

        results = SubfragiumClientLib.deleteTypeOid('help', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testDeleteOidMissingTarget(self):

        results = SubfragiumClientLib.deleteTypeOid('', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testDeleteOidMissingOid(self):

        results = SubfragiumClientLib.deleteTypeOid('target=123.123.1.10', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testDeleteOidBadTarget(self):

        results = SubfragiumClientLib.deleteTypeOid('target=^,oid=1.3.6.1.2', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testDeleteOidBadOid(self):

        results = SubfragiumClientLib.deleteTypeOid('target=123.123.1.10,oid=abc', getApiEndpointSuccess)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.delete')
    def testDeleteOidSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": true } }', 200)
        mockRequestResponse.return_value = requestObj

        results = SubfragiumClientLib.deleteTypeOid('target=123.132.1.10,oid=1.3.6.1.2', getApiEndPointUrls)
        print results

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

if __name__ == '__main__':
    unittest.main()
