import datetime
import os
import math
import json
import base64
import time
import datetime
import paho.mqtt.client as mqttClient
import serial
import pynmea2
from datetime import datetime
import time
from subprocess import Popen

import paho.mqtt.client as mqtt
from envirophat import light, motion, weather, leds
import socket

MQTT_IP = "35.177.218.103"
MQTT_PORT = "1883"

while True:
 s = socket.socket()
 address = MQTT_IP #127.0.0.1'
 port = MQTT_PORT #80  # port number is a number, not string
 try:
    s.connect((address, port)) 
    # originally, it was 
    # except Exception, e: 
    # but this syntax is not supported anymore. 
 except Exception as e: 
    print("something's wrong with %s:%d. Exception is %s" % (address, port, e))
 finally:
    s.close()
    print("Connection Valid!")
    break

# Need to edit so that it regularly checks GPS
class POSITIONING_DEVICE:
    ##############################################
    # Module Initializer
    ##############################################
    def __init__(self, client, device):
        print("Starting Positioning Device : " + device)
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

        self.DATA = {
            "time_start":        { "type":"Integer", "metadata":{}, "value":int(time.time())},
            "location":          { "type":"geo:json", "metadata":{}, "value":{ "type":"Point", "coordinates":[0.0,0.0] } },
            "altitude":          { "type":"Number", "metadata":{}, "value":0.0 },
            "heading":           { "type":"Number", "metadata":{}, "value":0.0 },
            "pressure":          { "type":"Number", "metadata":{}, "value":0.0 },
            "temperature":       { "type":"Number", "metadata":{}, "value":0.0 },
            "accelerometer":     { "type":"String", "metadata":{}, "value":"" }
        }

        self.serialPort = serial.Serial("/dev/ttyS0", 115200, timeout=0.5)
        cmd="AT+CGPS=0,1;+CGPSNMEARATE=1;+CGPSAUTO=1;+CGPS=1,1;+CGPSINFOCFG=1,261"
        self.serialPort.write(cmd.encode())
        print(self.serialPort.read(128))

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
        client.subscribe(self.COMMAND_TOPIC )
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
        print("PUBLISHING DATA")
        print(json.dumps(self.DATA,indent=3))
        (result,mid)=client.publish(self.DATA_TOPIC,
                                  json.dumps(self.DATA),
                                  2)
        print("Publish Result", result,mid)

    ##############################################
    # Main Event Processing Loop for the module.
    # Should decide what to do, perform it, then
    # publish the updated state. In the Warthog
    # we iterate over a list of commands.
    ##############################################
    def UPDATE_STATE(self, client):
      print(self.device + "Current Command List", self.commandlist)

      self.LookForGPSData()
      self.LookForEnviroData()

      self.PUBLISH_STATE(self.client)
      
      time.sleep(0.5)

      # If no commands to perform return
      if len(self.commandlist) == 0: return

      # Get the latest command
      cmd = self.commandlist[0]["command"]
      dat = self.commandlist[0]["data"]

      # Perform specific commands.
      if (cmd == "REBOOT"): res = self.REBOOT(dat)

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

    def REBOOT( self, command ):
      return True

    def LookForGPSData( self ):
      errors = 0
      gps_data = {}
      gps_data["GNGNS"] = None

      if not self.serialPort.in_waiting: return
      while self.serialPort.in_waiting:
        strv = self.serialPort.readline()
        print(strv)
        strv = strv.decode()
        if ('$GNGNS' not in strv): continue
        gps_data["GNGNS"] = pynmea2.parse(strv)

      if not gps_data["GNGNS"]: return

      self.DATA["altitude"]["value"] = float(gps_data["GNGNS"].altitude)
      self.DATA["location"]["value"]["coordinates"] = [float(gps_data["GNGNS"].longitude),float(gps_data["GNGNS"].latitude)]

      print(self.DATA)

    def LookForEnviroData(self):
     self.DATA["heading"]["value"] = float(motion.heading())
     self.DATA["pressure"]["value"] = float(weather.pressure())
     self.DATA["temperature"]["value"] = float(weather.temperature())
     self.DATA["accelerometer"]["value"] = str(motion.accelerometer())[1:-1].replace(' ', '')


time.sleep(30)

client=mqtt.Client()
print("Connecting to ", MQTT_IP, MQTT_PORT)
client.connect(MQTT_IP, int(MQTT_PORT),30)

position = POSITIONING_DEVICE(client, "position")
client.on_connect = position.on_connect
client.on_message = position.on_message
client.loop_start()

while True:
    position.UPDATE_STATE(client)

client.loop_stop()
client.disconnect()
