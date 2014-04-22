# -*- coding: utf-8 -*-


class Track:
    def __init__(self):
        self.train = 0
        self.stations = []
        self.edges = []

    def __repr__(self):
        return u"{{\n\ttrain:{}\n\tstations:{}\n\tedges:{}\n}}".format(self.train, self.stations, self.edges)