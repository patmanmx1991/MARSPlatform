import paho.mqtt.client as mqtt
import json
import os

print(os.environ)

mqttc=mqtt.Client()
mqttc.connect(os.environ["MARS_MQTT_IP"],int(os.environ["MARS_MQTT_PORT"]),60)
mqttc.loop_start()

message = {
  "command": "SET",
  "data": {
    "battery":{"value":10.1,"type":"Number","metadata":{}}
  }
}

print( json.dumps(message))
(result,mid)=mqttc.publish("marsapi/v1/marsrover1/warthog/command", json.dumps(message) ,2)

mqttc.loop_stop()
mqttc.disconnect()
