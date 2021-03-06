import urllib2
import json
import jsonschema
import re
from schema import Schema, SchemaError


def validateObj(objSchema, obj):

    objSchema = Schema(objSchema)

    try:
        objSchema.validate(obj)
        return {'success': True}
    except SchemaError, e:
        return {'success': False, 'err': 'Invalid Object: %s' % e}


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


def validateTargetName(name):

    validIpAddressRegex = '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
    validHostnameRegex = '^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$'

    nameValidator = re.compile(validIpAddressRegex)
    ipValidator = re.compile(validHostnameRegex)

    validatedNameInput = nameValidator.match(name)
    validatedIpInput = ipValidator.match(name)
    if validatedNameInput is None and validatedIpInput is None:
        return {'success': False, 'err': 'Invalid hostname or IP address'}

    return {'success': True}


def getApiEndPoint(apiServer):

    baseUrl = 'http://' + apiServer

    api = {}

    try:
        response = urllib2.urlopen(baseUrl)
        data = response.read()
        apiEndpoints = json.loads(data)
        for apiEndpoint in apiEndpoints['response']['obj']:
            url = baseUrl + apiEndpoints['response']['obj'][apiEndpoint]
            api[apiEndpoint] = url
        return {'success': True, 'urls': api}
    except urllib2.URLError:
        return {'success': False, 'err': 'Could not get API End Points'}
