#!/bin/sh

mv -v WarthogMQTTDevice.py ./.WarthogMQTTDevice.py_old_$(date +%s)
wget https://raw.githubusercontent.com/patmanmx1991/MARSPlatform/main/DEVICES/WARTHOG_MQTT/WarthogMQTTDevice.py
cat WarthogMQTTDevice.py
source setup.sh
python3 WarthogMQTTDevice.py
