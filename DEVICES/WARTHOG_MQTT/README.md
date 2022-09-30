#MARS Platform devices
Individual devices for the MARSPlatform should be added in seperate sub folders here.
The assumption is that each device can be modified to have an interface format that
fits in with the MQTT device examples shown here.

In each case a device subscribes to a topic associated with its own name on boot,
and periodically sends the devices current state to the remote server. Any large
datasets that don't fit into the standard json dictionary format should be treated
as special cases when uploading data.

Devices can upload data asynchronously, with times obtained from the server over
NTP used to correlate them (e.g. data from the pundit lab MQTT service linked to GPS data from the
warthog MQTT service).

Devices are at liberty to setup their own processing loops and command handling
provided they recieve the main topic subscriptions from the top level MQTT interface.

The Network Interlock is the exception. This runs on the Warthog, and receives
topic requests from

marsapi/v1/interlock/request and marsapi/va/interlock/release

In all cases only when the interlock queue is completely empty, will the rover actually move.

