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

query_string = """
MATCH (source:STATION {{ UIC:"{}" }}),(target:STATION {{ UIC:"{}" }}),
p = shortestPath((source)-[*]-(target))
RETURN p
"""
graph_db = neo4j.GraphDatabaseService()


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

                    query = query_string.format(trainStops[sortedStopTimes[0]].stationUic, stop[1].destinationID)
                    neoResult = neo4j.CypherQuery(graph_db, query).execute()

                    if neoResult.data:
                        nodes = neoResult.data[0].p.nodes
                        print nodes
                        for stop in trainStops.values():
                            print stop.stationUic



#                    for time in sortedStopTimes:
#                        station = trainStops[time]
#                        print station
#
#                    for r in neoResult:
#                        for node in r.p.nodes:
#                            print node['UIC'] + " " + node['name']


if __name__ == '__main__':
    #signal.signal(signal.SIGTERM, signalHandler)
    #signal.signal(signal.SIGINT, signalHandler)

    trainController.start()
    neoProcess = multiprocessing.Process(target=neo, args=(queue,))
    neoProcess.start()

    #socketServer.start()