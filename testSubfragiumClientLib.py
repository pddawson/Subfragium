import unittest
import mock
import SubfragiumControllerSchema
import jsonschema
import json

import SubfragiumClientLib

getApiEndPointUrls = {
    "urls": {
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

target1 = '123.123.1.10'
target1Data = {
    'snmpString': 'eur',
    'timeout': '200'
}

poller1 = 'poller1'
poller1Data = {
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

oid1 = '1.3.6.1.2.1'
oid1Data = {
    'poller': 'poller1',
    'name': 'network.interface.ifInHcOctets.GigabitEthernet0/0',
    'enabled': True
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


class requestResponse:

    def __init__(self, text, statusCode):
        self.text = text
        self.status_code = statusCode


class TestControllerApi(unittest.TestCase):

    ##
    ## Testing response validation function
    ##

    def testValidateResponseNothing(self):

        results = SubfragiumClientLib.validateResponse('', False)
        self.assertEquals(results['success'], False)
        self.assertEquals(results['err'], 'Error: No text in response')

    def testValidateResponseNoResponseField(self):

        res = requestResponse('{}', 404)
        results = SubfragiumClientLib.validateResponse(res, False)
        self.assertEquals(results['success'], False)
        self.assertEquals(results['err'], 'Error: Unknown response - {}')

    def testValidateResponseNoSuccessField(self):

        res = requestResponse('{"response":{}}', 404)
        results = SubfragiumClientLib.validateResponse(res, False)
        self.assertEquals(results['success'], False)
        self.assertEquals(results['err'], 'Error: Missing success/err field - {u\'response\': {}}')

    def testValidateResponseSuccessResponse(self):

        responseText = '{"success": true}'
        validOutputJson = validateJson(SubfragiumControllerSchema.PutDeleteOutput, json.loads(responseText))
        self.assertEquals(validOutputJson['success'], True)

        res = requestResponse('{"response":' + responseText + '}', 400)
        results = SubfragiumClientLib.validateResponse(res, False)
        self.assertEquals(results['success'], True)

    def testValidateResponseBadErrorResponse(self):

        res = requestResponse('{"response":{"abc": "abc"}}', 404)
        results = SubfragiumClientLib.validateResponse(res, False)
        self.assertEquals(results['success'], False)
        self.assertEquals(results['err'], 'Error: Missing success/err field - {u\'response\': {u\'abc\': u\'abc\'}}')

    def testValidateResponseGoodErrorResponse(self):

        requestText = '{"err": "abc"}'
        validOutputJson = validateJson(SubfragiumControllerSchema.PutDeleteOutput, json.loads(requestText))
        self.assertEquals(validOutputJson['success'], True)

        res = requestResponse('{"response":' + requestText + '}', 404)
        results = SubfragiumClientLib.validateResponse(res, False)
        self.assertEquals(results['success'], False)
        self.assertEquals(results['err'], 'abc')

    def testValidateResponseGoodGetResponse(self):

        requestText = '{"success": true, "obj": { "name": "123.123.1.1", "snmpString": "eur", "timeout": 200}}'
        validOutputJson = validateJson( SubfragiumControllerSchema.GetTargetOutput, json.loads(requestText))
        self.assertEquals(validOutputJson['success'], True)

        res = requestResponse('{"response":' + requestText + '}', 200)
        results = SubfragiumClientLib.validateResponse(res, True)
        self.assertEquals(results['success'], True)
        self.assertIn('obj', results)

    ##
    ## Testing Target API
    ##

    def testAddTargetHelp(self):

        results = SubfragiumClientLib.addTypeTarget('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testAddTargetBadInput(self):

        inputStrings = [
            '',
            'name=^',
            'name=' + target1,
            'name=' + target1 + 'snmpString=^',
            'name=' + target1 + 'snmpString=' + target1Data['snmpString'],
            'name=' + target1 + 'snmpString=' + target1Data['snmpString'] + 'timeout=abc'
        ]

        for inputString in inputStrings:
            results = SubfragiumClientLib.addTypeTarget(inputString, getApiEndPointUrls)
            self.assertIn('success', results)
            self.assertEquals(results['success'], False)
            self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.put')
    def testAddTargetSuccess(self, mockRequestResponse):

        # Create response text
        responseText = '{"success": true }'
        # Validate response text fits schema
        validOutputJson = validateJson(SubfragiumControllerSchema.PutDeleteOutput, json.loads(responseText))
        self.assertEquals(validOutputJson['success'], True)

        # Build response object
        requestObj = requestResponse('{"response":' + responseText + '}', 200)
        mockRequestResponse.return_value = requestObj

        # Build input string and test
        inputString = 'name=' + target1 + ',snmpString=' + target1Data['snmpString'] + ',timeout=' + target1Data['timeout']
        results = SubfragiumClientLib.addTypeTarget(inputString, getApiEndPointUrls)
        reqPayload = mockRequestResponse.call_args[1]['data']

        # Check the response fits the output
        validInputJson = validateJson(SubfragiumControllerSchema.PutTargetInput, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validInputJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    def testListTargetsHelp(self):

        results = SubfragiumClientLib.listTypeTargets('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    @mock.patch('SubfragiumClientLib.requests.get')
    def testListTargetsSuccess(self, mockRequestResponse):

        responseText = '{"success": true, "obj": [ { "name": "123.123.1.10", "snmpString": "eur", "timeout": 20 } ] }'
        validOutputJson = validateJson(SubfragiumControllerSchema.GetTargetsOutput, json.loads(responseText))
        self.assertEquals(validOutputJson['success'], True)

        requestObj = requestResponse('{"response": ' + responseText + '}', 200)
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

    def testListTargetBadInput(self):

        inputStrings = [
            '',
            'name=^'
        ]

        for inputString in inputStrings:
            results = SubfragiumClientLib.listTypeTarget(inputString, getApiEndPointUrls)
            self.assertIn('success', results)
            self.assertEquals(results['success'], False)
            self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.get')
    def testListTargetSuccess(self, mockRequestResponse):

        responseText = '{"success": true, "obj": { "name": "123.123.1.10", "snmpString": "eur", "timeout": 20 } }'
        validOutputJson = validateJson(SubfragiumControllerSchema.GetTargetOutput, json.loads(responseText))
        self.assertEquals(validOutputJson['success'], True)

        requestObj = requestResponse('{"response": ' + responseText + '}', 200)
        mockRequestResponse.return_value = requestObj

        inputString = 'name=' + target1
        results = SubfragiumClientLib.listTypeTargets(inputString, getApiEndPointUrls)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    def testDeleteTargetHelp(self):

        results = SubfragiumClientLib.deleteTypeTarget('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testListTargetBadInput(self):

        inputStrings = [
            '',
            'name=^'
        ]

        for inputString in inputStrings:
            results = SubfragiumClientLib.deleteTypeTarget(inputString, getApiEndPointUrls)
            self.assertIn('success', results)
            self.assertEquals(results['success'], False)
            self.assertIn('err', results)


    @mock.patch('SubfragiumClientLib.requests.delete')
    def testDeleteTargetSuccess(self, mockRequestResponse):

        responseText = '{"success": true}'
        validOutputJson = validateJson(SubfragiumControllerSchema.PutDeleteOutput, json.loads(responseText))
        self.assertEquals(validOutputJson['success'], True)

        requestObj = requestResponse('{"response": ' + responseText + ' }', 200)
        mockRequestResponse.return_value = requestObj

        inputString = 'name=' + target1
        results = SubfragiumClientLib.deleteTypeTarget(inputString, getApiEndPointUrls)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    def testModifyTargetHelp(self):

        results = SubfragiumClientLib.modifyTypeTarget('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testModifyTargetBadInput(self):

        inputStrings = [
            '',
            'name=^',
            'name=' + target1,
            'name=' + target1 + 'snmpString=^'
            'name=' + target1 + 'timeout=abc'

        ]

        for inputString in inputStrings:
            results = SubfragiumClientLib.modifyTypeTarget(inputString, getApiEndPointUrls)
            self.assertIn('success', results)
            self.assertEquals(results['success'], False)
            self.assertIn('err', results)

    @mock.patch( 'SubfragiumClientLib.requests.put' )
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyTargetSnmpStringSuccess(self, mockRequestGetResponse, mochRequestPutResponse):

        getResponseText = '{"success": true, "obj": { "name": "123.123.1.10", "snmpString": "eur", "timeout": 20 } }'
        validOutputJson = validateJson(SubfragiumControllerSchema.GetTargetOutput, json.loads(getResponseText))
        self.assertEquals(validOutputJson['success'], True)

        getRequestObj = requestResponse('{"response": ' + getResponseText + ' }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putResponseText = '{"success": true}'
        validOutputJson = validateJson(SubfragiumControllerSchema.PutDeleteOutput, json.loads(putResponseText))
        self.assertEquals(validOutputJson['success'], True)

        putRequestObj = requestResponse('{"response": ' + putResponseText + ' }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        inputString = 'name=' + target1 + ',snmpString=' + target1Data['snmpString']
        results = SubfragiumClientLib.modifyTypeTarget(inputString, getApiEndPointUrls )
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PutTargetInput, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    @mock.patch( 'SubfragiumClientLib.requests.put' )
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyTargetTimeoutSuccess(self, mockRequestGetResponse, mochRequestPutResponse):

        getResponseText = '{"success": true, "obj": { "name": "123.123.1.10", "snmpString": "eur", "timeout": 20 } }'
        validOutputJson = validateJson(SubfragiumControllerSchema.GetTargetOutput, json.loads(getResponseText))
        self.assertEquals(validOutputJson['success'], True)

        getRequestObj = requestResponse('{"response": ' + getResponseText + '}', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putResponseText = '{"success": true}'
        validOutputJson = validateJson(SubfragiumControllerSchema.PutDeleteOutput, json.loads(putResponseText))
        self.assertEquals(validOutputJson['success'], True)

        putRequestObj = requestResponse('{"response": ' + putResponseText + '}', 200)
        mochRequestPutResponse.return_value = putRequestObj

        inputString = 'name=' + target1 + ',timeout=' + target1Data['timeout']
        results = SubfragiumClientLib.modifyTypeTarget(inputString, getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PutTargetInput, json.loads(reqPayload))

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

    def testAddPollerBadInput(self):

        inputStrings = [
            '',
            'name=^',
            'name=' + poller1,
            'name=' + poller1 +
            ',minProcesses=abc',

            'name=' + poller1 +
            ',minProcesses=' + str(poller1Data['minProcesses']),

            'name=' + poller1 +
            ',minProcesses=' + str(poller1Data['minProcesses']) +
            ',maxProcesses=' + str(poller1Data['maxProcesses']),

            'name=' + poller1 +
            ',minProcesses=' + str(poller1Data['minProcesses']) +
            ',maxProcesses=abc',

            'name=' + poller1 +
            ',minProcesses=' + str(poller1Data['minProcesses']) +
            ',maxProcesses=' + str(poller1Data['maxProcesses']) +
            ',numProcesses=abc',

            'name=' + poller1 +
            ',minProcesses=' + str(poller1Data['minProcesses']) +
            ',maxProcesses=' + str(poller1Data['maxProcesses']) +
            ',numProcesses=' + str(poller1Data['numProcesses']),

            'name=' + poller1 +
            ',minProcesses=' + str( poller1Data[ 'minProcesses' ] ) +
            ',maxProcesses=' + str( poller1Data[ 'maxProcesses' ] ) +
            ',numProcesses=' + str( poller1Data[ 'numProcesses' ] ) +
            ',holdDown=abc',

            'name=' + poller1 +
            ',minProcesses=' + str( poller1Data[ 'minProcesses' ] ) +
            ',maxProcesses=' + str( poller1Data[ 'maxProcesses' ] ) +
            ',numProcesses=' + str( poller1Data[ 'numProcesses' ] ) +
            ',holdDown='  + str( poller1Data[ 'holdDown' ] ),

            'name=' + poller1 +
            ',minProcesses=' + str( poller1Data[ 'minProcesses' ] ) +
            ',maxProcesses=' + str( poller1Data[ 'maxProcesses' ] ) +
            ',numProcesses=' + str( poller1Data[ 'numProcesses' ] ) +
            ',h,ldDown=' + str( poller1Data[ 'holdDown' ] ) +
            ',cycleTime=abc',

            'name=' + poller1 +
            ',minProcesses=' + str( poller1Data[ 'minProcesses' ] ) +
            ',maxProcesses=' + str( poller1Data[ 'maxProcesses' ] ) +
            ',numProcesses=' + str( poller1Data[ 'numProcesses' ] ) +
            ',holdDown=' + str( poller1Data[ 'holdDown' ] ) +
            ',cycleTime=' + str( poller1Data[ 'cycleTime' ] ),

            'name=' + poller1 +
            ',minProcesses=' + str( poller1Data[ 'minProcesses' ] ) +
            ',maxProcesses=' + str( poller1Data[ 'maxProcesses' ] ) +
            ',numProcesses=' + str( poller1Data[ 'numProcesses' ] ) +
            ',holdDown=' + str( poller1Data[ 'holdDown' ] ) +
            ',cycleTime=' + str( poller1Data[ 'cycleTime' ] ) +
            ',storageType=^',

            'name=' + poller1 +
            ',minProcesses=' + str( poller1Data[ 'minProcesses' ] ) +
            ',maxProcesses=' + str( poller1Data[ 'maxProcesses' ] ) +
            ',numProcesses=' + str( poller1Data[ 'numProcesses' ] ) +
            ',holdDown=' + str( poller1Data[ 'holdDown' ] ) +
            ',cycleTime=' + str( poller1Data[ 'cycleTime' ] ) +
            ',storageType=' + str( poller1Data[ 'storageType' ] ),

            'name=' + poller1 +
            ',minProcesses=' + str( poller1Data[ 'minProcesses' ] ) +
            ',maxProcesses=' + str( poller1Data[ 'maxProcesses' ] ) +
            ',numProcesses=' + str( poller1Data[ 'numProcesses' ] ) +
            ',holdDown=' + str( poller1Data[ 'holdDown' ] ) +
            ',cycleTime=' + str( poller1Data[ 'cycleTime' ] ) +
            ',storageType=' + str( poller1Data[ 'storageType' ] ) +
            ',storageLocation=^',

            'name=' + poller1 +
            ',minProcesses=' + str( poller1Data[ 'minProcesses' ] ) +
            ',maxProcesses=' + str( poller1Data[ 'maxProcesses' ] ) +
            ',numProcesses=' + str( poller1Data[ 'numProcesses' ] ) +
            ',holdDown=' + str( poller1Data[ 'holdDown' ] ) +
            ',cycleTime=' + str( poller1Data[ 'cycleTime' ] ) +
            ',storageType=' + str( poller1Data[ 'storageType' ] ) +
            ',storageLocation=' + str( poller1Data[ 'storageLocation' ] ),

            'name=' + poller1 +
            ',minProcesses=' + str( poller1Data[ 'minProcesses' ] ) +
            ',maxProcesses=' + str( poller1Data[ 'maxProcesses' ] ) +
            ',numProcesses=' + str( poller1Data[ 'numProcesses' ] ) +
            ',holdDown=' + str( poller1Data[ 'holdDown' ] ) +
            ',cycleTime=' + str( poller1Data[ 'cycleTime' ] ) +
            ',storageType=' + str( poller1Data[ 'storageType' ] ) +
            ',storageType=' + str( poller1Data[ 'storageType' ] ) +
            ',disabled=abc',

            'name=' + poller1 +
            ',minProcesses=' + str( poller1Data[ 'minProcesses' ] ) +
            ',maxProcesses=' + str( poller1Data[ 'maxProcesses' ] ) +
            ',numProcesses=' + str( poller1Data[ 'numProcesses' ] ) +
            ',holdDown=' + str( poller1Data[ 'holdDown' ] ) +
            ',cycleTime=' + str( poller1Data[ 'cycleTime' ] ) +
            ',storageType=' + poller1Data['storageType'] +
            ',storageType=' + poller1Data['storageType'] +
            ',disabled=' + str(poller1Data[ 'disabled']),

            'name=' + poller1 +
            ',minProcesses=' + str( poller1Data[ 'minProcesses' ] ) +
            ',maxProcesses=' + str( poller1Data[ 'maxProcesses' ] ) +
            ',numProcesses=' + str( poller1Data[ 'numProcesses' ] ) +
            ',holdDown=' + str( poller1Data[ 'holdDown' ] ) +
            ',cycleTime=' + str( poller1Data[ 'cycleTime' ] ) +
            ',storageType=' + poller1Data[ 'storageType' ] +
            ',storageType=' + poller1Data[ 'storageType' ] +
            ',disabled=' + str( poller1Data[ 'disabled' ] ) +
            ',errorThreshold=abc',

            'name=' + poller1 +
            ',minProcesses=' + str( poller1Data[ 'minProcesses' ] ) +
            ',maxProcesses=' + str( poller1Data[ 'maxProcesses' ] ) +
            ',numProcesses=' + str( poller1Data[ 'numProcesses' ] ) +
            ',holdDown=' + str( poller1Data[ 'holdDown' ] ) +
            ',cycleTime=' + str( poller1Data[ 'cycleTime' ] ) +
            ',storageType=' + poller1Data[ 'storageType' ] +
            ',storageType=' + poller1Data[ 'storageType' ] +
            ',disabled=' + str( poller1Data[ 'disabled' ] ) +
            ',errorThreshold=' + str( poller1Data[ 'errorThreshold' ] ),

            'name=' + poller1 +
            ',minProcesses=' + str( poller1Data[ 'minProcesses' ] ) +
            ',maxProcesses=' + str( poller1Data[ 'maxProcesses' ] ) +
            ',numProcesses=' + str( poller1Data[ 'numProcesses' ] ) +
            ',holdDown=' + str( poller1Data[ 'holdDown' ] ) +
            ',cycleTime=' + str( poller1Data[ 'cycleTime' ] ) +
            ',storageType=' + poller1Data[ 'storageType' ] +
            ',storageType=' + poller1Data[ 'storageType' ] +
            ',disabled=' + str( poller1Data[ 'disabled' ] ) +
            ',errorThreshold=' + str( poller1Data[ 'errorThreshold' ] ) +
            ',errorHoldDown=abc'
        ]

        for inputString in inputStrings:
            results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
            self.assertIn('success', results)
            self.assertEquals(results['success'], False)
            self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.put')
    def testAddPollerSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": "True" } }', 200)
        mockRequestResponse.return_value = requestObj

        inputString = 'name=' + poller1 + \
                      ',minProcesses=' + str(poller1Data['minProcesses']) + \
                      ',maxProcesses=' + str(poller1Data['maxProcesses']) + \
                      ',numProcesses=' + str(poller1Data['numProcesses']) + \
                      ',holdDown=' + str(poller1Data['holdDown']) + \
                      ',cycleTime=' + str(poller1Data['cycleTime']) + \
                      ',storageType=' + poller1Data['storageType'] + \
                      ',storageLocation=' + poller1Data['storageLocation'] + \
                      ',disabled=' + str(poller1Data['disabled']) + \
                      ',errorThreshold=' + str(poller1Data['errorThreshold']) + \
                      ',errorHoldTime=' + str(poller1Data['errorHoldTime'])

        results = SubfragiumClientLib.addTypePoller(inputString, getApiEndPointUrls)
        reqPayload = mockRequestResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PutPollerInput, json.loads(reqPayload))

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

    def testListPollerBadInput(self):

        inputStrings = [
            '',
            'name=^',
        ]

        for inputstring in inputStrings:
            results = SubfragiumClientLib.listTypePoller(inputstring, getApiEndPointUrls)
            self.assertIn('success', results)
            self.assertEquals(results['success'], False)
            self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.get')
    def testListPollerSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": "True", "obj": [ { "cycleTime": 3, "disable": false, "errorHoldTime": 60, "errorThreshold": 10, "holdDown": 20, "maxProcesses": 10, "minProcesses": 1, "name": "poller1", "numProcesses": 1, "storageLocation": "pickle://graphite:5000", "storageType": "graphite"} ] } }', 200)
        mockRequestResponse.return_value = requestObj

        inputString = 'name=' + poller1
        results = SubfragiumClientLib.listTypePoller(inputString, getApiEndPointUrls)

        # Now check the function returned the correct results
        self.assertIn('success', results )
        self.assertEquals(results['success'], True)

    def testDeletePollerHelp(self):

        results = SubfragiumClientLib.deleteTypePoller('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testDeletePollerBadInput(self):

        inputStrings = [
            '',
            'name=^'
        ]

        for inputString in inputStrings:
            results = SubfragiumClientLib.deleteTypePoller(inputString, getApiEndPointUrls)
            self.assertIn('success', results)
            self.assertEquals(results['success'], False)
            self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.delete')
    def testDeletePollerSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": "True" } }', 200)
        mockRequestResponse.return_value = requestObj

        inputString = 'name=' + poller1
        results = SubfragiumClientLib.deleteTypePoller(inputString, getApiEndPointUrls)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    def testModifyPollerHelp(self):

        results = SubfragiumClientLib.modifyTypePoller('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testModifyPollerBadInput(self):

        inputStrings = [
            '',
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

        inputString = 'name=' + poller1 + ',minProcesses=' + str(poller1Data['minProcesses'])
        results = SubfragiumClientLib.modifyTypePoller(inputString, getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PutPollerInput, json.loads(reqPayload))

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

        inputString = 'name=' + poller1 + ',maxProcesses=' + str(poller1Data['maxProcesses'])
        results = SubfragiumClientLib.modifyTypePoller(inputString, getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PutPollerInput, json.loads(reqPayload))

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

        inputString = 'name=' + poller1 + ',numProcesses=' + str(poller1Data['numProcesses'])
        results = SubfragiumClientLib.modifyTypePoller(inputString, getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PutPollerInput, json.loads(reqPayload))

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

        inputString = 'name=' + poller1 + ',holdDown=' + str(poller1Data['holdDown'])
        results = SubfragiumClientLib.modifyTypePoller(inputString, getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PutPollerInput, json.loads(reqPayload))

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

        inputString = 'name=' + poller1 + ',cycleTime=' + str(poller1Data['cycleTime'])
        results = SubfragiumClientLib.modifyTypePoller(inputString, getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PutPollerInput, json.loads(reqPayload))

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

        inputString = 'name=' + poller1 + ',storageType=' + str(poller1Data['storageType'])
        results = SubfragiumClientLib.modifyTypePoller(inputString, getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PutPollerInput, json.loads(reqPayload))

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

        inputString = 'name=' + poller1 + ',storageLocation=' + str( poller1Data['storageLocation'])
        results = SubfragiumClientLib.modifyTypePoller(inputString, getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PutPollerInput, json.loads(reqPayload))

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

        inputString = 'name=' + poller1 + ',disabled=' + str(poller1Data['disabled'])
        results = SubfragiumClientLib.modifyTypePoller(inputString, getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PutPollerInput, json.loads(reqPayload))

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

        inputString = 'name=' + poller1 + ',errorThreshold=' + str(poller1Data['errorThreshold'])
        results = SubfragiumClientLib.modifyTypePoller(inputString, getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PutPollerInput, json.loads(reqPayload))

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

        inputString = 'name=' + poller1 + ',errorHoldTime=' + str(poller1Data['errorHoldTime'])
        results = SubfragiumClientLib.modifyTypePoller(inputString, getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PutPollerInput, json.loads(reqPayload))

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

    def testAddOidBadInput(self):

        inputStrings = [
            '',
            'target=^',
            'target=' + target1 + 'oid=abc',
            'target=' + target1 + 'oid=' + oid1,
            'target=' + target1 + 'oid=' + oid1 + 'poller=^',
            'target=' + target1 + 'oid=' + oid1 + 'poller=' + oid1Data['poller'],
            'target=' + target1 + 'oid=' + oid1 + 'poller=' + oid1Data['poller'] + 'name=^',
            'target=' + target1 + 'oid=' + oid1 + 'poller=' + oid1Data['poller'] + 'name=' + oid1Data['name'],
            'target=' + target1 + 'oid=' + oid1 + 'poller=' + oid1Data['poller'] + 'name=' + oid1Data['name'] + 'enabled=yes',
        ]

        for inputString in inputStrings:
            results = SubfragiumClientLib.addTypeOid(inputString, getApiEndPointUrls)
            self.assertIn('success', results)
            self.assertEquals(results[ 'success'], False)
            self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.put')
    def testAddOidSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": "True" } }', 200)
        mockRequestResponse.return_value = requestObj

        inputString = 'target=' + poller1 + \
                      ',oid=' + oid1 + \
                      ',poller=' + oid1Data['poller'] + \
                      ',name=' + oid1Data['name'] + \
                      ',enabled=' + str(oid1Data['enabled'])
        results = SubfragiumClientLib.addTypeOid(inputString, getApiEndPointUrls)
        reqPayload = mockRequestResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PutOidInput, json.loads(reqPayload))

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

    def testListOidBadInput(self):

        inputStrings = [
            ''
            'target=^',
            'target=' + target1,
            'target=' + target1 + 'oid=abc'
        ]

        for inputString in inputStrings:
            results = SubfragiumClientLib.listTypeOid(inputString, getApiEndPointUrls)
            self.assertIn('success', results)
            self.assertEquals(results['success'], False)
            self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.get')
    def testListOidSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": true, "obj": [ { "enabled": true, "id": "123.123.1.10:1.3.6.1.2.1.2.2.1.10.2", "name": "network.interface.IfInOctets.router1.FastEthernet0/0", "oid": "1.3.6.1.2.1.2.2.1.10.2", "poller": "poller1", "snmpString": "eur", "target": "123.123.1.10", "timeout": 200} ] } }', 200)
        mockRequestResponse.return_value = requestObj

        inputString = 'target=' + target1 + ',oid=' + oid1
        results = SubfragiumClientLib.listTypeOid(inputString, getApiEndPointUrls)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    def testDeleteOidHelp(self):

        results = SubfragiumClientLib.deleteTypeOid('help', getApiEndPointUrls)
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)
        self.assertIn('helpMsg', results)

    def testDeleteOidBadInput(self):

        inputStrings = [
            '',
            'target=^',
            'target=' + target1 + 'oid=abc'
        ]

        for inputString in inputStrings:
            results = SubfragiumClientLib.deleteTypeOid(inputString, getApiEndPointUrls)
            self.assertIn('success', results)
            self.assertEquals(results['success'], False)
            self.assertIn('err', results)

    @mock.patch('SubfragiumClientLib.requests.delete')
    def testDeleteOidSuccess(self, mockRequestResponse):

        requestObj = requestResponse('{"response": {"success": true } }', 200)
        mockRequestResponse.return_value = requestObj

        inputString = 'target=' + target1 + ',oid=' + oid1
        results = SubfragiumClientLib.deleteTypeOid(inputString, getApiEndPointUrls)

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

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "enabled": true, "id": "123.123.1.10:1.3.6.1.2.1.2.2.1.10.2", "name": "network.interface.IfInOctets.router1.FastEthernet0/0", "oid": "1.3.6.1.2.1.2.2.1.10.2", "poller": "poller1", "snmpString": "eur", "target": "123.123.1.10", "timeout": 2000 } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        inputString = 'target=' + target1 + ',oid=' + oid1 + ',poller=' + oid1Data['poller']
        results = SubfragiumClientLib.modifyTypeOid(inputString, getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PutOidInput, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    @mock.patch('SubfragiumClientLib.requests.put')
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyOidModifyNameSuccessfully(self, mockRequestGetResponse, mochRequestPutResponse):

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "enabled": true, "id": "123.123.1.10:1.3.6.1.2.1.2.2.1.10.2", "name": "network.interface.IfInOctets.router1.FastEthernet0/0", "oid": "1.3.6.1.2.1.2.2.1.10.2", "poller": "poller1", "snmpString": "eur", "target": "123.123.1.10", "timeout": 200 } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        inputString = 'target=' + target1 + ',oid=' + oid1 + ',name=' + oid1Data['name']
        results = SubfragiumClientLib.modifyTypeOid(inputString, getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PutOidInput, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

    @mock.patch('SubfragiumClientLib.requests.put')
    @mock.patch('SubfragiumClientLib.requests.get')
    def testModifyOidModifyEnabledSuccessfully(self, mockRequestGetResponse, mochRequestPutResponse):

        getRequestObj = requestResponse('{"response": {"success": "True", "obj": { "enabled": true, "id": "123.123.1.10:1.3.6.1.2.1.2.2.1.10.2", "name": "network.interface.IfInOctets.router1.FastEthernet0/0", "oid": "1.3.6.1.2.1.2.2.1.10.2", "poller": "poller1", "snmpString": "eur", "target": "123.123.1.10", "timeout": 200 } } }', 200)
        mockRequestGetResponse.return_value = getRequestObj

        putRequestObj = requestResponse('{"response": {"success": true} }', 200)
        mochRequestPutResponse.return_value = putRequestObj

        inputString = 'target=' + target1 + ',oid=' + oid1 + ',enabled=' + str(oid1Data['enabled'])
        results = SubfragiumClientLib.modifyTypeOid('target=123.123.1.10,oid=1.3.6.1.2,enabled=False', getApiEndPointUrls)
        reqPayload = mochRequestPutResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PutOidInput, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

if __name__ == '__main__':
    unittest.main()
