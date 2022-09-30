import paho.mqtt.client as mqtt
import json

mqttc=mqtt.Client()
mqttc.connect(os.environ["MARS_MQTT_IP"],int(os.environ["MARS_MQTT_PORT"]),60)
mqttc.loop_start()

message = {
  "command": "motion_target",
  "data": {
    "target": { "type": "Points", "coordinates": [0.0,0.0] }
  }
}

print( json.dumps(message))
(result,mid)=mqttc.publish("marsapi/v1/marsrover1/warthog/command", json.dumps(message) ,2)
print(result,mid)

import time

while True:

  datastream = {
    "location": { "type":"geo:json", "meta":{}, "value":{ "type":"Point", "coordinates":[0.0,0.0] } },
    "battery":  { "type":"Number", "meta":{}, "value":"12.1" },
    "start_time": { "type":"Integer", "meta":{}, "value":'0' }
  }

  (result,mid)=mqttc.publish("marsapi/v1/marsrover1/warthog/data", json.dumps(datastream) ,2)
  print(result,mid)

  time.sleep(1)

mqttc.loop_stop()
mqttc.disconnect()
