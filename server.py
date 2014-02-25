#!/usr/local/bin/python

import requests
import json

REGIONAL_TRAINS = "http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Queue()?$filter=TrainType ne 'S-tog'"
DANISH_STATIONS = "http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Station()?$filter=CountryCode eq '86'"
INCIDENT_TO_CEN = "http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Queue()?$filter=StationUic eq '8600626' and TrainType ne 'S-tog'"
HEADERS = {'Accept': 'application/json'}

def main () :
  r = requests.get(INCIDENT_TO_CEN, headers=HEADERS)
  for station in r.json()['d'] :
    print json.dumps(station, indent = 4)
    #print station["UIC"] + " " + station["Name"]
  #r = requests.get(REGIONAL_TRAINS, headers=HEADERS)
  #print(r.text)


if __name__ == '__main__':
  main()