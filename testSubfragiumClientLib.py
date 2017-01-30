import unittest
import mock

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


class TestControllerApi(unittest.TestCase):

    @mock.patch('SubfragiumClientLib.urllib2.urlopen')
    def testGetApiEndPointSuccess(self, mockUrlResponse):

        mockUrlResponse.return_value = getApiEndpointSuccess

        res = SubfragiumClientLib.getApiEndPoint('localhost:5000')
        print res

if __name__ == '__main__':
    unittest.main()
