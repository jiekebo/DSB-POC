# -*- coding: utf-8 -*-

from Queue import Full
import multiprocessing
import time
import sys

import requests

from model.Train import Train


REGIONAL_TRAINS = "http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Queue()?$filter=TrainType ne 'S-tog'"
HEADERS = {'Accept': 'application/json'}


class TrainController(multiprocessing.Process):
    def __init__(self, queue):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        self.trains = {}
        self._q = queue

    def update_trains(self):
        print "requesting train data"
        try:
            train_response = requests.get(REGIONAL_TRAINS, headers=HEADERS, timeout=1)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return
        print "got response for " + str(len(train_response.json()['d'])) + " updates"

        updated_trains = []
        for train in train_response.json()['d']:
            train_object = Train(train['ID'], train['TrainType'], train['TrainNumber'], train['StationUic'],
                                 train['Direction'],
                                 train['Track'], train['Line'], train['DestinationID'], train['DestinationName'],
                                 train['DestinationCountryCode'],
                                 train['Generated'], train['ScheduledArrival'], train['ArrivalDelay'],
                                 train['ScheduledDeparture'],
                                 train['MinutesToDeparture'], train['DepartureDelay'], train['Cancelled'])
            updated_trains.append(train_object.train_number)
            try:
                self.trains[train_object.train_number][train_object.station_uic] = train_object
            except KeyError as e:
                self.trains[train_object.train_number] = {}
                self.trains[train_object.train_number][train_object.station_uic] = train_object

        print "total trains " + str(len(self.trains))
        trains_for_removal = list(set(self.trains.keys()) - set(updated_trains))
        print "removing trains " + str(len(trains_for_removal))
        for removal in trains_for_removal:
            del self.trains[removal]

    def run(self):
        while not self.exit.is_set():
            self.update_trains()
            try:
                self._q.put_nowait(self.trains)
            except Full:
                print "queue is full"
            time.sleep(5)
        print "Process exited"

    def shutdown(self):
        self.exit.set()