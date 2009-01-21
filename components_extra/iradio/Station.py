class Station(object):

    def __init__(self):
    
        self.name = ""
        self.now_playing = ""
        self.path = ""
        self.resource = ""
        self.bitrate = ""


    def __cmp__(self, other):
    
        return cmp(self.name, other.name)

