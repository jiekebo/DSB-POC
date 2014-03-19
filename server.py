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

    """
    8600551
    8600512
    """

def neo(queue):
    while True:
        trains = queue.get()

        for train in trains.iteritems():
            trainNumber = train[0]
            trainStops = train[1]

            for stop in trainStops.iteritems():
                if stop[1].destinationID == 8600551 or stop[1].destinationID == 8600512:
                    print "Stops for train " + trainNumber + ":"
                    sortedStopTimes = trainStops.keys()
                    sortedStopTimes.sort()
                    for time in sortedStopTimes:
                        station = trainStops[time]
                        print station

                    graph_db = neo4j.GraphDatabaseService()
                    query_string = """
                    MATCH (source:STATION {{ UIC:"{}" }}),(target:STATION {{ UIC:"{}" }}),
                    p = shortestPath((source)-[*]-(target))
                    RETURN p
                    """.format(trainStops[sortedStopTimes[0]].stationUic, stop[1].destinationID)
                    result = neo4j.CypherQuery(graph_db, query_string).execute()
                    for r in result:
                        print type(r)  # r is a py2neo.util.Record object
                        print type(r.p)  # p is a py2neo.neo4j.Path object
                        print r.p
                        #for node in r.p.nodes:
                        #  print node['UIC']


if __name__ == '__main__':
    #signal.signal(signal.SIGTERM, signalHandler)
    #signal.signal(signal.SIGINT, signalHandler)

    trainController.start()
    neoProcess = multiprocessing.Process(target=neo, args=(queue,))
    neoProcess.start()

    #socketServer.start()