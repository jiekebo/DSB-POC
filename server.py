#!/usr/bin/python

import requests
import json
from datetime import datetime
import re

REGIONAL_TRAINS = "http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Queue()?$filter=TrainType ne 'S-tog'"
DANISH_STATIONS = "http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Station()?$filter=CountryCode eq '86'"
NON_DANISH_STATIONS = "http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Station()?$filter=CountryCode ne '86'"
INCIDENT_TO_CEN = "http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Queue()?$filter=StationUic eq '8600626' and TrainType ne 'S-tog'"
HEADERS = {'Accept': 'application/json'}

class Station:
  def __init__ (self, uic, name, abbreviation, countryName, countryCode) : 
    self.uic = uic
    self.name = name
    self.abbreviation = abbreviation
    self.countryName = countryName
    self.countryCode = countryCode
    self.trains = []

  def addTrain(self, train) : 
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

    # Strain stations
    self.stations = {}

  def addStation(self, time, station) : 
    self.stations[time] = station

  def _convertTimestamp (self, str) :
    timestamp = re.findall('\d+', str)
    return datetime.fromtimestamp(int(timestamp[0])/1000)

  def toString (self, showStations = False) :
    string = "Train: " + self.trainNumber + ", Destination: " + self.destinationName
    if not showStations :
      return string
    string += " Stations: \n"
    for key in sorted(self.stations.iterkeys()) : 
      if key == None :
        #string += "\t" + .toString() + "\n"
        pass
      else :
        string += "\t" + self._convertTimestamp(key).strftime("%Y-%m-%d %H:%M:%S") + " - " + self.stations[key].toString() + "\n"
    return string


def main () :
  stationResponse = requests.get(NON_DANISH_STATIONS, headers=HEADERS)
  stations = {}
  for station in stationResponse.json()['d'] :
    stations[station['UIC']] = Station(station['UIC'], station['Name'], station['Abbreviation'], station['CountryName'], station['CountryCode'])

  trains = {}
  trainResponse = requests.get(REGIONAL_TRAINS, headers=HEADERS)
  for train in trainResponse.json()['d']:
    trainObject = Train(train['ID'], train['TrainType'], train['TrainNumber'], train['StationUic'], train['Direction'], 
      train['Track'], train['Line'], train['DestinationID'], train['DestinationName'], train['DestinationCountryCode'],
      train['Generated'], train['ScheduledArrival'], train['ArrivalDelay'], train['ScheduledDeparture'],
      train['MinutesToDeparture'], train['DepartureDelay'], train['Cancelled'])
    try :
      stations[train['StationUic']].addTrain(trainObject)
    except KeyError as e:
      print e

    try :
      savedTrain = trains[trainObject.trainNumber]
      savedTrain.addStation(trainObject.scheduledArrival, stations[trainObject.stationUic])
    except KeyError as e:
      try: 
        trainObject.addStation(trainObject.scheduledArrival, stations[trainObject.stationUic])
        trains[trainObject.trainNumber] = trainObject
      except KeyError as e:
        print e

  f = open('data/stationTrains.txt', 'w')
  for key, value in stations.items() :
    f.write(value.toString(True).encode('UTF-8'))
  f.close()

  f = open('data/trainStations.txt', 'w')
  for key, value in trains.items() : 
    f.write(value.toString(True).encode('UTF-8'))
  f.close()

if __name__ == '__main__' :
  main()