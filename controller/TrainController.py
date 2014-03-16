import multiprocessing
import requests
import time
import sys

from model.Train import Train

REGIONAL_TRAINS = "http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Queue()?$filter=TrainType ne 'S-tog'"
DANISH_STATIONS = "http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Station()?$filter=CountryCode eq '86'"
STATIONS = "http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Station()"
INCIDENT_TO_CEN = "http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Queue()?$filter=StationUic eq '8600626' and TrainType ne 'S-tog'"
HEADERS = {'Accept': 'application/json'}

class TrainController(multiprocessing.Process):
  def __init__ (self, queue):
    multiprocessing.Process.__init__(self)
    self.exit = multiprocessing.Event()
    self.trains = {}
    self._q = queue

  """
  Structure:
  trainNumber
  -- id, trainObject
  -- id, trainObject
  trainNumber
  -- id, trainObject
  """
  def updateTrains(self):
    print "requesting train data"
    try : 
      trainResponse = requests.get(REGIONAL_TRAINS, headers=HEADERS, timeout=1)
    except:
      print "Unexpected error:", sys.exc_info()[0]
      return
    print "got response for " + str(len(trainResponse.json()['d'])) + " updates"
    
    updatedTrains = []
    for train in trainResponse.json()['d']:
      trainObject = Train(train['ID'], train['TrainType'], train['TrainNumber'], train['StationUic'], train['Direction'], 
        train['Track'], train['Line'], train['DestinationID'], train['DestinationName'], train['DestinationCountryCode'],
        train['Generated'], train['ScheduledArrival'], train['ArrivalDelay'], train['ScheduledDeparture'],
        train['MinutesToDeparture'], train['DepartureDelay'], train['Cancelled'])
      updatedTrains.append(trainObject.trainNumber)
      try:
        self.trains[trainObject.trainNumber][trainObject.id] = trainObject
      except KeyError as e: 
        self.trains[trainObject.trainNumber] = {}
        self.trains[trainObject.trainNumber][trainObject.id] = trainObject
    
    print "total trains " + str(len(self.trains))
    trainsForRemoval = list(set(self.trains.keys()) - set(updatedTrains))
    print "removing trains " + str(len(trainsForRemoval))
    for removal in trainsForRemoval:
      del self.trains[removal]

  def run(self):
    while not self.exit.is_set():
      self.updateTrains()
      try:
        self._q.put_nowait(self.trains)
      except:
        print "queue is full"
      time.sleep(5)
    print "Process exited"

  def shutdown(self):
    print "Shutdown initiated"
    self.exit.set()