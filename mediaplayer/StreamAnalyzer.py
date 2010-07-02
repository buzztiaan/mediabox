from utils import logging
import urllib


class StreamAnalyzer(object):
    """
    Analyzer for media streams so that we don't get a playlist where we expected
    media data.
    """

    PLAYLIST = 0
    STREAM = 1
    ATOM_FEED = 2
    

    def __init__(self):
    
        pass

        
    def analyze(self, url):
    
        try:
            fd = urllib.urlopen(url)
        except:
            return
        data = fd.read(1024).strip()
        fd.close()
        
        out = ""
        for d in data:
            if (33 <= ord(d) <= 127):
                out += d
            else:
                out += "\\%03d" % ord(d)
        #end for
        logging.debug("Analyzing stream:\n%s", out)

        if (data.startswith("[playlist]")):
            return self.PLAYLIST

        elif (data.startswith("<?xml")):
            if ("http://www.w3.org/2005/Atom" in data):
                return self.ATOM_FEED
                
        elif (data.startswith("FLV")):
            return self.STREAM
    
        else:
            return self.STREAM

