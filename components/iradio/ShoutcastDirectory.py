from Station import Station
from io import Downloader


_SHOUTCAST_BASE = "http://www.shoutcast.com"


class ShoutcastDirectory(object):

    def __init__(self):
    
        # table: genre_path -> genre_name
        self.__genres = {}
        
        
    def __parse_genres(self, data):

        # find genre list
        idx = data.find(">Stations by Genre</span>")
        idx1 = data.find("<li>", idx)
        idx2 = data.find("setUpRadio")
        data = data[idx1:idx2]

        # read genre by genre
        pos = 0
        self.__genres = {}
        while (True):
            pos = data.find("/genre/", pos)
            if (pos == -1): break
            
            pos1 = pos + len("/genre/")
            pos2 = data.find("'", pos1)
            genre_path = data[pos1:pos2]
            
            pos1 = data.find(">", pos2)
            pos2 = data.find("<", pos1)
            genre_name = data[pos1 + 1:pos2].strip()
            
            self.__genres[genre_path] = genre_name
            
            pos = pos2
        #end while



    def __parse_stations(self, data, cb):

        pos = 0
        while (True):
            pos = data.find("dirTuneMoreDiv", pos)
            print pos
            if (pos == -1): break
            
            # URL
            pos = data.find("<a href=", pos)
            pos1 = data.find("\"", pos)
            pos2 = data.find("\"", pos1 + 1)
            pls_url = data[pos1 + 1:pos2]
            pos = pos2
            
            # Name
            pos = data.find("dirStationCnt", pos)
            pos = data.find("<a", pos)
            pos1 = data.find(">", pos)
            pos2 = data.find("<", pos1)
            name = data[pos1 + 1:pos2].strip()
            pos = pos2
            
            # Now Playing            
            pos = data.find("dirNowPlayingCnt", pos)
            pos = data.find("<span", pos)
            pos1 = data.find(">", pos)
            pos2 = data.find("<", pos1)
            now_playing = data[pos1 + 1:pos2].strip()
            pos = pos2

            # build station object
            station = Station()
            station.name = name
            station.now_playing = now_playing
            station.resource = pls_url
            #station.bitrate = bitrate
            
            cb(True, station)
        #end while

        cb(False, None)
        
        
        
    def get_path(self, path, cb):
    
        def on_load(d, amount, total, data):
            if (d):
                data[0] += d
            else:
                #open("/tmp/shoutcast-genres.html", "w").write(data[0])
                self.__parse_genres(data[0])
                if (self.__genres):
                    self.__list_path(path, cb)

    
        if (path and path[0] == "/"): path = path[1:]

        print "GET PATH", path
        if (not path and not self.__genres):
            #on_load("", 0, 0, [open("/tmp/shoutcast-genres.html").read()])
            dl = Downloader(_SHOUTCAST_BASE + "/", on_load, [""])            
        else:
            self.__list_path(path, cb)


    def __list_path(self, path, cb):

        def on_load(d, amount, total, data):
            if (d):
                data[0] += d
            else:
                #open("/tmp/shoutcast-stations.html", "w").write(data[0])
                self.__parse_stations(data[0], cb)


        if (not path):
            # list genres
            items = self.__genres.items()
            items.sort(lambda a,b:cmp(a[1],b[1]))
            for p, n in items:
                station = Station()
                station.name = n
                station.path = p

                cb(False, station)
            #end for
            cb(False, None)
                
        else:
            # list stations
            #on_load("", 0, 0, [open("/tmp/shoutcast-stations.html").read()])
            #return
            name = self.__genres[path]
            dl = Downloader(_SHOUTCAST_BASE + \
                "/directory/genreSearchResult.jsp?startIndex=1&" \
                "mode=listeners&maxbitrate=all&sgenre=%s" % name,
                #"/genre/%s?numresult=25&startat=0" % name,
                on_load, [""])

