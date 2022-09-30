# MARS Server

The MARSPlatform server is based on the FiWARE Application stack.
Modules are all loaded via docker-compose, so to start the server
simply run 

$ docker-compose up

The only non-standard FiWARE module is currently the mqtthandler.
This automatically intercepts data coming from the devices over
MQTT and adds it as an entity automatically to ORION. This means
new devices can be added as entities easily in the field, however
no automated subscriptions are yet established for historic
data saving.




