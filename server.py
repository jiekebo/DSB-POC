#!/usr/bin/python

import requests
import json
from datetime import datetime
import re
import time
import urllib

REGIONAL_TRAINS = "http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Queue()?$filter=TrainType ne 'S-tog'"
DANISH_STATIONS = "http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Station()?$filter=CountryCode eq '86'"
STATIONS = "http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Station()"
INCIDENT_TO_CEN = "http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Queue()?$filter=StationUic eq '8600626' and TrainType ne 'S-tog'"
HEADERS = {'Accept': 'application/json'}

class Station : 
  def __init__ (self, uic, name, abbreviation, countryName, countryCode) : 
    self.uic = uic
    self.name = name
    self.abbreviation = abbreviation
    self.countryName = countryName
    self.countryCode = countryCode
    self.trains = []

  def addTrain (self, train) : 
    self.trains.append(train)

  def toString (self, showTrains = False) : 
    string = "Station: " + self.name + " UIC: " + self.uic
    if not showTrains :
      return string
    string += " Trains: \n"
    for train in self.trains : 
      string += "\t" + train.toString() + "\n"
    return string

class Train:
  def __init__ (self, id, trainType, trainNumber, stationUic, direction, 
    track, line, destinationID, destinationName, destinationCountryCode, 
    generated, scheduledArrival, arrivalDelay, scheduledDeparture, 
    minutesToDeparture, departureDelay, cancelled):
    # Train identification
    self.id = id
    self.trainType = trainType
    self.trainNumber = trainNumber

    # Train location
    self.stationUic = stationUic
    self.direction = direction
    self.track = track
    self.line = line
    
    # Train destination
    self.destinationID = destinationID
    self.destinationName = destinationName
    self.destinationCountryCode = destinationCountryCode
    
    # Train schedule
    self.generated = generated
    self.scheduledArrival = scheduledArrival
    self.arrivalDelay = arrivalDelay
    self.scheduledDeparture = scheduledDeparture
    self.minutesToDeparture = minutesToDeparture
    self.departureDelay = departureDelay
    self.cancelled = cancelled

  def _convertTimestamp (self, str) : 
    timestamp = re.findall('\d+', str)
    return datetime.fromtimestamp(int(timestamp[0])/1000).strftime("%Y-%m-%d %H:%M:%S")

  def toString (self, showStations = False) : 
    arrival = ""
    if(self.scheduledArrival) :
      arrival = self._convertTimestamp(self.scheduledArrival)
    string =  """Train: %s, Id: %s, Destination: %s, Type: %s, Station: %s, Arrival: %s\n""" % (self.trainNumber, self.id, self.destinationName, self.trainType, self.stationUic, arrival)

    return string

class StationController: 
  def __init__ (self) : 
    stationResponse = requests.get(STATIONS, headers=HEADERS)
    self.stations = {}
    for station in stationResponse.json()['d'] :
      self.stations[station['UIC']] = Station(station['UIC'], station['Name'], station['Abbreviation'], station['CountryName'], station['CountryCode'])

  def getStation (self, uid) : 
    try : 
      return self.stations[uid]
    except KeyError as e : 
      print e

class TrainController : 
  def __init__ (self) : 
    self.trains = {}

  """
  Structure:
  trainNumber
  -- id, trainObject
  -- id, trainObject
  trainNumber
  -- id, trainObject
  """
  def updateTrains (self) : 
    print "requesting train data"
    try : 
      trainResponse = requests.get(REGIONAL_TRAINS, headers=HEADERS, timeout=1)
    except (requests.exceptions.Timeout, urllib.error.URLError) as e :
      return
    print "got response for " + str(len(trainResponse.json()['d'])) + " updates"
    
    updatedTrains = []
    for train in trainResponse.json()['d'] : 
      trainObject = Train(train['ID'], train['TrainType'], train['TrainNumber'], train['StationUic'], train['Direction'], 
        train['Track'], train['Line'], train['DestinationID'], train['DestinationName'], train['DestinationCountryCode'],
        train['Generated'], train['ScheduledArrival'], train['ArrivalDelay'], train['ScheduledDeparture'],
        train['MinutesToDeparture'], train['DepartureDelay'], train['Cancelled'])
      updatedTrains.append(trainObject.trainNumber)
      try :
        self.trains[trainObject.trainNumber][trainObject.id] = trainObject
      except KeyError as e : 
        self.trains[trainObject.trainNumber] = {}
        self.trains[trainObject.trainNumber][trainObject.id] = trainObject
    
    print "total trains " + str(len(self.trains))
    trainsForRemoval = list(set(self.trains.keys()) - set(updatedTrains))
    print "removing trains " + str(len(trainsForRemoval))
    for removal in trainsForRemoval : 
      del self.trains[removal]

  def getTrain (self, trainNumber) : 
    return self.trains[trainNumber]

  def getAllTrains (self) : 
    return self.trains

def main () : 
  stationController = StationController()
  trainController = TrainController()
  while True:
    trainController.updateTrains()
    time.sleep(3)

  f = open('data/trainStations.txt', 'w')
  for key, value in trainController.getAllTrains().items() : 
    for key, train in value.items() : 
      f.write(train.toString(False).encode('UTF-8'))
  f.close()

  """
  try :
    savedTrain = trains[trainObject.trainNumber]
    savedTrain.addStation(trainObject.scheduledArrival, stations[trainObject.stationUic])
  except KeyError as e:
    try :
      trainObject.addStation(trainObject.scheduledArrival, stations[trainObject.stationUic])
      trains[trainObject.trainNumber] = trainObject
    except KeyError as e:
      print e


  f = open('data/stationTrains.txt', 'w')
  for key, value in stations.items() :
    f.write(value.toString(True).encode('UTF-8'))
  f.close()
  """

if __name__ == '__main__' : 
  main()