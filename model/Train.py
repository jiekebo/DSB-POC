import datetime
import re


class Train:
    def __init__(self, id, trainType, trainNumber, stationUic, direction,
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

    def _convertTimestamp(self, str):
        timestamp = re.findall('\d+', str)
        return datetime.fromtimestamp(int(timestamp[0]) / 1000).strftime("%Y-%m-%d %H:%M:%S")

    def toString(self, showStations=False):
        arrival = ""
        if self.scheduledArrival:
            arrival = self._convertTimestamp(self.scheduledArrival)
        string = """Train: %s, Id: %s, Destination: %s, Type: %s, Station: %s, Arrival: %s\n""" % (
        self.trainNumber, self.id, self.destinationName, self.trainType, self.stationUic, arrival)
        return string

    def __repr__(self):
        return "{{trainNumber:{}, id:{}}}".format(
            self.trainNumber,
            self.id)