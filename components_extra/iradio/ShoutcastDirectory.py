from Station import Station
from io import Downloader
from xml.etree import ElementTree
from cStringIO import StringIO
import urllib

_SHOUTCAST_BASE = "http://www.shoutcast.com"

class ShoutcastDirectory(object):

    def __init__(self):

        # genre list
        self.__genres = []
        # station list for each genre
        self.__stations = {}

    def __parse_genres(self, data):
        print '__parse_genres'
        #print data
        self.__genres = []
        try:
            dtree = ElementTree.parse(StringIO(data))
            for i in dtree.getiterator():
                if i.tag == "genre":
                    for j,n in i.items():
                        if j == "name":
                            self.__genres.append(n)
                            self.__stations[n] = []
        except:
            print 'shoutcast genre listing download failed'

    def __parse_stations(self, data, genre):
        print '__parse_stations', genre
        stations = []
        try:
            dtree = ElementTree.parse(StringIO(data))
            for i in dtree.getiterator():
                if i.tag == "station":
                    # build station object
                    station = Station()
                    for j,n in i.items():
                        if j == "name":
                            station.name = n
                        elif j == "ct":
                            station.now_playing = n
                        elif j == "id":
                            station.resource = _SHOUTCAST_BASE + "/sbin/shoutcast-playlist.pls?rn=%s&file=filename.pls" % n
                        elif j == "br":
                            station.bitrate = n
                    stations.append(station)
                #cb(True, station)
        except:
            print 'shoutcast listing download failed'

        #stations.sort()
        self.__stations[genre] = stations

    def get_path(self, path, cb):

        def on_load(d, amount, total, data):
            if (d):
                data[0] += d
            else:
                #open("/tmp/shoutcast-genres.html", "w").write(data[0])
                self.__parse_genres(data[0])
                #if (self.__genres):
                self.__list_path(path, cb)

        if (path and path[0] == "/"): path = path[1:]

        if (not path and not self.__genres):
            #on_load("", 0, 0, [open("/tmp/shoutcast-genres.html").read()])
            dl = Downloader(_SHOUTCAST_BASE + "/sbin/newxml.phtml", on_load, [""])
        else:
            self.__list_path(path, cb)

    def __list_path(self, path, cb):

        def on_load(d, amount, total, data):
            if (d):
                data[0] += d
            else:
                #open("/tmp/shoutcast-stations.html", "w").write(data[0])
                self.__parse_stations(data[0], data[1])
                if self.__stations[data[1]]:
                    for s in self.__stations[data[1]]:
                        cb(True, s)
                cb(False, None)

        if (not path):
            # list genres
            for n in self.__genres:
                station = Station()
                station.name = n
                station.path = n

                cb(False, station)
            #end for
            cb(False, None)

        else:
            # list stations
            #on_load("", 0, 0, [open("/tmp/shoutcast-stations.html").read()])
            #return
            if not self.__stations[path]:
                name = urllib.quote(path)
                dl = Downloader(_SHOUTCAST_BASE + "/sbin/newxml.phtml?genre=%s" % name, on_load, ["",path])
            else:
                for station in self.__stations[path]:
                    cb(True, station)
                cb(False, None)

