import requests
import os
import time

class orion_entity:

    def __init__(self, id, type):
        self.data = {}
        self.data["id"] = id
        self.data["type"] = type

        self.Set( "timestamp", "Number", "0" )

    def SetFromJson(self, key, val):
      if key not in self.data: self.data[key] = {}
      for key2 in val:
        self.data[key][key2] = val


    def SetID(self, val):
       self.data["id"] = val
    def SetType(self, val):
       self.data["type"] = val

    def Set(self, key, type="EMPTY_TYPE", value="EMPTY_VALUE", metadata={}):

        if key not in self.data:
            self.data[key] = {
            "type":"",
            "value":"",
            "metadata":{}
            }

        if key in self.data:
            if type != "EMPTY_TYPE": self.data[key]["type"] = str(type)
            if value != "EMPTY_VALUE": self.data[key]["value"]  = (value)
            if len(metadata) != 0: self.data[key]["metadata"] = metadata

    def SV(self, key, value):
        self.Set(key,value=value)

    def Get(self,key): return self.data[key]

    def Dataframe(self):
        df = {}


        df["id"] = []
        df["type"] = []
        df["value"] = []

        for key in self.data:
            if key == "id" or key == "type": continue
            df["id"].append(key)
            df["type"].append( self.GetType(key))
            df["value"].append( self.GetValue(key) )

        df = pd.DataFrame(data=df)
        df = df.sort_values("type")
        return df

    def GetEntityID(self): return self.data["id"]
    def GetEntityType(self): return self.data["type"]

    def SetEntityID(self, val): self.data["id"] = val
    def SetEntityType(self, val): self.data["type"] = val

    def GetValue(self,key): 
      print("GV",key)
      return self.data[key]["value"]
    def GetType(self,key): return self.data[key]["type"]

    def GetData(self): return self.data
    def SetData(self, jdata): self.data = jdata

    def Print(self):
        print("-> Orion Entity : ", self.data["id"], " : ", self.data["type"])
        for key in self.data:
            if key == "id" or key == "type": continue
            print("-->", key, self.GetValue(key), self.GetType(key))

    def GetDifference(self, entity):

        dt = self.GetData()

        if entity:
          dt2 = entity.GetData()
        else: dt2 = {}

        # print dt['mytimestamp']
        # print dt2['mytimestamp']

        newdt = {}
        for key in dt2:
            if key not in dt:
                newdt[key] = dt2[key]
                continue

            if dt2[key] != dt[key]:
                newdt[key] = dt2[key]

        # set1 = set(dt.items())
        # set2 = set(dt2.items())
        # dif = set1 ^ set2

        return newdt



class orion_handler:
    def __init__(self):

        self.gateway = os.environ["COSMICSWAMP_IP"]
        self.port    = os.environ["ORION_PORT"]

        self.aliases = {}
    def __init__(self, gw, port):

        self.gateway = gw
        self.port    = port
            
        self.aliases = {}

    def AddAlias(self,id,label):
        self.aliases[label] = id

    def GetEntity(self,alias):

        urid = alias
        if alias in self.aliases:
            urid = self.aliases[alias]

        url = self.gateway + ":" + self.port + "/v2/entities/" + urid
        headers = {"fiware-service":"openiot",
                   "fiware-servicepath":"/"}
        r = requests.get(url, headers=headers)

        if "error" in r.json(): return None

        entity = orion_entity("temp","temp")
        print(r.json())
        entity.SetData(r.json())

        return entity

    def GE(self,alias):
        return self.GetEntity(alias)

    def GetSubscriptions(self):
        url = self.gateway + ":" + self.port + "/v2/subscriptions"
        headers = {"fiware-service":"openiot",
                   "fiware-servicepath":"/"}
        
        r = requests.get(url, headers=headers)
        return r.json()

    def ListAllEntities(self):
        url = self.gateway + ":" + self.port + "/v2/entities?limit=100"
        headers = {"fiware-service":"openiot",
                   "fiware-servicepath":"/"}

        #print("URL",url)
        r = requests.get(url, headers=headers)
        #print("LISTING ENTITIES")
        #print(r.json())
        entity_list = []
        for key in r.json():
            entity_list.append( [key["id"], key["type"]] )

        return entity_list

    def EntitiesByType(self, type):
        url = self.gateway + ":" + self.port + "/v2/entities?type=" + type + "&limit=1000"
        headers = {"fiware-service":"openiot",
                   "fiware-servicepath":"/"}

        r = requests.get(url, headers=headers)
        return r.json()

    def EntitiesNearLocation(self, type, maxdistance, coords):

        url = self.gateway + ":" + self.port + "/v2/entities?type=" + type + \
         "&georel=near;maxDistance:" + str(maxdistance) + \
         "&geometry=point&coords=" + str(coords[1]) + "," + str(coords[0]) + "&limit=100"
        headers = {"fiware-service":"openiot",
                   "fiware-servicepath":"/"}

        r = requests.get(url, headers=headers)
        return r.json()

        # http://3.11.166.242:1026/v2/entities?type=NeutronProbe&georel=near;maxDistance:300&geometry=point&coords=-1.4674708525442828,51.52848815945248



    def DataframeAllEntities(self):
        url = self.gateway + ":" + self.port + "/v2/entities?limit=100"
        headers = {"fiware-service":"openiot",
                   "fiware-servicepath":"/"}

        r = requests.get(url, headers=headers)

        entity_list_df = {}
        entity_list_df["id"] = []
        entity_list_df["type"] = []

        for key in r.json():
            entity_list_df["id"].append( key["id"] )
            entity_list_df["type"].append( key["type"] )


        return pd.DataFrame(data=entity_list_df)


    def PrintAllEntities(self):
        url = self.gateway + ":" + self.port + "/v2/entities"
        headers = {"fiware-service":"openiot",
                   "fiware-servicepath":"/"}


        r = requests.get(url, headers=headers)

        print("------------- ORION STATE ----------------- ")
        for key in r.json():
            print('{:40}'.format(key["id"]), '{:10}'.format(key["type"]))
        print("------------------------------------------- ")
        return r.json()

    def CreateEntity(self, id, type):
        return orion_entity(id, type)

    def UploadEntity(self, entity):

        url = self.gateway + ":" + self.port + "/v2/entities"
        headers = {"Content-Type":"application/json",
                   "fiware-service":"openiot",
                   "fiware-servicepath":"/"}


        r = requests.post(url, headers=headers, json=entity.GetData())

        return

    def UpdateEntity(self, entity):

        tag = entity.GetEntityID()

        current = self.GetEntity(tag)
        dt = current.GetDifference(entity)

        url = self.gateway + ":" + self.port + "/v2/entities/" + tag + "/attrs"
        headers = {"Content-Type":"application/json",
                   "fiware-service":"openiot",
                   "fiware-servicepath":"/"}

        #print("UPDATE",url, headers, dt)
        r = requests.post(url, headers=headers, json=dt)
        #time.sleep(10)
        return

    def SV(self,entity,key,value):
        e = self.GetEntity(entity)
        e.SV(key,value)
        self.UpdateEntity(e)

    def CopyEntity(self,alias,alias2):

        urid = alias
        if alias in self.aliases:
            urid = self.aliases[alias]

        urid2 = alias2
        if alias2 in self.aliases:
            urid2 = self.aliases[alias2]

        entity = self.GetEntity(urid)
        entity.SetEntityID(urid2)

        return entity

    def DeleteEntity(self,alias):

        urid = alias
        if alias in self.aliases:
            urid = self.aliases[alias]

        url = self.gateway + ":" + self.port + "/v2/entities/" + urid
        headers = {"fiware-service":"openiot",
                   "fiware-servicepath":"/"}

        print("UPDATE",url, headers)
        r = requests.delete(url, headers=headers)
        return

    def CreateCommandSubscription(self, url, type, description):
        dt = {
            "description": description,
            "subject": {
                "entities": [{
                        "type": type,
                        "idPattern":"urn:ngsd-ld:*"
                }],
                "condition": { "attrs": ["command"] }
            },
            "notification": {
                "http": { "url": url },
                "metadata": ["dateCreated", "dateModified"],
                "attrs": ["command"]
            }
        }
        print("DT",dt)
        url = self.gateway + ":" + self.port + "/v2/subscriptions/"
        headers = {"fiware-service":"openiot",
                   "fiware-servicepath":"/"}

        r = requests.post(url, headers=headers, json=dt)
        raw_input("WAIT")
        return

    def CreateTypeSubscription(self, url, type, description, attributes=[]):
        dt = {
            "description": description,
            "subject": {
                "entities": [{
                        "type": type,
                        "idPattern":"urn*"
                }],
                "condition": { "attrs": [] }
            },
            "notification": {
                "http": { "url": url },
                "metadata": ["dateCreated", "dateModified"],
                "attrs": attributes,
                "onlyChangedAttrs":True
            }
        }
        print("DT",dt)
        url = self.gateway + ":" + self.port + "/v2/subscriptions/"
        headers = {"fiware-service":"openiot",
                   "fiware-servicepath":"/"}

        r = requests.post(url, headers=headers, json=dt)
        return

    def GetQLData(self,requestdata):

        url = self.gateway + ":4200/_sql"
        dt = {"stmt":requestdata}
        headers = {"fiware-service":"openiot",
                   "fiware-servicepath":"/"}
        r = requests.post(url, headers=headers, json=dt)

        print("REQEST",dt)
        return r.json()
