import requests
from model.Station import Station


STATIONS = "http://traindata.dsb.dk/stationdeparture/opendataprotocol.svc/Station()"
HEADERS = {'Accept': 'application/json'}


class StationController:
    def __init__(self):
        stationResponse = requests.get(STATIONS, headers=HEADERS)
        self.stations = {}
        for station in stationResponse.json()['d']:
            self.stations[station['UIC']] = Station(station['UIC'], station['Name'], station['Abbreviation'],
                                                    station['CountryName'], station['CountryCode'])

    def getStation(self, uid):
        try:
            return self.stations[uid]
        except KeyError as e:
            print e