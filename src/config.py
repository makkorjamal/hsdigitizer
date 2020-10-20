import configparser as cp

class SpectraConfig:

    def __init__():

        self.workingPath = ''
        self.solarAzimuthAngle = 0
        self.signalNoiseRatio = 100
        self.dateAndTime = '01/01/1958 00:00'
        self.spectralRange = [0, 0]
        self.apodisation = 'TRI'
        self.rEarth = 6371
        self.latitudeAndLongitude = []
        self.resolution = 0.1
        self.config = cp.ConfigParser()
