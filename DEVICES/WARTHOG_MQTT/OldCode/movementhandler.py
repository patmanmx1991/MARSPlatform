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

orion = orion_handler("")

commandlist = {
"current_command": "",
"commands": []
}

device_entity = {
    "location": { "type":"geo:json", "meta":{}, "value":{ "type":"Point", "coordinates":[0.0,0.0] } },
    "battery":  { "type":"Number", "meta":{}, "value":"12.1" },
    "start_time": { "type":"Integer", "meta":{}, "value":'0' }
    "command_timestamp":{"value":int(time.time()), "type":"Integer", "meta":{}},
    "command_list":{"value":json.dumps( commandlist ), "type":"String", "meta":{}}
}

def EMERGENCYSTOP( command=None ):
  print("EMERGENCY STOP")
  return True

def CLEARCOMMANDLIST( command=None ):
  print("CLEARING COMMAND LIST")
  commandlist["commands"] = []
  commandlist["current_command"] = ""
  return True

def WAIT( command ):
  time.sleep( command['time'] )
  return True
 
def MOVE( command ):
  
  print("Moving Rover!")
  time.sleep(1)

  return True  

def PublishState(client):
  (result,mid)=client.publish("marsapi/v1/marsrover1/warthog/data", json.dumps(datastream) ,2)
  print(result,mid)

def on_connect(client, userdata, flags, rc):
    # This will be called once the client connects
    print(f"Connected with result code {rc}")

    # Subscribe here!
    client.subscribe("marsapi/v1/marsrover1/warthog/command")

def on_message(client, userdata, msg):
    print(f"Message received [{msg.topic}]: {msg.payload}")
    
    # Only accept specific MQTT command messages
    if (msg.topic != "marsapi/v1/marsrover1/warthog/command"): return 

    # Check for emergency stop or clearcommands
    jsonobj = json.loads(msg.payload.decode())
   
    if jsonobj["command"] == "emergencystop": EMERGENCYSTOP()
    if jsonobj["command"] == "clearcommandlist": CLEARCOMMANDLIST()    
       
    # Add the command to the master list of commands.
    print("Adding Command", jsonobj)
    global commandlist
    commandlist["commands"].append( jsonobj )

    # Update the device entity
    PublishState()
    
client=mqtt.Client()
client.connect("


client.on_connect = on_connect
client.on_message = on_message

client.loop_start()

dev = orion.GetEntity( "warthog" )
  
while True:

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

client.loop_stop()
client.disconnect()
