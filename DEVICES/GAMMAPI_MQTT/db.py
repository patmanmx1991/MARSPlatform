from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String, MetaData, Float
from sqlalchemy import select
from sqlalchemy.orm import Session
import sqlalchemy as db
from sqlalchemy import select, update

class dbhandler:

  def __init__(self, dblist):
    self.engines = {}
    self.sessions = {}
    self.metas = {}

    for key in dblist:
      self.engines[key] = create_engine('sqlite:////home/gammapi/DB/' + key + '.db', echo = False)
      self.sessions[key] = Session(self.engines[key])
      self.metas[key] = MetaData(bind=self.engines[key])
      db.MetaData.reflect( self.metas[key] )

      insp = db.inspect(self.engines[key])
      db_list = insp.get_table_names()
      print(key, db_list)

  def GetTable(self, db_name, table_name):
    eng = self.engines[db_name]
    met = self.metas[db_name]
    ses = self.sessions[db_name]
    table = db.Table( table_name, met, autoload=True, autoload_with=eng)
    return table

#order_by()
  def GetTableLast(self, db_name, table_name):
    eng = self.engines[db_name]
    met = self.metas[db_name]
    ses = self.sessions[db_name]
    table = db.Table( table_name, met, autoload=True, autoload_with=eng)
    query = db.select(table.columns).order_by(table.columns.i.desc())
    ResultSet = eng.execute(query).fetchall()[0]
    dicts = {}
    for i, key in enumerate(table.columns.keys()):
      dicts[key] = ResultSet[i]
    return dicts

  def GetTableAll(self, db_name, table_name):
    eng = self.engines[db_name]
    met = self.metas[db_name]
    ses = self.sessions[db_name]
    print("Getting all for ", db_name, table_name)
    table = db.Table( table_name, met, autoload=True, autoload_with=eng)
    print(table, table.columns)
    query = db.select(table.columns)
    print(table.columns.keys())

    ResultProxy = eng.execute(query)
    ResultSet = ResultProxy.fetchall()

    dicts = {}
    for i, key in enumerate(table.columns.keys()):
      dicts[key] = []
    
    print("DICTS",dicts)
    for set in ResultSet:
      for i, key in enumerate(table.columns.keys()):
        dicts[key].append( set[i] )

    return dicts

  def GetTableAllByRun(self, db_name, table_name,id):
    eng = self.engines[db_name]
    met = self.metas[db_name]
    ses = self.sessions[db_name]

    print("Getting all for ", db_name, table_name)
    table = db.Table( table_name, met, autoload=True, autoload_with=eng)
    print(table, table.columns)
    query = db.select(table.columns).where(table.c.run_tag == id)
    print(table.columns.keys())

    ResultProxy = eng.execute(query)
    ResultSet = ResultProxy.fetchall()

    dicts = {}
    for i, key in enumerate(table.columns.keys()):
      dicts[key] = []

    for set in ResultSet:
      for i, key in enumerate(table.columns.keys()):
        dicts[key].append( set[i] )

    return dicts


  def UpdateTableEntry(self, db_name, table_name, id, values):
    eng = self.engines[db_name]
    met = self.metas[db_name]
    ses = self.sessions[db_name]

    table = db.Table( table_name, met, autoload=True, autoload_with=eng)
    u = update(table).where(table.c.id == id).values(values)
    print(u)
    eng.execute(u)


  def GetTableEntry(self, db_name, table_name, id):
    eng = self.engines[db_name]
    met = self.metas[db_name]
    ses = self.sessions[db_name]

    table = db.Table( table_name, met, autoload=True, autoload_with=eng)
    query = db.select([table]).where( table.columns.id == id )

    try:
      ResultProxy = eng.execute(query)
      ResultSet = ResultProxy.fetchall()[0]
      dicts = {}
      for i, key in enumerate(table.columns.keys()):
        dicts[key] = ResultSet[i]
      return dicts
    except:
      return None

  def AddTable(self, db_name, table_name, structure):

    eng = self.engines[db_name]
    met = self.metas[db_name]
    ses = self.sessions[db_name]

    new_table = Table(
      table_name,
      met,
      **structure)

    met.create_all(eng)

  def AddEntry(self, db_name, table_name, values_dict):
    
    eng = self.engines[db_name]
    met = self.metas[db_name]
    ses = self.sessions[db_name]

    table = db.Table( table_name, met, autoload=True, autoload_with=eng)    
    ins = table.insert().values(
      **values_dict
    )
    conn = eng.connect()
    result = conn.execute(ins)

