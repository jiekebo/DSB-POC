#!/usr/bin/python
# -*- coding: utf-8 -*-

import multiprocessing
import sys

from py2neo import neo4j

from controller.TrainController import TrainController
from controller.SocketServer import SocketServer

queue = multiprocessing.Queue(1)
trainController = TrainController(queue)
socketServer = SocketServer(queue)


def signalHandler(sig, frame):
    trainController.shutdown()
    socketServer.shutdown()
    sys.exit(0)


def neo():
    graph_db = neo4j.GraphDatabaseService()
    query_string = """
    MATCH (nivå:STATION { name:"Nivå" }),(malmö:STATION { name:"Malmö Central" }),
    p = shortestPath((nivå)-[*..15{line:"kystbanen"}]-(malmö))
    RETURN p
    """
    result = neo4j.CypherQuery(graph_db, query_string).execute()
    for r in result:
        print type(r) # r is a py2neo.util.Record object
        print type(r.p) # p is a py2neo.neo4j.Path object
        print r.p
        #for node in r.p.nodes:
        #  print node['UIC']


if __name__ == '__main__':
    #neo()
    #signal.signal(signal.SIGTERM, signalHandler)
    #signal.signal(signal.SIGINT, signalHandler)

    trainController.start()
    #socketServer.start()