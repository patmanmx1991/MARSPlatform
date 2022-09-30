import paho.mqtt.client as mqtt
import json

mqttc=mqtt.Client()
mqttc.connect("
mqttc.loop_start()

starttime = int(time.time())
import time

while True:

  status = "idle"
  commandlist = []

  datastream = {
    "timestamp": { "type":"Integer", "meta":{} "value": int(time.time()) },
    "status_timestamp": { "type":"Integer", "meta":{} "value": int(time.time()) },
    "location": { "type":"geo:json", "meta":{}, "value":{ "type":"Point", "coordinates":[0.0,0.0] } },
    "battery":  { "type":"Number", "meta":{}, "value":"12.1" },
    "start_time": { "type":"Integer", "meta":{}, "value": starttime }
    "status": {  "type":"Integer", "meta":{}, "value": status } 
  }

  (result,mid)=mqttc.publish("marsapi/v1/marsrover1/warthog/data", json.dumps(datastream) ,2)
  time.sleep(1)

mqttc.loop_stop()
mqttc.disconnect()
