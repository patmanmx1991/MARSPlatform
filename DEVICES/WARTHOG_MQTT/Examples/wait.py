import paho.mqtt.client as mqtt
import json

mqttc=mqtt.Client()
mqttc.connect(os.environ["MARS_MQTT_IP"],int(os.environ["MARS_MQTT_PORT"]),60)
mqttc.loop_start()

message = {
  "command": "WAIT",
  "data": {
    "time": 10
  }
}

print( json.dumps(message))
(result,mid)=mqttc.publish("marsapi/v1/marsrover1/warthog/command", json.dumps(message) ,2)
print(result,mid)

mqttc.loop_stop()
mqttc.disconnect()
