import pymongo
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.opimon
topology = db.topology.find()
flow_mods = db.flow_mods.find()

for document in topology:
    print document
