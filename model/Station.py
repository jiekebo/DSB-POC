class Station:
    def __init__(self, uic, name, abbreviation, country_name, country_code):
        self.uic = uic
        self.name = name
        self.abbreviation = abbreviation
        self.country_name = country_name
        self.country_code = country_code
        self.trains = []

    def addTrain(self, train):
        self.trains.append(train)

    def toString(self, showTrains=False):
        string = "Station: " + self.name + " UIC: " + self.uic
        if not showTrains:
            return string
        string += " Trains: \n"
        for train in self.trains:
            string += "\t" + train.toString() + "\n"
        return string