# Subfragium

Subfragium is a basic API based SNMP poller for network engineers. It fits in the
gap between full feature SNMP pollers such as Cacti, OpenNMS etc and a simple scripts c
collecting a few SNMP OIDs.

The system is intended to provide a simple interface that a network 
engineer can easily understand to poll SNMP OIDs of interest. It also frees the 
engineer from having to consider basic scaling of how many SNMP OIDs can be
gathered in a single polling cycle which is where most simple scripts run into
problems.

It does not handle the storage of gathered data. There are many time series 
storage system that can handle this task. Currently its integrated with
graphite.

Its under active development - further documentation will be written when 
time permits.

## Components

1. SubfragiumController : A flask based REST API providing access to modifying the 
back end database of SNMP targets and their respective OIDs and allocating 
them to a SubfragiumPoller
2. SubfragiumPoller : A multiprocess script that queries the API for a list of
 SNMP OIDs and then polls them periodically and stores them in a time series 
 database
3. SufragiumClient : A simple CLI client that integrates with the API to provide 
a method of adding/deleting and modifying SNMP OIDs for polling