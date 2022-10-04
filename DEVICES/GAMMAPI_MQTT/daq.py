
from command import *
import time
import sys
import os
import serial
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String, MetaData, Float
from sqlalchemy import select
from sqlalchemy.orm import Session
import sqlalchemy as db
import time
from db import *
import json

#time.sleep(30)

print ("Getting DB")
db = dbhandler(["global","rundata"])


longruncount = 0
shortruncount = 0
longruntime_start = time.time()
shortruntime_start = time.time()

lstamp = 0
devicestarttime = 4*[0]
devicestoptime = 4*[0]
lastcounts = 4*[1024*[0]]

print("Getting configs")
# This should be run everytime a run is restarted.
tab         = db.GetTableEntry('global','global_config', 'default')
det0_config = db.GetTableEntry('global','det_config', tab['det0_config'])
det1_config = db.GetTableEntry('global','det_config', tab['det1_config'])
det2_config = db.GetTableEntry('global','det_config', tab['det2_config'])
det3_config = db.GetTableEntry('global','det_config', tab['det3_config'])
det_configs = [det0_config,det1_config,det2_config,det3_config]
usbdevices = [None,None,None,None]

while True:

  longruntime = time.time()-longruntime_start
  shortruntime = time.time()-shortruntime_start

  if (longruncount == 0 or longruntime > tab["long_time"]):
    print("Refreshing run")
    longruntime_start = time.time()
    longruncount += 1
    shortruncount = 0    
    # This should be run everytime a run is restarted.
    tab         = db.GetTableEntry('global','global_config', 'default')
    det0_config = db.GetTableEntry('global','det_config', tab['det0_config'])
    det1_config = db.GetTableEntry('global','det_config', tab['det1_config'])
    det2_config = db.GetTableEntry('global','det_config', tab['det2_config'])
    det3_config = db.GetTableEntry('global','det_config', tab['det3_config'])
    det_configs = [det0_config,det1_config,det2_config,det3_config]

    # Build Device List
    for i in range(4):
      print(i,usbdevices)
      if (usbdevices[i] != None): continue

      if tab["det" + str(i) + "_active"] > 0:
        print("Opening device ",i)
        dev = USBGammaSpec(i)
        usbdevices[i] = dev
      else:
        usbdevices[i] =  None

    for i in range(4):
      if usbdevices[i] == None: continue
      print("Stopping Run")
      usbdevices[i].StopRun()

      last_counts = 4*[1024*[0]]

      print("Setting Config")
      usbdevices[i].SetConfigFromTable( det_configs[i] ) 

      print("Starting new run")
      usbdevices[i].StartRun()
      devicestarttime[i] = int(time.time()*1000.0)

  if (shortruntime > tab["short_time"]):

   print("Short time elapsed, save count data for this device")
   shortruntime_start = time.time()
   shortruncount += 1

   for i in range(4):
      if usbdevices[i] == None: continue

      devinterf = usbdevices[i]
      devconfig = det_configs[i]

      counts = 1024*[0]
      corr_counts = 1024*[0]

      for k in range(10):
        devicestoptime[i] = int(time.time()*1000.0)
        devinterf.GetReadings()
        exposure = devicestoptime[i]-devicestarttime[i]
        devicestarttime[i] = int(time.time()*1000.0)

        for j in range(1024):
          counts[j] = devinterf.GetCounts(j) 

        for j in range(1024):
          corr_counts[j] = counts[j] - last_counts[i][j]
        
        print(corr_counts, max(corr_counts), min(corr_counts))
        if min(corr_counts) > 0: break

      #counts = []
      #for j in range(1024):
      #  counts.append( int(final_counts[j]) )

      ustamp = int(time.time()*1000.0)
      values = { "unixtime": ustamp,
       "run_tag": tab["run_tag"],
       "detid": i,
       "short_run_count":shortruncount,
       "long_run_count":longruncount,
       "hv": devconfig["hv"],
       "lld": devconfig["lld"],
       "exposure": exposure,
       "counts": json.dumps({'counts':corr_counts})
      }

      print(values)
      db.AddEntry( "rundata","gammadata", values )


