from command import *
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

class GAMMAPI_DEVICE:
    ##############################################
    # Module Initializer
    ##############################################
    def __init__(self, client, device):
        print("Starting GammaPi Device : " + device)
        self.device = device
        self.client = client
        self.servertime = -1
        self.ServerConnected = False

        # Setup client subscriptions
        self.COMMAND_TOPIC  = "marsapi/v1/marsrover1/{}/command".format(device)
        self.DATA_TOPIC     = "marsapi/v1/marsrover1/{}/data".format(device)
        self.ACK_TOPIC      = "marsapi/v1/message"
        self.SERVERHB_TOPIC = "marsapi/v1/heartbeat"

        # Establish default polling dataset
        # List of data
        # - Start time, current time, devicesettings, 

        self.DATA = {
            "start_time":        { "type":"Integer",  "metadata":{}, "value":int(time.time()) },
            "timestamp":      { "type":"Integer",  "metadata":{}, "value":int(time.time()) },
            "command_list":      { "type":"String",   "metadata":{}, "value": "" },
            "ready":             { "type":"Integer",  "metadata":{}, "value": 1 },
            "runtag":            { "type":"String", "metadata":{}, "value": "gammapi" },
            "exposure":          { "type":"Integer", "metadata":{}, "value": 20 },
            "tube0_hv":          { "type":"Integer", "metadata":{}, "value": 550 },
            "tube1_hv":          { "type":"Integer", "metadata":{}, "value": 550 },
            "tube2_hv":          { "type":"Integer", "metadata":{}, "value": 550 },
            "tube3_hv":          { "type":"Integer", "metadata":{}, "value": 550 },
            "tube0_lld":          { "type":"Integer", "metadata":{}, "value": 100 },
            "tube1_lld":          { "type":"Integer", "metadata":{}, "value": 100 },
            "tube2_lld":          { "type":"Integer", "metadata":{}, "value": 100 },
            "tube3_lld":          { "type":"Integer", "metadata":{}, "value": 100 }
        }
        self.SettingsChanged = True
        self.runcount = 0

        # Establish a new command list
        self.commandlist = []

        # Publish State on BOOT
        self.PUBLISH_STATE(self.client)

    ##############################################
    # Main MQTT Connecetion Commands (Required)
    ##############################################
    def acknowledge(self, msg):
        self.client.publish(self.ACK_TOPIC, "[" + self.device + "] " + msg + " : " + str(int(time.time())),2)

    def on_connect(self,client, userdata, flags, rc):
        # This will be called once the client connects
        print(f"{self.device} Connected with result code {rc}")
        # Subscribe here
        print("Subscribing to :", self.COMMAND_TOPIC)
        client.subscribe(self.COMMAND_TOPIC)
        client.subscribe(self.SERVERHB_TOPIC)

        self.ServerConnected = True

        self.acknowledge("CONNECTED")

    def on_message(self,client, userdata, msg):
        print(f"{self.device} Message received [{msg.topic}]: {msg.payload}")
        self.acknowledge("MESSAGE RECEIVED {msg.topic} {msg.payload}")

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

        if (msg.topic == self.POSITION_TOPIC):
            self.UPDATE_POSITION(jsonobj)

        if (msg.topic == self.SERVERHB_TOPIC):
            self.servertime = time.time()

        # Always update the device entity after a command or setting
        self.PUBLISH_STATE(client)

    def check_server_connection(self):
        if time.time() - self.servertime > 5: self.ServerConnected = False

    ##############################################
    # Publish current state periodically
    ##############################################
    def PUBLISH_STATE(self,client):
        self.DATA["command_list"]["value"] = str((json.dumps(self.commandlist)).encode())
        self.DATA["timestamp"]["value"] = int(time.time())
        self.DATA["ready"]["value"] = int(len(self.commandlist) == 0)
        print(self.DATA)

        print(json.dumps(self.DATA,indent=3))

        (result,mid)=client.publish(self.DATA_TOPIC,
                                  json.dumps(self.DATA),
                                  2)
        print("Publish Result", result,mid)

    ##############################################
    # Receive an MQTT Command
    ##############################################
    def DEVICE_COMMAND(self, jsonobj):
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

      self.ProcessRun()

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
      if (cmd == "STOP"):  res = self.STOP(dat)
      if (cmd == "START"): res = self.START(dat)
      if (cmd == "SET"):   res = self.SET(dat)

      # If returned true, command successful and can remove
      if res == True:
        del self.commandlist[0]

      self.PUBLISH_STATE(self.client)
      print("Current Command List", self.commandlist)

    ##############################################
    # Add all possible commands
    ##############################################
    def CLEARCOMMANDLIST( self, command=None ):
      print("CLEARING COMMAND LIST")
      self.commandlist = []
      return True

    def STOP( self, command ):
      print("STOP")
      return True

    def START( self, command ):
      print("START")
      return True
  
    def WAIT( self, command ):
      print("WAIT")
      time.sleep( command["time"] )
      return True

    def SET( self, command ):
      for key in command:
          if key in self.GLOBAL_DATA: self.DATA[key] = command[key]
          else: print("Setting not found in device : ", key, command[key])
      self.SettingsChanged = True
      return True


    def ProcessRun(self):

      if self.runcount % 30 == 0 or self.SettingsChanged:
        self.SettingsChanged = False
        print("Starting run")
        self.devicestarttime = 4*[0]
        self.devicestoptime = 4*[0]
        self.usbdevices = 4*[None]
        for i in range(4):
          try:
            self.usbdevices[i] = USBGammaSpec(i)
            print("Registered USB Spec {}".format(i))
          except:
            print("USB Device {} failed to add!".format(i))
            self.usbdevices[i] = None
          break

        print("Setting up Run")

        for i in range(4):
          if self.DATA["tube{}_hv".format(i)]["value"] > 1000:
            self.DATA["tube{}_hv".format(i)]["value"] = 1000

        for i in range(4):
          if self.usbdevices[i]:
            print("Stopping for {}".format(i))
            self.usbdevices[i].SetConfig(
                hv=self.DATA["tube{}_hv".format(i)]["value"],
                gain=1000,
                lld=self.DATA["tube{}_lld".format(i)]["value"],
                in1 = 1,
                pmtgain = 12,
                out1 = 1,
                out2 = 1)
            self.usbdevices[i].StopRun()
            self.devicestarttime[i] = int(time.time()*1000.0)
            self.usbdevices[i].StartRun()

        for i in range(4):
          self.last_counts = 4*[1024*[0]]

      exposure = int(self.DATA["exposure"]["value"])
      if exposure > 30: exposure = 30
      print("Waiting for {} Seconds".format(exposure))
      time.sleep(exposure)

      print("Stopping Run")
      for i in range(4):
        if self.usbdevices[i]:
          print(f"Getting Readings {i}")
          self.usbdevices[i].GetReadings()
          self.usbdevices[i].GetReadings()
          self.usbdevices[i].GetReadings()
          self.devicestoptime[i] = int(time.time()*1000.0)
          self.usbdevices[i].StartRun()
          
      print("Getting Run Readings")
      for i in range(4):
        if self.usbdevices[i]:
         exposure = self.devicestoptime[i]-self.devicestarttime[i]

         counts = 1024*[0]
         corr_counts = 1024*[0]

         for j in range(1024):
           counts[j] = self.usbdevices[i].GetCounts(j) 
           counts[j] = self.usbdevices[i].GetCounts(j) 
           counts[j] = self.usbdevices[i].GetCounts(j) 
           corr_counts[j] = counts[j] - self.last_counts[i][j]
           self.last_counts[i][j] = counts[j]

         df = {
           "time": int(time.time()*1000.0),
           "start_time": self.devicestarttime[i],
           "end_time": self.devicestoptime[i],
           "device": i,
           "counts": str(json.dumps(counts).encode()),
           "corr_counts": str(json.dumps(corr_counts).encode()),
           "hv": self.DATA["tube{}_hv".format(i)]["value"],
           "lld": self.DATA["tube{}_lld".format(i)]["value"],
           "exposure":  self.devicestoptime[i]-self.devicestarttime[i],
           "runtag": self.DATA["runtag"]["value"]
         }
         print(df)
         res = client.publish("marsapi/v1/marsrover1/{}/data".format(self.device + "_det" + str(i)), json.dumps(df), 2)
         print(res)

         self.devicestarttime[i] = self.devicestoptime[i]
      self.runcount += 1

client=mqtt.Client()
print("Connecting to ", MQTT_IP, MQTT_PORT)
client.connect(MQTT_IP, int(MQTT_PORT),1)

gammapi = GAMMAPI_DEVICE(client, "gammapi")
client.on_connect = gammapi.on_connect
client.on_message = gammapi.on_message

client.loop_start()

while True:
    gammapi.UPDATE_STATE(client)

client.loop_stop()
client.disconnect()
