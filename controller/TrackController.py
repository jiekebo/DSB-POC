# -*- coding: utf-8 -*-

from Queue import Full
import multiprocessing
import time
import json

from py2neo import neo4j

from model.Track import Track


query_string = """
MATCH (source:STATION {{ UIC:"{}" }}),(target:STATION {{ UIC:"{}" }}),
p = shortestPath((source)-[*]-(target))
RETURN p
"""
graph_db = neo4j.GraphDatabaseService()


class TrackController(multiprocessing.Process):
    def __init__(self, in_queue, out_queue):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        self.trains = {}
        self.in_queue = in_queue
        self.out_queue = out_queue

    def update_tracks(self):
        trains = self.in_queue.get()

        tracks = []

        for train in trains.iteritems():
            train_number = train[0]
            train_stops = train[1]

            first_station = self._get_first_station(train_stops)
            destination = train_stops.itervalues().next().destination_uic

            track = Track()
            track.train = train_number

            if destination == 8600551 or destination == 8600512:
                result = self._get_shortest_path(first_station, destination)

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
                    tracks.append(json.dumps(track.__dict__))
        return json.dumps(tracks)


    @staticmethod
    def _get_shortest_path(start, stop):
        query = query_string.format(start, stop)
        return neo4j.CypherQuery(graph_db, query).execute()

    @staticmethod
    def _get_first_station(stations):
        sorted_stations = sorted(stations.iteritems(), key=lambda x: x[1].scheduled_arrival)
        return sorted_stations[0][0]

    def run(self):
        while not self.exit.is_set():
            try:
                self.out_queue.put_nowait(self.update_tracks())
            except Full:
                print "queue is full"
            time.sleep(5)
        print "Process exited"

    def shutdown(self):
        print "Shutdown initiated"
        self.exit.set()