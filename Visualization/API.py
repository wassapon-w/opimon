import json
import csv
import string
import pymongo
from pymongo import MongoClient

def main():
    client = MongoClient("mongodb://localhost:27017")
    db = client.opimon
    topologyRaw = db.topology.find()
    flowmodsRaw = db.flow_mods.find()

    topology = []
    flowmods = []

    for document in topologyRaw:
        doc = []
        doc.append(document["timestamp"])
        doc.append(document["switch_src"])
        doc.append(document["port_src"])
        doc.append(document["switch_dst"])
        doc.append(document["port_dst"])
        topology.append(doc)

    # for document in flowmodsRaw:

    out = open("topology.csv", "wb")
    writer = csv.writer(out)
    for i in range(len(topology)):
		writer.writerow(topology[i])
    print "Saved topology.csv"

    out = open("flowmods.csv", "wb")
    writer = csv.writer(out)
    for i in range(len(flowmods)):
        writer.writerow(flowmods[i])
    print "Saved flowmods.csv"

if __name__ == '__main__':
	main()
