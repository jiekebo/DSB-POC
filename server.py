#!/usr/bin/python
# -*- coding: utf-8 -*-

import multiprocessing
import json
import sys

from py2neo import neo4j

from controller.TrainController import TrainController
from controller.SocketServer import SocketServer
from model.Track import Track

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
            train_number = train[0]
            train_stops = train[1]

            first_station = get_first_station(train_stops)
            destination = train_stops.itervalues().next().destination_uic

            track = Track()
            track.train = train_number

            if destination == 8600551 or destination == 8600512:
                result = get_shortest_path(first_station, destination)

                if result.data:
                    """
                    print train_number
                    print train_stops
                    print result.data
                    """
                    for node in result.data[0].p.nodes:
                        node_properties = node.get_properties()
                        node_uic = node_properties['UIC']
                        try:
                            train = train_stops[node_uic]
                            node_properties['time'] = train.scheduled_arrival
                            track.stations.append(node_properties)
                        except KeyError as e:
                            track.stations.append(node_properties)
                    for relation in result.data[0].p.relationships:
                        start = relation.start_node.get_properties()['UIC']
                        end = relation.end_node.get_properties()['UIC']
                        track.edges.append({"start": start, "end": end})
                    print json.dumps(track.__dict__, indent=4)


def get_shortest_path(start, stop):
    query = query_string.format(start, stop)
    return neo4j.CypherQuery(graph_db, query).execute()


def get_first_station(stations):
    sorted_stations = sorted(stations.iteritems(), key=lambda x: x[1].scheduled_arrival)
    return sorted_stations[0][0]


if __name__ == '__main__':
    #signal.signal(signal.SIGTERM, signalHandler)
    #signal.signal(signal.SIGINT, signalHandler)

    trainController.start()
    neoProcess = multiprocessing.Process(target=neo, args=(queue,))
    neoProcess.start()

    #socketServer.start()