import unittest
import mock
import SubfragiumControllerSchema
import jsonschema
import json

import SubfragiumClientLib

getApiEndPointUrls = {
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

        results = SubfragiumClientLib.addTypeTarget('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testAddTargetMissingName(self):

        results = SubfragiumClientLib.addTypeTarget('', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddTargetMissingSnmpString(self):

        inputString = 'name=' + poller1
        results = SubfragiumClientLib.addTypeTarget(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddTargetMissingTimeout(self):

        inputString = 'name=' + poller1
        inputString += 'snmpString=' + poller1Data['snmpString']
        results = SubfragiumClientLib.addTypeTarget(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddTargetBadName(self):

        inputString = 'name=' + '\n'
        inputString += 'snmpString=' + poller1Data['snmpString']
        inputString += 'timeout=' + poller1Data['timeout']
        results = SubfragiumClientLib.addTypeTarget('name=\n,snmpString=eur', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddTargetSnmpString(self):

        inputString = 'name=' + poller1
        inputString += 'snmpString=' + '\n'
        inputString += 'timeout=' + poller1Data['timeout']
        results = SubfragiumClientLib.addTypeTarget('name=poller1,snmpString=\n', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddTargetTimeout(self):

        inputString = 'name=' + poller1
        inputString += 'snmpString=' + poller1Data['snmpString']
        inputString += 'timeout=' + 'abc'
        results = SubfragiumClientLib.addTypeTarget('name=poller1,snmpString=eur,timeout=abc', getApiEndPointUrls)
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

        results = SubfragiumClientLib.listTypeTargets('help', getApiEndPointUrls)
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

        results = SubfragiumClientLib.listTypeTarget('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testListTargetMissingName(self):

        results = SubfragiumClientLib.listTypeTarget('', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testListTargetBadName(self):

        results = SubfragiumClientLib.listTypeTarget('name=^', getApiEndPointUrls)
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

        results = SubfragiumClientLib.deleteTypeTarget('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testDeleteTargetMissingName(self):

        results = SubfragiumClientLib.deleteTypeTarget('', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testDeleteTargetBadname(self):

        results = SubfragiumClientLib.deleteTypeTarget('name=^', getApiEndPointUrls)
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

    def testModifyTargetHelp(self):

        results = SubfragiumClientLib.modifyTypeTarget('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testModifyTargetMissingAttribute(self):

        results = SubfragiumClientLib.modifyTypeTarget('', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testModifyTargetBadName(self):

        results = SubfragiumClientLib.modifyTypeTarget('name=^', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testModifyTargetBadSnmpString(self):

        results = SubfragiumClientLib.modifyTypeTarget('name=123.123.1.10,snmpString=^', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testModifyTargetBadTimeout(self):

        results = SubfragiumClientLib.modifyTypeTarget('name=123.123.1.10,timeout=abc', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    @mock.patch( 'SubfragiumClientLib.requests.put' )
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyTargetSnmpStringSuccess(self, mockRequestGetResponse, mochRequestPutResponse):

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "name": "123.123.1.10", "snmpString": "eur", "timeout": 20 } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        results = SubfragiumClientLib.modifyTypeTarget('name=123.123.1.10,snmpString=abc', getApiEndPointUrls )
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PingTarget, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    @mock.patch( 'SubfragiumClientLib.requests.put' )
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyTargetTimeoutSuccess(self, mockRequestGetResponse, mochRequestPutResponse):

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "name": "123.123.1.10", "snmpString": "eur", "timeout": 20 } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        results = SubfragiumClientLib.modifyTypeTarget('name=123.123.1.10,timeout=123', getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PingTarget, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    ##
    ## Testing Poller API
    ##

    def testAddPollerHelp(self):

        results = SubfragiumClientLib.addTypePoller('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testAddPollerMissingName(self):

        results = SubfragiumClientLib.addTypePoller('', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingMinProcesses(self):

        inputString = 'name=poller1'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingMaxProcesses(self):

        inputString = 'name=poller1,minProcesses=1'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingNumProcesses(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingHoldTime(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,NumProcesses=1'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingCycleTime(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,NumProcesses=1,holdDown=20'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingStorageType(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=20,cycleTime=60'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingStorageLocation(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=20,cycleTime=60,storageType=graphite'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingDisabled(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingErrorThreshold(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerMissingErrorHoldTime(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=4'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadName(self):

        inputString = 'name=abc>234,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadMinProcesses(self):

        inputString = 'name=poller1,minProcesses=a,maxProcesses=10,numProcesses=1,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadMaxProcesses(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=a,numProcesses=1,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadNumProcesses(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=a,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadHoldDown(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=a,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadCycleTime(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=2,cycleTime=a,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadStorageType(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=2,cycleTime=60,storageType=(,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadStorageLocation(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=2,cycleTime=60,storageType=graphite,storageLocation=pickle:,disabled=False,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadDisabledStatus(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=2,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=yes,errorThreshold=4,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadErrorThreshold(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=2,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=a,errorHoldTime=1800'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddPollerBadErrorHoldTime(self):

        inputString = 'name=poller1,minProcesses=1,maxProcesses=10,numProcesses=1,holdDown=2,cycleTime=60,storageType=graphite,storageLocation=pickle://123.123.1.10:5000,disabled=False,errorThreshold=3,errorHoldTime=abc'
        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
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

        results = SubfragiumClientLib.listTypePollers('help', getApiEndPointUrls)
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

        results = SubfragiumClientLib.listTypePoller('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testListPollerNoName(self):

        results = SubfragiumClientLib.listTypePoller('', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testListPollerBadName(self):

        results = SubfragiumClientLib.listTypePoller('name=^', getApiEndPointUrls)
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

        results = SubfragiumClientLib.deleteTypePoller('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testDeletePollerMissingName(self):

        results = SubfragiumClientLib.deleteTypePoller('', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testDeletePollerBadname(self):

        results = SubfragiumClientLib.deleteTypePoller('name=^', getApiEndPointUrls)
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

    def testModifyPollerHelp(self):

        results = SubfragiumClientLib.modifyTypePoller('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testModifyPollerMissingName(self):

        results = SubfragiumClientLib.modifyTypePoller('', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testModifyPollerBadInput(self):

        inputStrings = [
            'name=^',
            'name=poller1,minProcesses=abc',
            'name=poller1,maxProcesses=abc',
            'name=poller1,numProcesses=abc',
            'name=poller1,holdDown=abc',
            'name=poller1,cycleTime=abc',
            'name=poller1,storageType=^',
            'name=poller1,storageLocation=^',
            'name=poller1,disabled=true',
            'name=poller1,errorThreshold=abc',
            'name=poller1,errorHoldTime=abc',
        ]

        for inputString in inputStrings:
            results = SubfragiumClientLib.modifyTypePoller(inputString, getApiEndPointUrls)
            self.assertIn('success', results, 'Failed with string' + inputString)
            self.assertEquals(results['success'], False)
            self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.put')
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyPollerModifyMinProcessSuccess(self, mockRequestGetResponse, mochRequestPutResponse):

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "name": "poller1", "minProcesses": 1, "maxProcesses": 10, "numProcesses": 1, "cycleTime": 60, "holdDown": 20, "storageType": "graphite", "storageLocation": "pickle://graphite:5000", "disabled": false, "errorThreshold": 5, "errorHoldTime": 1800 } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        results = SubfragiumClientLib.modifyTypePoller('name=poller1,minProcesses=2', getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.Poller, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    @mock.patch('SubfragiumClientLib.requests.put')
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyPollerModifyMaxProcessesSuccess(self, mockRequestGetResponse, mochRequestPutResponse):

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "name": "poller1", "minProcesses": 1, "maxProcesses": 10, "numProcesses": 1, "cycleTime": 60, "holdDown": 20, "storageType": "graphite", "storageLocation": "pickle://graphite:5000", "disabled": false, "errorThreshold": 5, "errorHoldTime": 1800 } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        results = SubfragiumClientLib.modifyTypePoller('name=poller1,maxProcesses=2', getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.Poller, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    @mock.patch('SubfragiumClientLib.requests.put')
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyPollerModifyNumProcessesSuccess(self, mockRequestGetResponse, mochRequestPutResponse):

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "name": "poller1", "minProcesses": 1, "maxProcesses": 10, "numProcesses": 1, "cycleTime": 60, "holdDown": 20, "storageType": "graphite", "storageLocation": "pickle://graphite:5000", "disabled": false, "errorThreshold": 5, "errorHoldTime": 1800 } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        results = SubfragiumClientLib.modifyTypePoller('name=poller1,numProcesses=2', getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.Poller, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    @mock.patch('SubfragiumClientLib.requests.put')
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyPollerModifyHoldDownSuccess(self, mockRequestGetResponse, mochRequestPutResponse):

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "name": "poller1", "minProcesses": 1, "maxProcesses": 10, "numProcesses": 1, "cycleTime": 60, "holdDown": 20, "storageType": "graphite", "storageLocation": "pickle://graphite:5000", "disabled": false, "errorThreshold": 5, "errorHoldTime": 1800 } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        results = SubfragiumClientLib.modifyTypePoller('name=poller1,numProcesses=5', getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.Poller, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    @mock.patch('SubfragiumClientLib.requests.put')
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyPollerModifyCycleTimeSuccess(self, mockRequestGetResponse, mochRequestPutResponse):

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "name": "poller1", "minProcesses": 1, "maxProcesses": 10, "numProcesses": 1, "cycleTime": 60, "holdDown": 20, "storageType": "graphite", "storageLocation": "pickle://graphite:5000", "disabled": false, "errorThreshold": 5, "errorHoldTime": 1800 } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        results = SubfragiumClientLib.modifyTypePoller('name=poller1,cycleTime=30', getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.Poller, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    @mock.patch('SubfragiumClientLib.requests.put')
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyPollerModifyStorageTypeSuccess(self, mockRequestGetResponse, mochRequestPutResponse):

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "name": "poller1", "minProcesses": 1, "maxProcesses": 10, "numProcesses": 1, "cycleTime": 60, "holdDown": 20, "storageType": "graphite", "storageLocation": "pickle://graphite:5000", "disabled": false, "errorThreshold": 5, "errorHoldTime": 1800 } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        results = SubfragiumClientLib.modifyTypePoller('name=poller1,storageType=graphite', getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.Poller, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    @mock.patch('SubfragiumClientLib.requests.put')
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyPollerModifyStorageLocationSuccess(self, mockRequestGetResponse, mochRequestPutResponse):

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "name": "poller1", "minProcesses": 1, "maxProcesses": 10, "numProcesses": 1, "cycleTime": 60, "holdDown": 20, "storageType": "graphite", "storageLocation": "pickle://graphite:5000", "disabled": false, "errorThreshold": 5, "errorHoldTime": 1800 } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        results = SubfragiumClientLib.modifyTypePoller('name=poller1,storageLocation=pickle://graphite2:5001', getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.Poller, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    @mock.patch('SubfragiumClientLib.requests.put')
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyPollerModifyDisabledSuccess(self, mockRequestGetResponse, mochRequestPutResponse):

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "name": "poller1", "minProcesses": 1, "maxProcesses": 10, "numProcesses": 1, "cycleTime": 60, "holdDown": 20, "storageType": "graphite", "storageLocation": "pickle://graphite:5000", "disabled": false, "errorThreshold": 5, "errorHoldTime": 1800 } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        results = SubfragiumClientLib.modifyTypePoller('name=poller1,disabled=True', getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.Poller, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    @mock.patch('SubfragiumClientLib.requests.put')
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyPollerModifyErrorThresholdSuccess(self, mockRequestGetResponse, mochRequestPutResponse):

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "name": "poller1", "minProcesses": 1, "maxProcesses": 10, "numProcesses": 1, "cycleTime": 60, "holdDown": 20, "storageType": "graphite", "storageLocation": "pickle://graphite:5000", "disabled": false, "errorThreshold": 5, "errorHoldTime": 1800 } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        results = SubfragiumClientLib.modifyTypePoller('name=poller1,errorThreshold=10', getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.Poller, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    @mock.patch('SubfragiumClientLib.requests.put')
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyPollerModifyErrorHoldTimeSuccess(self, mockRequestGetResponse, mochRequestPutResponse):

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "name": "poller1", "minProcesses": 1, "maxProcesses": 10, "numProcesses": 1, "cycleTime": 60, "holdDown": 20, "storageType": "graphite", "storageLocation": "pickle://graphite:5000", "disabled": false, "errorThreshold": 5, "errorHoldTime": 1800 } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        results = SubfragiumClientLib.modifyTypePoller('name=poller1,errorHoldTime=1800', getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.Poller, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    ##
    ## Testing OID API
    ##

    def testAddOidHelp(self):

        results = SubfragiumClientLib.addTypeOid('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testAddOidMissingTarget(self):

        results = SubfragiumClientLib.addTypeOid('', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidMissingOid(self):

        inputString = 'target=123.123.10.1'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidMissingPoller(self):

        inputString = 'target=123.123.10.1,oid=1.3.6.1.2'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidMissingName(self):

        inputString = 'target=123.123.10.1,oid=1.3.6.1.2,poller=poller1'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidMissingEnabled(self):

        inputString = 'target=123.123.10.1,oid=1.3.6.1.2,poller=poller1,name=TestOid1'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidBadTarget(self):

        inputString = 'target=abc,oid=1.3.6.1.2,poller=poller1,name=TestOid1'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidBadOid(self):

        inputString = 'target=123.123.1.10,oid=abc,poller=poller1,name=TestOid1'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidBadPoller(self):

        inputString = 'target=123.123.1.10,oid=1.3.6.1,poller=^,name=TestOid1'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidBadName(self):

        inputString = 'target=123.123.1.10,oid=1.3.6.1,poller=poller1,name=^'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testAddOidBadEnabled(self):

        inputString = 'target=123.123.1.10,oid=1.3.6.1,poller=poller1,name=TestOid1,enabled=Yes'
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndPointUrls)
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

        results = SubfragiumClientLib.listTypeOids('help', getApiEndPointUrls)
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

        results = SubfragiumClientLib.listTypeOid('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testListOidMissingTarget(self):

        results = SubfragiumClientLib.listTypeOid('', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testListOidMissingOid(self):

        results = SubfragiumClientLib.listTypeOid('target=123.123.1.10', getApiEndPointUrls)
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

        results = SubfragiumClientLib.deleteTypeOid('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testDeleteOidMissingTarget(self):

        results = SubfragiumClientLib.deleteTypeOid('', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testDeleteOidMissingOid(self):

        results = SubfragiumClientLib.deleteTypeOid('target=123.123.1.10', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testDeleteOidBadTarget(self):

        results = SubfragiumClientLib.deleteTypeOid('target=^,oid=1.3.6.1.2', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    def testDeleteOidBadOid(self):

        results = SubfragiumClientLib.deleteTypeOid('target=123.123.1.10,oid=abc', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], False)
        self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.delete')
    def testDeleteOidSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": true } }', 200)
        mockRequestResponse.return_value = requestObj

        results = SubfragiumClientLib.deleteTypeOid('target=123.132.1.10,oid=1.3.6.1.2', getApiEndPointUrls)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    def testModifyOidHelp(self):

        results = SubfragiumClientLib.listTypeOid('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testModifyOidBadParameter(self):

        inputStrings = [
            '',
            'target=123.123.1.10',
            'target=123.123.1.10,oid=1.3.6.1.2',
            'target=123.123.1.10,oid=1.3.6.1.2,poller=^',
            'target=123.123.1.10,oid=1.3.6.1.2,name=^',
            'target=123.123.1.10,oid=1.3.6.1.2,enabled=false'
        ]

        for inputString in inputStrings:
            results = SubfragiumClientLib.modifyTypeOid(inputString, getApiEndPointUrls)
            self.assertIn('success', results, 'Failed for input string ' + inputString)
            self.assertEquals(results['success'], False)
            self.assertIn('err', results, 'Failed for input string ' + inputString)


    @mock.patch('SubfragiumClientLib.requests.put')
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyOidModifyPollerSuccessfully(self, mockRequestGetResponse, mochRequestPutResponse):

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "enabled": true, "id": "123.123.1.10:1.3.6.1.2.1.2.2.1.10.2", "name": "network.interface.IfInOctets.router1.FastEthernet0/0", "oid": "1.3.6.1.2.1.2.2.1.10.2", "poller": "poller1", "snmpString": "eur", "target": "123.123.1.10" } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        results = SubfragiumClientLib.modifyTypeOid('target=123.123.1.10,oid=1.3.6.1.2,poller=poller2', getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.Oid, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    @mock.patch('SubfragiumClientLib.requests.put')
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyOidModifyNameSuccessfully(self, mockRequestGetResponse, mochRequestPutResponse):

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "enabled": true, "id": "123.123.1.10:1.3.6.1.2.1.2.2.1.10.2", "name": "network.interface.IfInOctets.router1.FastEthernet0/0", "oid": "1.3.6.1.2.1.2.2.1.10.2", "poller": "poller1", "snmpString": "eur", "target": "123.123.1.10" } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        results = SubfragiumClientLib.modifyTypeOid('target=123.123.1.10,oid=1.3.6.1.2,name=test2', getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.Oid, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    @mock.patch('SubfragiumClientLib.requests.put')
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyOidModifyEnabledSuccessfully(self, mockRequestGetResponse, mochRequestPutResponse):

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "enabled": true, "id": "123.123.1.10:1.3.6.1.2.1.2.2.1.10.2", "name": "network.interface.IfInOctets.router1.FastEthernet0/0", "oid": "1.3.6.1.2.1.2.2.1.10.2", "poller": "poller1", "snmpString": "eur", "target": "123.123.1.10" } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        results = SubfragiumClientLib.modifyTypeOid('target=123.123.1.10,oid=1.3.6.1.2,enabled=False', getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.Oid, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

if __name__ == '__main__':
    unittest.main()
