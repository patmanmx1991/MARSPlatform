import ctypes
import time
import json

lib = ctypes.cdll.LoadLibrary('/home/gammapi/GAMMA_MULTI/python/libUSBGAMMADAQ.so')

class USBGammaSpec(object):

  def __init__(self, id):    
    lib.USBGammaSpec_ctype.argtypes = [ctypes.c_int]
    lib.USBGammaSpec_ctype.restype = ctypes.c_void_p

    lib.StartRun_ctype.argtypes = [ctypes.c_void_p]
    lib.StartRun_ctype.restype  = ctypes.c_void_p

    lib.StopRun_ctype.argtypes = [ctypes.c_void_p]
    lib.StopRun_ctype.restype  = ctypes.c_void_p

    lib.GetReadings_ctype.argtypes = [ctypes.c_void_p]
    lib.GetReadings_ctype.restype = ctypes.c_void_p

    lib.GetReadingExposure_ctype.argtypes = [ctypes.c_void_p]
    lib.GetReadingExposure_ctype.restype = ctypes.c_long

    lib.GetCounts_ctype.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.GetCounts_ctype.restype = ctypes.c_int

    lib.SetConfig_ctype.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    lib.SetConfig_ctype.restypes = ctypes.c_void_p
    
    self.obj = lib.USBGammaSpec_ctype(id)
    self.isrunning = False
    
  def StartRun(self):
    self.starttime = time.time()
    lib.StartRun_ctype(self.obj)
    self.isrunning = True
    
  def StopRun(self):
    self.stoptime = time.time()
    lib.StopRun_ctype(self.obj)
    self.isrunning = False
    
  def GetReadings(self): lib.GetReadings_ctype(self.obj)

  def GetReadingExposure(self): return int(lib.GetReadingExposure_ctype(self.obj))

  def GetStartTime(self): return self.starttime
  def GetStopTime(self):
    if self.isrunning: return time.time()
    else: return self.stoptime
    
  def GetCounts(self, i): return  lib.GetCounts_ctype(self.obj, i)
  
  def SetConfig(self,
                hv=550,
                gain=1000,
                lld=25,
                in1 = 1,
                pmtgain = 12,
                out1 = 1,
                out2 = 1):
    self.hv = hv
    self.gain = gain
    self.lld = lld
    self.in1 = in1
    self.pmtgain = 12
    self.out1 = out1
    self.out2 = out2
    lib.SetConfig_ctype( self.obj, hv, gain, lld, in1, pmtgain, out1, out2)
  def SetConfigFromTable(self,table):
    self.SetConfig( hv=table["hv"], gain=table["gain"],lld=table["lld"],in1=table["in1"],pmtgain=table["pmtgain"],out1=table["out1"],out2=table["out2"])

  def GetHist(self):
    vals = []
    for i in range(20,1020):
      print("HIST",i,self.GetCounts(i))
      val = self.GetCounts(i)
      vals.append(val)
    return vals
  
  def SaveReadings(self, filepath):
    datadict = {}
    datadict["hv"] = self.hv
    datadict["lld"] = self.lld
    datadict["gain"] = self.gain
    datadict["in1"] = self.in1
    datadict["pmtgain"] = self.pmtgain
    datadict["out1"] = self.out1
    datadict["out2"] = self.out2
    datadict["start"] = self.GetStartTime()
    datadict["stop"] = self.GetStopTime()
    datadict["data"] = self.GetHist()

    print("saving readings to :",filepath)
    with open(filepath, 'w') as outfile:
      json.dump(datadict, outfile)
    
