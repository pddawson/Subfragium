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

    def __init__(self, text):
        self.text = text

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
    def testAddTargetSuccess(self, mockRequstResponse):

        requestObj = requestResponse('{"response": {"success": "True" } }')
        mockRequstResponse.return_value = requestObj

        inputString = 'name=123.123.1.10,snmpString=eur,timeout=200'
        results = SubfragiumClientLib.addTypeTarget(inputString, getApiEndPointUrls)
        reqPayload = mockRequstResponse.call_args[1]['data']

        validJson = validateJson(SubfragiumControllerSchema.PingTarget, json.loads(reqPayload))

        # First check that API requirements were satisfied
        self.assertEquals(validJson['success'], True)

        # Now check the function returned the correct results
        self.assertIn('success', results)
        self.assertEquals(results['success'], True)

if __name__ == '__main__':
    unittest.main()
