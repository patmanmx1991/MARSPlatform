import datetime
import os
import math
import json
import base64
import time
import datetime
import paho.mqtt.client as mqttClient
from orionapi import *

import paho.mqtt.client as mqtt

orion = orion_handler("

def on_connect(client, userdata, flags, rc):
    # This will be called once the client connects
    print(f"Connected with result code {rc}")
    # Subscribe here!

def on_message(client, userdata, msg):
    print(f"Message received [{msg.topic}]: {msg.payload}")

    print("Processing Data MQTT Topic")
    device = msg.topic.split("/")[3]
    print( "Device =", msg.topic.split("/")[3])
    
    jsonobj = json.loads(msg.payload.decode())
    print("JSON",jsonobj)
    for key in jsonobj: print(key)

    print("Orion Entity State")
    dev = orion.GetEntity( device )
    if not dev: 
      print("Device not found! Creating!")

      dev = orion.CreateEntity( device, "DataStream" )
      orion.UploadEntity( dev )
      dev = orion.GetEntity( device )

    else:
      print("Found device",dev)

    for key in jsonobj:
      dev.SetFromJson(key, jsonobj[key])
  
    print("Uploading entity")

    dev.Print()
    orion.UploadEntity( dev )
    orion.UpdateEntity( dev)
    
client=mqtt.Client()
client.connect("

client.on_connect = on_connect
client.on_message = on_message

client.subscribe("marsapi/v1/marsrover1/+/data")

client.loop_forever()
