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

MQTT_IP_ADDRESS = os.environ["MARS_MQTT_IP"]
MQTT_PORT = os.environ["MARS_MQTT_PORT"]  

COMMAND_TOPIC = "marsapi/v1/marsrover1/warthog/command"
DATA_TOPIC = "marsapi/v1/marsrover1/warthog/data"

class MotionDevice():
    def __init__(self, client):

        print("Starting Motion Device")
        self.DATA = {
            "location":          { "type":"geo:json", "meta":{}, "value":{ "type":"Point", "coordinates":[0.0,0.0] } },
            "battery":           { "type":"Number", "meta":{}, "value":"12.1" },
            "start_time":        { "type":"Integer", "meta":{}, "value":'0' },
            "command_timestamp": { "value":int(time.time()), "type":"Integer", "meta":{}},
            "command_list":      { "value":json.dumps( commandlist ), "type":"String", "meta":{}}
        }

        self.COMMAND_TOPIC

    def on_connect(client, userdata, flags, rc):
        # This will be called once the client connects
        print(f"Connected with result code {rc}")

        # Subscribe here!
        client.subscribe(COMMAND_TOPIC)

    def on_message(client, userdata, msg):
        print(f"Message received [{msg.topic}]: {msg.payload}")

        # Check only accept specific MQTT command messages
        if (msg.topic != COMMAND_TOPIC): return

        # Parse JSON Object
        jsonobj = json.loads(msg.payload.decode())
        DEVICE_COMMAND(client, jsonobj)

        # Always update the device entity
        PUBLISH_STATE(client)

    def PUBLISH_STATE(client):
      (result,mid)=client.publish(DATA_TOPIC, json.dumps(datastream) ,2)
      print(result,mid)

    def DEVICE_LOOP(client):
      time.sleep(1)
      print("Current Command List", commandlist)

      if len(commandlist["commands"]) == 0: continue

      commandlist["current_command"] = commandlist["commands"][0]

      cmd = commandlist["current_command"]["command"]
      dat = commandlist["current_command"]["data"]

      if (cmd == "WAIT"): res = WAIT(dat)
      if (cmd == "MOVE"): res = MOVE(dat)

      # If returned true, command successful and can remove
      if res == True:
        del commandlist["commands"][0]
        commandlist["current_command"] = ""

      PublishState()
      print("Current Command List", commandlist)

    def DEVICE_COMMAND(client, jsonobj):
        if jsonobj["command"] == "emergencystop": EMERGENCYSTOP()
        if jsonobj["command"] == "clearcommandlist": CLEARCOMMANDLIST()

        # Add the command to the master list of commands.
        print("Adding Command", jsonobj)
        global DEVICE_DATA
        DEVICE_DATA["command_list"].append( jsonobj )

    def EMERGENCYSTOP( self, command=None ):
      print("EMERGENCY STOP")
      return True

    def CLEARCOMMANDLIST( self, command=None ):
      print("CLEARING COMMAND LIST")
      commandlist["commands"] = []
      commandlist["current_command"] = ""
      return True

    def WAIT( command ):
      time.sleep( self, command['time'] )
      return True

    def MOVE( self, command ):
      print("Moving Rover!")
      time.sleep(1)
      return True


client=mqtt.Client()
client.connect(MQTT_IP_ADDRESS, int(MQTT_IP_PORT),60)

warthog = WARTHOG_DEVICE(client)
client.on_connect = warthog.on_connect
client.on_message = warthog.on_message

client.loop_start()
while True:
    warthog.DEVICE_LOOP()
    
client.loop_stop()
client.disconnect()
