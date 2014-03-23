# -*- coding: utf-8 -*-

import datetime
import re


class Train:
    def __init__(self, id, train_type, train_number, station_uic, direction,
                 track, line, destination_uic, destination_name, destination_country_code,
                 generated, scheduled_arrival, arrival_delay, scheduled_departure,
                 minutes_to_departure, departure_delay, cancelled):
        # Train identification
        self.id = id
        self.train_type = train_type
        self.train_number = train_number

        # Train location
        self.station_uic = station_uic
        self.direction = direction
        self.track = track
        self.line = line

        # Train destination
        self.destination_uic = destination_uic
        self.destination_name = destination_name
        self.destination_country_code = destination_country_code

        # Train schedule
        self.generated = generated
        self.scheduled_arrival = scheduled_arrival
        self.arrival_delay = arrival_delay
        self.scheduled_departure = scheduled_departure
        self.minutes_to_departure = minutes_to_departure
        self.departure_delay = departure_delay
        self.cancelled = cancelled

    @staticmethod
    def _convert_timestamp(str):
        if str is None:
            return None
        timestamp = re.findall('\d+', str)
        return datetime.datetime.fromtimestamp(int(timestamp[0]) / 1000).strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self):
        return u"{{train_number:{}, station:{}, arrival:{}, end:{}}}".format(
            self.train_number,
            self.station_uic,
            self._convert_timestamp(self.scheduled_arrival),
            self.destination_uic)