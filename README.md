# Subfragium

Subfragium is a basic API based Simple Network Management Protocol (SNMP) version 2 
poller for network engineers. It fits in the gap between full feature SNMP pollers 
such as Cacti, OpenNMS etc and a simple scripts collecting a few SNMP Object Identifiers
(OID).

**REF** to SNMP resources

The system is intended to provide a simple interface that a network 
engineer can easily understand to poll SNMP OIDs of interest. It also frees the 
engineer from having to consider basic scaling of how many SNMP OIDs can be
gathered in a single polling cycle which is where most simple scripts run into
problems.

It does not handle the storage of gathered data. There are many time series 
storage system that can handle this task. Currently its integrated with
graphite (**REF**).

The poller is synchronous in operation which limits it scalability but makes it simplier.
As outlined above scalability wasn't one of the primary goals. If polling many thousands / 
millions of OIDs is the aim one of the other platforms above is a better choice.

## Storage

Currently only graphite is supported for back end storage of metrics. 

### Graphite

Installing graphite and setting it up is beyond the scope of this documentation. Better guides exist such as 
**GRAPHITE REF**

* When using graphite with whisper storage (the default) the filesystem is used to organise and store data. 
Subfragium will convert any '/' which are filesystem delimiters on *nix platforms to '-' to avoid confusion. 
Cisco platforms which general name interfaces with the form that looks like form <interface><slot>/<port> or 
some similar variation is a good example e.g. GigabitEthernet0/1 will become GigabitEthernet0-1.
Other platforms such as Juniper have similar behaviour.

## Python Virtual Environment

Subfragium has been developed using the Python Virtual Environment (virtualEnv) (**REF**) to avoid 
installing modules into a python installation (possibly system wide). It runs without virtualenv but 
the dependencies outlined  below will be easier to install within a virtual env
the system wide Python modules.

## Module Dependencies

The following modules are required for Subfragium:

* Flask 0.11.1
* gevent 1.2.1
* jsonschema 2.5.1
* pysnmp 4.3.2
* python-daemon 2.1.2
* requests 2.11.1
* schema 0.6.5
* Werkzeug 0.11.11

To run the unit tests also requires:

* mock 2.0.0

## Basic Concepts

Subfragium is built on three basic concepts:

* Targets: Devices that support SNMP and contain OIDs that should be polled
* OID: Specific OIDs on a target that should be polled by the poller
* Pollers: Scripts that poll particular OIDs on targets and place the polled data 
into data storage

### Targets

This is a device that supports SNMP. Usually a network device of some kind although
any device supporting SNMP version 2 should be compatible. A target is defined using:

* Hostname / IP Address: This is the destination of SNMP GET requests 
* SNMP Community String: THis is a security string required by the device
* Timeout: This is the period to wait for an SNMP response

### OIDs

OIDs are specific instances of a statistic on a device accessible via SNMP. They are 
defined using:

* Target: A hostname / IP address previous defined as a target
* OID: ASN.1 notation unique identifier from the Management Information Base (MIB)
* Enabled State: Whether or not this OID should be actively polled
* Poller: The poller instance that should poll this OID

Generally the OID being defined would one that returns a value that changes over time. 

### Pollers

Pollers are specific instances of the polling script that poll SNMP OIDs on particular
devices. These are defined using:

* Name: Essentially just a unique string

## Components

1. SubfragiumController : Flask based REST API providing control information for 
the SubfragiumPoller
2. SubfragiumPoller : A multiprocess script that polls configured OIDs
3. SufragiumCli : A simple CLI client that manipulates the SubfragriumController

## SubfragiumController

### Description

The SubfragiumController is a Flask based HTTP REST API that provides an interface 
to manipulate targets, OIDs and pollers from the Basic Components section. It stores 
these definitions in a database (currently SQLite). It primary reason for having a 
controller is provide a central location for configuration information that is easy to
modify as required.

The API provides functions to add, delete, modify and query targets, OID, and pollers 
while ensuring they are logically correct. e.g. The API prevents a request to add
a OID for polling on non-existent target.

### Configuration

The SubfragiumController requires a configuration file to allow it to start and service
requests. All the parameters are currently grouped under the general section.
The parameters required are:

* dbPath (URL formatted string): The path to the SQLite database in which to store 
target, oid and poller data
* port (number): A port upon which to listen for API requests
* logFile (string): A path to a log file
* logLevel (enum): The level of logging which should one of
    * debug
    * info
    * warning
    * error
    * critical

An example file is included that contains:

<pre>
<code>
[general]
dbPath = sqlite:////home/pdd/Subfragium-Dev/SubfragiumDB-Dev.sqlite
port = 9999
logFile = /home/pdd/Subfragium-Dev/SubfragiumController.log
logLevel = info
</code>
</pre>

## Usage

To start the SubfragiumController enter the following commands:

<pre>
<code>
# python SubfragiumController.py SubfragriumController.cfg
</code>
</pre>

This assumes everything is in the current directory including the Subfragium software
and configuration.

The SubfragiumController supports the following command line options:

* -f : Run in the foreground for debugging purposes

## SubfragiumPoller

### Description

The SubfragiumPoller handles polling defined OIDs against targets and send the data
to a time series data store (currently graphite). It is multi-process with two types of
process

1. Managment Process: Handles start up, shutdown, getting the list of OIDs to query 
peridically and the number of polling processes
2. Poller Process: Simply polles the OIDs and places the results in the back end time
series data store.

A local configuration fileis purely to provide enough configuration to get the poller 
running and tell it where its controller is. Most of its configuration is taken from 
the SubfragiumController. Primarily this is the list of OIDs to be polled but some 
other configuration information  is also held too such as:
 
* cycleTime (seconds): How often the poller polls the OIDs.
* disabled (True|False): Whether the poller is available for new targets. This allows the API to deny
requests that add new OIDs to a specific poller. It doesn't however re-assign existing
OIDs.
* errorThreshold (number): This defines how many failed polls for an OID are allowed 
before it is disabled for a period of time.
* errorHoldTime (seconds): This defines how long a OID is disabled if it reaches the
errorThreshold.
* holdDown (seconds): Length of time that changes to the number of processes are 
prevented to allow the load to settle.
* maxProcesses (number): The maximum number of polling sub-processes a poller is allowed 
to have. Broadly depends on the capacity available to polling (CPU, Memory, Network). 
The poller will not start more than this number of processes.
* minProcesses (number): The minimum number of polling sub-processes a poller is allowed 
to have.
* numProcesses (number): The number of polling sub-processes a poller starts with.
* name (string): A string to uniquely identify this poller instance.
* storageLocation (URI formatted string): Where to send data points for storage.
* storageType (string): The type of storage defined in the storageLocation field

### Configuration

The SubfragiumPoller requires a configuration file to start up and find its controller
which provides the rest of the information above. All of the parameters are currently 
grouped under the general section. The parameters required are:

* controller (string): A hostname:port combination that defines location of the API
* logLevel (enum): The level of logging which should one of
    * debug
    * info
    * warning
    * error
    * critical
* pollerName (string): A string that uniquely identifies the poller
* logFile (string): A path to a log file

Example file is included that contains:

<pre>
<code>
[general]
controller = localhost:9999
logLevel = debug
pollerName = poller1
logFile = SubfragiumPoller.log
</code>
</pre>

### Usage

To start the SubfragiumPoller enter the following commands:

<pre>
<code>
# python SubfragiumPoller.py SubfragriumPoller.cfg
</code>
</pre>

This assumes everything is in the current directory including the Subfragium software
and configuration.

The SubfragiumPoller supports the following command line options:

* -c <host:port> : Overrides the SubfragiumController defined in the configuration file
* -f : Run in the foreground for debugging purposes
* -l <level>: Overrides the log level defined in the configuration file
* -L <path>: Overrides the log file path defined in the configuration file
* -p <name>: Overrides the poller name definde in the configuration file

## SubfragiumCli

### Description

The SubfragiumCli is a simple command line interface (CLI) that manipulates the API. 
The API can be modified using a web brower or other HTTP interface but for small 
tasks a CLI is more convienient.

The SubfragiumCli provides the ability to manipulate all of the available API methods.

### Usage

<pre>
<code>
# python SubfragiumCli.py <controllerHost:port> <action> <type> <data|filter>
</code>
</pre>

The SubfragiumCli has no command line options but must be supplied with the following
positional arguments:

* <controllerHost:port>: The hostname and port that the SubfragriumController listens for
API requests on
* action: What action the API is going to take. Must be one of:
    * add
    * delete
    * modify
    * list
* type: What type is the action applied to. Must be one of:
    * target
    * targets
    * oid
    * oids
    * poller
    * pollers
* data|'all': What data or filter is being supplied to the API
    * In the case of an add this is id=value,[field=value]
    * In the case of a delete this is id=value
    * In the case of a modify this is id=value,field=value
    * In the case of a list this is either 'all' or id=value

Note: When modifying a entry using the CLI after identifying the entry to be modified only a single
value maybe changed at a time. This is a limitation of the CLI to make it relatively simple to use.
As many values as desired can be changed through the raw API.

### Examples

The following example show how to use the CLI interface.

#### Targets

* Adding a new target
<pre>
<code>
python SubfragiumCli.py add target name=123.123.1.1,snmpString=eur,timeout=200
</code>
</pre>

* Deleting an existing target
<pre>
<code>
python SubfragiumCli.py delete target name=123.123.1.1
</code>
</pre>

* Modifying an existing target
<pre>
<code>
python SubfragiumCli.py modify target name=123.123.1.1,timeout=500
</code>
</pre>

* Listing a specific target
<pre>
<code>
python SubfragiumCli.py list target name=123.123.1.1
</code>
</pre>

* Searching for targets
<pre>
<code>
python SubfragiumCli.py list targets all
</code>
</pre>

#### OIDs

* Adding a new oid:
<pre>
<code>
python SubfragiumCli.py add oid target=123.123.1.1,oid=1.3.6.1.2.1.3,poller=poller1,name=network.interface.ifInHcOctets.router1.FastEthernet0/0,enabled=True
</code>
</pre>

* Deleting an existing OID
<pre>
<code>
python SubfragiumCli.py delete oid target=123.123.1.1,oid=1.3.6.1.2.1.3
</code>
</pre>

* Modifying an existing OID
<pre>
<code>
python SubfragiumCli.py modify oid target=123.123.1.1,oid=1.3.6.1.2.1.3,poller=poller2
</code>
</pre>

* Listing a specific OID
<pre>
<code>
python SubfragiumCli.py list oid target=123.123.1.1,oid=1.3.6.1.2.1.3
</code>
</pre>

* Searching for OID(s)
<pre>
<code>
python SubfragiumCli.py list oids all
</code>
</pre>

#### Pollers

* Adding a new poller
<pre>
<code>
python SubfragiumCli.py add poller poller=poller1,minProcesses=1,maxProcesses=10,numProcesses=5,holdDown=20,cycleTime=60,storageType=graphite,storageLocation=pickle://graphite:5000,disabled=True,errorThreshold=3,errorHoldTime=1800
</code>
</pre>

* Deleting an existing poller
<pre>
<code>
python SubfragiumCli.py delete poller poller=poller1
</code>
</pre>

* Modifying an existing poller
<pre>
<code>
python SubfragiumCli.py modify poller poller=poller1,numProcesses=10
</code>
</pre>

* Listing a specific poller
<pre>
<code>
python SubfragiumCli.py list poller poller=poller1
</code>
</pre>

* Searching for poller(s)
<pre>
<code>
python SubfragiumCli.py list pollers all
</code>
</pre>

## API

* URL: /target/\<target\>
    * <code>\<target\></code>: IP address or Hostname e.g. 123.123.123.123 or host1.network.com
    * HTTP Methods
        * HTTP GET: Returns information about a specific target
            * Payload: None
            * URI Parameters: None
            * Response:
                * HTTP Response Code 200: Successful get for target
                    <pre>
                    <code>
                    {
                        'response': {
                            'obj': {
                                target': 'ipAddress|hostname>,
                                'snmpString': 'string',
                                'timeout': 'integer (millseconds)'
                            }
                        }
                        'success': true
                    }
                    </code>
                    </pre>
                * HTTP Response Code 404: Bad client request e.g. no such target
                    <pre>
                    <code>
                    {
                        'err': 'string'
                    }
                    </code>
                    </pre>
                * HTTP Response Code 503: Server failure e.g. Database problem
                    <pre>
                    <code>
                    {
                        'err': 'string' 
                    }
                    </code>
                    </pre>
        * HTTP PUT: Adds a target to the configuration
            * Payload:
                <pre>
                <code>
                {
                    'snmpString': 'string',
                    'timeout': 'integer (millseconds)'
                }
                </code>
                </pre>
            * URI Parameters: None
            * Response
                * HTTP Response Code 200: Successful addition of target
                    <pre>
                    <code>
                    {
                        'success': true
                    }
                    </code>
                    </pre>
                * HTTP Response Code 404: Bad client request e.g. Target already exists
                    <pre>
                    <code>
                    {
                        'err': 'string'
                    }
                    </code>
                    </pre>
                * HTTP Response Code 503: Server failure e.g. Database problem
                    <pre>
                    <code>
                    {
                        'err': 'string'
                    }
                    </code>
                    </pre>
        * HTTP DELETE: Deletes a target from the configuration
            * Payload: None
            * URI Parameters: None
            * Response:
                * HTTP Response Code 200: Successful delete of target
                    <pre>
                    <code>
                    {
                        'success': true
                    }
                    </code>
                    </pre>
                * HTTP Response Code 404: Bad client request e.g. target doesn't exist
                    <pre>
                    <code>
                    {
                        'err': 'string'
                    }
                    </code>
                    </pre>
                * HTTP Response Code 503: Server failure e.g. Database problem
                    <pre>
                    <code>
                    {
                        'err': 'string'
                    }
                    </code>
                    </pre>
* /targets
    * HTTP Methods
        * HTTP GET: Searches across all targets
            * Payload: None
            * URI Parameters: None
            * Response:
                * HTTP Response Code 200: Successful search
                    <pre>
                    <code>
                    {
                        'response': {
                            'obj': [
                                {
                                    'target': 'ipAddress|hostname',
                                    'snmpString': 'string',
                                    'timeout': 'integer (milliseconds)'
                                }
                            ]
                        }
                        'success': true
                    }
                    </code>
                    </pre>
                * HTTP Response Code 503: Server Failure e.g. Database problems
                    <pre>
                    <code>
                    {
                            'err': 'string'
                    }
                    </code>
                    </pre>
* /oid/\<target\>/\<oid\>
    * \<target\>: Hostname or dotted quad notation IP address e.g. abc.net.gs.com or 123.123.123.123
    * \<oid\>: ASN.1 OID definition e.g. 1.3.6.1.2.1.3
    * HTTP Methods
        * HTTP GET: Returns information about a specific OID
            * Payload: None
            * URI Parameters: None
            * Response:
                * HTTP Response Code 200: Successful get of existing OID
                    <pre>
                    <code>
                    {
                        'response': {
                            'obj': [
                                {
                                    'enabled': 'boolean'
                                    'id': 'string',
                                    'name': 'string',
                                    'oid': 'string',
                                    'poller': 'string',
                                    'snmpString': 'string',
                                    'target': 'string',
                                    'timeout': 'number (milliseconds)'
                                }
                            ]
                        }
                        'success': true
                    }
                    </code>
                    </pre>
                * HTTP Response Code 404: Bad client request e.g. No such OID
                    <pre>
                    <code>
                    {
                        'err': 'string'
                    }
                    </code>
                    </pre>
                * HTTP Response Code 503: Server failure e.g. Database problem
                    <pre>
                    <code>
                    {
                        'err': 'string'
                    }
                    </code>
                    </pre>
        * HTTP PUT: Adds a specific OID to the configuration
            * Payload: 
                <pre>
                <code>
                {
                    'enabled': 'boolean'
                    'name': 'string',
                    'poller': 'string',
                }
                </code>
                </pre>
            * URI Parameters: None
            * Response:
                * HTTP Response Code 200: Successful addition of new OID
                    <pre>
                    <code>
                    {
                            'success': true
                    }
                    </code>
                    </pre>                    
                * HTTP Response Code 404: Bad client request e.g. No such OID
                    <pre>
                    <code>
                    {
                            'err': 'string
                    }
                    </code>
                    </pre> 
                * HTTP Response Code 503: Server failure e.g. Database problem
                    <pre>
                    <code>
                    {
                            'err': 'string
                    }
                    </code>
                    </pre> 
        * HTTP DELETE: Delete an OID from the configuration
            * Payload: None
            * URI Parameters: None
            * Response:
                * HTTP Response Code 200: Success deletion of an existing OID
                    <pre>
                    <code>
                    {
                            'success': true
                    }
                    </code>
                    </pre>
                * HTTP Response Code 404: Bad client request e.g. No such OID
                    <pre>
                    <code>
                    {
                            'err': 'string'
                    }
                    </code>
                    </pre>
                * HTTP Response Code 503: Server failure e.g. Database problem
                    <pre>
                    <code>
                    {
                            'err': 'string'
                    }
                    </code>
                    </pre>
                
* /oids
    * HTTP Methods
        * HTTP GET: Seaches across all OIDs
        * Payload: None
        * URI Parameters: None
        * Response:
                * HTTP Response Code 200: Successful search
                    <pre>
                    <code>
                    {
                        'response' {
                            'obj': [ 
                                {
                                    'enabled': 'boolean',
                                    'id': 'string',
                                    'name': 'string',
                                    'oid': 'string',
                                    'poller': 'string',
                                    'snmpString': 'string',
                                    'target': 'string',
                                    'timeout': 'number (millseconds)'
                                }
                            ]
                        }
                        'success': true
                    }
                    </code>
                    </pre>
                * HTTP Response Code 503: Server failure e.g. Database problem
                    <pre>
                    <code>
                    {
                            'err': 'string'
                    }
                    </code>
                    </pre>
    
* /poller/\<poller\>
    * \<poller\>: String representing a unique poller
    * HTTP Methods
        * HTTP GET: Returns information on a specific poller
            * Payload: None
            * URI Parameters: None
            * Response:
                    * HTTP Response Code 200: Success get of existing poller
                        <pre>
                        <code>
                        {
                            'response': {
                                'obj': {
                                    'cycleTime': 'number (seconds)'
                                    'disabled': 'boolean',
                                     'errorHoldTime': 'number (seconds)',
                                     'errorThreshold': 'number',
                                     'holdDown': 'number (seconds)',
                                     'maxProcesses': 'number',
                                     'minProcesses': 'number',
                                     'name': 'string',
                                     'numProcesses': 'number',
                                     'storageLocation': 'string (URI format)',
                                     'storageType': 'string'   
                                 }
                            }
                            'success': true
                        }
                        </code>
                        </pre>
                    * HTTP Response Code 404: Bad client request e.g. No such poller
                        <pre>
                        <code>
                        {
                                'err': 'string'
                        }
                        </code>
                        </pre>
                    * HTTP Response Code 503: Server failure e.g. Database problems
                        <pre>
                        <code>
                        {
                                'err': 'string'
                        }
                        </code>
                        </pre>
        * HTTP PUT: Adds a poller to the configuration
            * Payload: 
                <pre>
                <code>
                {
                    'cycleTime': 'number (seconds)'
                    'disabled': 'boolean',
                    'errorHoldTime': 'number (seconds)',
                    'errorThreshold': 'number',
                    'holdDown': 'number (seconds)',
                    'maxProcesses': 'number',
                    'minProcesses': 'number',
                    'name': 'string',
                    'numProcesses': 'number',
                    'storageLocation': 'string (URI formatted)',
                    'storageType': 'string'
                }
                </code>
                </pre>
            * URI Parameters: None
            * Response:
                    * HTTP Response Code 200: Successfully added a new poller
                        <pre>
                        <code>
                        {
                                'success': true
                        }
                        </code>
                        </pre>
                    * HTTP Response Code 404: Bad client request e.g. Existing poller
                        <pre>
                        <code>
                        {
                                'err': 'string'
                        }
                        </code>
                        </pre>
                    * HTTP Response Code 503: Server failure e.g. Database problems
                        <pre>
                        <code>
                        {
                                'err': 'string'
                        }
                        </code>
                        </pre>                    
        * HTTP DELETE: Deletes a poller from the configuration
            * Payload: None
            * URI Parameters: None
                * HTTP Response Code 200: Successfully deleted an existing poller
                        <pre>
                        <code>
                        {
                                'success': true
                        }
                        </code>
                        </pre>
                    * HTTP Response Code 404: Bad client request e.g. No such poller
                        <pre>
                        <code>
                        {
                                'err': 'string'
                        }
                        </code>
                        </pre>
                    * HTTP Response Code 503: Server failure e.g. Database problems
                        <pre>
                        <code>
                        {
                                'err': 'string'
                        }
                        </code>
                        </pre> 
* /pollers
    * HTTP Methods
        * HTTP GET: Searches across all pollers
            * Payload: None
            * URI Paramters: None
            * Response:
                * HTTP Response Code 200: Successful search
                    <pre>
                    <code>
                    {
                        'response' {
                            'obj': [ 
                                {
                                    'cycleTime': 'number',
                                    'disanbled': 'boolean',
                                    'errorHoldTime': 'number (seconds)',
                                    'errorThreshold': 'number',
                                    'holdDown': 'number (seconds)',
                                    'maxProcesses': 'number',
                                    'minProcesses': 'number',
                                    'name': 'string',
                                    'numProcesses': 'number',
                                    'storageLocation': 'string (URI formatted),
                                    'storageType': 'string'
                                }
                            ]
                        }
                        'success': true
                    }
                    </code>
                    </pre>u
                * HTTP Response Code 503: Server failure e.g. Database problem
                        <pre>
                        <code>
                        {
                                'err': 'string'
                        }
                        </code>
                        </pre> 
                
    
## Example Setup

### Setup using virtualenv and graphite

1. Setup graphite

Setting up graphite is beyond the scope of this document but documentation may be found here:
**REF**

2. Setup virtualenv



3. Configure and Start SubfragiumController
4. Add poller to SubfragiumController(s)
5. Configure and Start SubfragiumPoller(s)
6. Add target(s) to SubfragriumController
7. Add oid(s) to SubfragiumController
8. Check graphite