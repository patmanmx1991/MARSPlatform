import paho.mqtt.client as mqtt
import json
import os

print(os.environ)

mqttc=mqtt.Client()
mqttc.connect(os.environ["MARS_MQTT_IP"],int(os.environ["MARS_MQTT_PORT"]),60)
mqttc.loop_start()

message = {
  "command": "MOVE",
  "data": {
    "target":{"type":"Point","coordinates":[0.0,0.0]}
  }
}

print( json.dumps(message))
(result,mid)=mqttc.publish("marsapi/v1/marsrover1/warthog/command", json.dumps(message) ,2)

for i in range(200):
  print(i)
  message["data"]["target"]["coordinates"] = [i,i]
  (result,mid)=mqttc.publish("marsapi/v1/marsrover1/warthog/command", json.dumps(message) ,2)
  print(result,mid)

print(result,mid)

mqttc.loop_stop()
mqttc.disconnect()
