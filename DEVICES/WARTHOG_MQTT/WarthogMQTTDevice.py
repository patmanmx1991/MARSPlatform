import datetime
import os
import math
import json
import base64
import time
import datetime
import paho.mqtt.client as mqttClient

import paho.mqtt.client as mqtt

MQTT_IP = os.environ["MARS_MQTT_IP"]
MQTT_PORT = os.environ["MARS_MQTT_PORT"]

class WARTHOG_DEVICE:
    ##############################################
    # Module Initializer
    ##############################################
    def __init__(self, client, device):
        print("Starting Warthog Device : " + device)
        self.device = device
        self.client = client

        # Setup client subscriptions
        self.COMMAND_TOPIC = "marsapi/v1/marsrover1/{}/command".format(device)
        self.DATA_TOPIC    = "marsapi/v1/marsrover1/{}/data".format(device)

        # Establish default polling dataset
        self.DATA = {
            "location":          { "type":"geo:json", "metadata":{}, "value":{ "type":"Point", "coordinates":[0.0,0.0] } },
            "battery":           { "type":"Number",   "metadata": {}, "value":12.1 },
            "start_time":        { "type":"Integer",  "metadata":{}, "value":int(time.time()) },
            "timestamp":         { "type":"Integer", "metadata": {}, "value":int(time.time()) },
            "command_list":      { "value": "", "type":"String", "metadata":{}},
            "ready":              { "value": 1, "type":"Integer", "metadata":{}}
        }

        # Establish a new command list
        self.commandlist = []

        # Publish State on BOOT
        self.PUBLISH_STATE(self.client)

    ##############################################
    # Main MQTT Connecetion Commands (Required)
    ##############################################
    def on_connect(self,client, userdata, flags, rc):
        # This will be called once the client connects
        print(f"{self.device} Connected with result code {rc}")
        # Subscribe here
        print("Subscribing to :", self.COMMAND_TOPIC)
        client.subscribe(self.COMMAND_TOPIC)

    def on_message(self,client, userdata, msg):
        print(f"{self.device} Message received [{msg.topic}]: {msg.payload}")

        # Parse JSON Object, should always be valid JSON
        try:
            jsonobj = json.loads(msg.payload.decode())
        except:
            print("Failed to parse MQTT JSON Object!")
            return

        # Check only accept specific MQTT command messages
        if (msg.topic == self.COMMAND_TOPIC):
            # Run Command Parser
            self.DEVICE_COMMAND(jsonobj)

        # Always update the device entity after a command or setting
        self.PUBLISH_STATE(client)


    ##############################################
    # Publish current state periodically
    ##############################################
    def PUBLISH_STATE(self,client):
        self.DATA["command_list"]["value"] = (json.dumps(commandlist)).encode()
        self.DATA["timestamp"]["value"] = int(time.time())
        self.DATA["ready"]["value"] = len(self.commandlist) == 0

        print(json.dumps(self.DATA,indent=3))

        (result,mid)=client.publish(self.DATA_TOPIC,
                                  json.dumps(self.DATA),
                                  2)
        print("Publish Result", result,mid)

    ##############################################
    # Receive an MQTT Command
    ##############################################
    def DEVICE_COMMAND(self, jsonobj):

        if jsonobj["command"] == "emergencystop":    self.EMERGENCYSTOP()
        if jsonobj["command"] == "clearcommandlist": self.CLEARCOMMANDLIST()

        # Add the command to the master list of commands.
        print("Adding Command", jsonobj)
        self.commandlist.append( jsonobj )

    ##############################################
    # Main Event Processing Loop for the module.
    # Should decide what to do, perform it, then
    # publish the updated state. In the Warthog
    # we iterate over a list of commands.
    ##############################################
    def UPDATE_STATE(self, client):
      print(self.device + "Current Command List", self.commandlist)
      self.PUBLISH_STATE(self.client)

      # Introduce a lag for updates.
      time.sleep(0.5)

      # If no commands to perform return
      if len(self.commandlist) == 0: return

      # Get the latest command
      cmd = self.commandlist[0]["command"]
      dat = self.commandlist[0]["data"]

      # Perform specific commands.
      if (cmd == "WAIT"): res = self.WAIT(dat)
      if (cmd == "MOVE"): res = self.MOVE(dat)
      if (cmd == "SET"): res = self.SET(dat)

      # If returned true, command successful and can remove
      if res == True:
        del self.commandlist[0]

      self.PUBLISH_STATE(self.client)
      print("Current Command List", self.commandlist)


    ##############################################
    # Add all possible commands
    ##############################################
    def EMERGENCYSTOP( self, command=None ):
      print("EMERGENCY STOP")
      return True

    def CLEARCOMMANDLIST( self, command=None ):
      print("CLEARING COMMAND LIST")
      self.commandlist = []
      return True

    def WAIT( command ):
      print("WAITIING")
      time.sleep( self, command['time'] )
      return True

    def MOVE( self, command ):
      print("Moving Rover!")
      time.sleep(1)
      return True

    def SET( self, command ):
      for key in command:
          if key in self.DATA: self.DATA[key] = command[key]
          else:
              print("Setting not found in device : ", key, command[key])
      return True
    
client=mqtt.Client()
print("Connecting to ", MQTT_IP, MQTT_PORT)
client.connect(MQTT_IP, int(MQTT_PORT),1)

warthog = WARTHOG_DEVICE(client, "warthog")
client.on_connect = warthog.on_connect
client.on_message = warthog.on_message

client.loop_start()

while True:
    warthog.UPDATE_STATE(client)

client.loop_stop()
client.disconnect()
