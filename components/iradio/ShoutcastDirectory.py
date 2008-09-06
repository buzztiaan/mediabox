from Station import Station
from io import Downloader


_SHOUTCAST_BASE = "http://www.shoutcast.com"


class ShoutcastDirectory(object):

    def __init__(self):
    
        # table: path -> (name, [sub_paths])
        self.__genres = {}
        
        
        
    def __parse_genres(self, data):

        # find genre list
        idx = data.find("class=\"SearchBox\"")
        idx1 = data.find("<SELECT name=\"sgenre\"", idx)
        idx2 = data.find("</SELECT>", idx1)
        genre_data = data[idx1:idx2]
        
        # read genre by genre
        pos = 0
        current_main_genre = ""
        self.__genres = {}
        self.__genres[""] = ("", [])
        while (True):
            pos = genre_data.find("<OPTION", pos)
            if (pos == -1): break

            pos = genre_data.find("VALUE=", pos)
            pos1 = genre_data.find("\"", pos)
            pos2 = genre_data.find("\"", pos1 + 1)
            genre_name = genre_data[pos1 + 1:pos2]
            
            pos = genre_data.find(">", pos2)
            
            if (not genre_name):
                continue
            
            if (genre_data[pos + 2] == "="):
                # uninteresting
                continue
            elif (genre_data[pos + 1] == "-"):
                # subgenre
                path = current_main_genre + "/" + genre_name
                self.__genres[current_main_genre][1].append(path)
                self.__genres[path] = (genre_name, [])
            else:
                # main genre
                path = genre_name
                self.__genres[""][1].append(path)
                self.__genres[path] = (genre_name, [])
                current_main_genre = genre_name
        #end while



    def __parse_stations(self, data, cb):

        pos = 0
        while (True):
            pos = data.find("/sbin/shoutcast-playlist.pls?", pos)
            if (pos == -1): break
            
            # URL
            pos1 = pos
            pos2 = data.find("\"", pos1)
            pls_url = data[pos1:pos2]
            pos = pos2 + 1
            
            # Name
            pos = data.find("id=\"listlinks\"", pos)
            pos1 = data.find(">", pos)
            pos2 = data.find("<", pos1)
            name = data[pos1 + 1:pos2].strip()
            pos = pos2 + 1
            
            # Now Playing            
            pos1 = data.find("Now Playing:", pos)
            pos2 = data.find("#FFFFFF", pos)
            if (pos1 < pos2):
                pos1 = data.find(">", pos1)
                pos2 = data.find("<", pos1)
                now_playing = data[pos1 + 1:pos2].strip()
                pos = pos2 + 1
            else:
                now_playing = ""
            
            # Bitrate
            pos = data.find("#FFFFFF", pos)
            pos = data.find("#FFFFFF", pos + 1)
            pos1 = data.find(">", pos)
            pos2 = data.find("<", pos1)
            bitrate = data[pos1 + 1:pos2]
            pos = pos2 + 1

            # build station object
            station = Station()
            station.name = name
            station.now_playing = now_playing
            station.resource = "http://www.shoutcast.com" + pls_url
            station.bitrate = bitrate
            
            cb(True, station)
        #end while

        cb(False, None)
        
        
        
    def get_path(self, path, cb):
    
        def on_load(d, amount, total, data):
            if (d):
                data[0] += d
            else:
                self.__parse_genres(data[0])
                if (self.__genres):
                    self.__list_path(path, cb)

    
        if (path and path[0] == "/"): path = path[1:]

        if (not path and not self.__genres):
            dl = Downloader(_SHOUTCAST_BASE + "/directory", on_load, [""])
        else:
            self.__list_path(path, cb)


    def __list_path(self, path, cb):

        def on_load(d, amount, total, data):
            if (d):
                data[0] += d
            else:
                self.__parse_stations(data[0], cb)


        name, subs = self.__genres[path]
        if (subs):
            # list genres
            for s in subs:
                name, ssubs = self.__genres[s]

                station = Station()
                station.name = name
                station.path = s

                cb(False, station)
            #end for
            cb(False, None)
                
        else:
            # list stations
            dl = Downloader(_SHOUTCAST_BASE + \
                "/directory/?numresult=25&startat=0&sgenre=%s" % name,
                            on_load, [""])

