from storage import Device, File
from com import msgs
from io import Downloader
from utils import logging
from utils import urlquote
from theme import theme

from xml.etree import ElementTree
from cStringIO import StringIO


#_SHOUTCAST_BASE = "http://www.shoutcast.com"
_SHOUTCAST_BASE = "http://yp.shoutcast.com"



class ShoutcastDirectory(Device):
    """
    Storage device for browsing the SHOUTcast internet radio directory.
    """

    CATEGORY = Device.CATEGORY_WAN
    TYPE = Device.TYPE_AUDIO


    def __init__(self):

        # genre list
        self.__genres = []
    
        Device.__init__(self)
        
        
        
    def get_prefix(self):
    
        return "iradio-shoutcast://"
        
        
    def get_name(self):
    
        return "SHOUTcast Radio"


    def get_icon(self):
    
        return theme.shoutcast_folder


    def __make_genre(self, genre):

        f = File(self)    
        f.name = genre
        f.path = "/" + urlquote.quote(genre, "")
        f.mimetype = f.DIRECTORY
        f.icon = theme.shoutcast_folder.get_path()
        f.folder_flags = f.ITEMS_ENQUEUEABLE

        return f


    def __make_station(self, s):
    
        try:
            name, bitrate, mimetype, location, genre = self.__decode_station(s)
        except:
            logging.error("error decoding iradio path: %s\n%s",
                            path, logging.stacktrace())
            return None
        
        f = File(self)
        f.name = name
        f.info = "Bitrate: %s kb" % bitrate
        f.resource = location
        f.path = "/" + urlquote.quote(genre, "") + "/" + s
        f.mimetype = mimetype
        f.icon = theme.shoutcast_station.get_path()
        
        return f       


    def get_file(self, path):

        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)
        
        f = None
        if (len_parts == 0):
            # root folder
            f = File(self)
            f.path = "/"
            f.mimetype = f.DIRECTORY
            f.resource = ""
            f.name = self.get_name()
            f.info = "Browse the SHOUTcast directory"
            f.icon = self.get_icon().get_path()
            f.folder_flags = f.ITEMS_ENQUEUEABLE | f.ITEMS_COMPACT
    
        elif (len_parts == 1):
            genre = urlquote.unquote(parts[0])
            f = self.__make_genre(genre)
    
        elif (len_parts == 2):
            f = self.__make_station(parts[1])

        return f
        
        
    def get_contents(self, folder, begin_at, end_at, cb, *args):

        def list_genres():
            cnt = 0
            for name in self.__genres:
                if (cnt < begin_at): continue
                if (end_at and cnt > end_at): break

                f = self.__make_genre(name)
                cb(f, *args)
                cnt += 1
            #end for
            cb(None, *args)


        def on_load_genres(d, amount, total, data):
            if (d):
                data[0] += d

            else:
                #open("/tmp/shoutcast-genres.html", "w").write(data[0])
                self.__genres = self.__parse_genres(data[0])
                list_genres()


        def on_load_stations(d, amount, total, data, genre):
            if (d):
                data[0] += d

            else:
                #open("/tmp/shoutcast-stations.html", "w").write(data[0])
                stations = self.__parse_stations(data[0], genre)
                cnt = 0
                for station in stations:
                    if (cnt < begin_at): continue
                    if (end_at and cnt > end_at): break

                    cb(station, *args)
                    cnt += 1
                #end for
                cb(None, *args)


        path = folder.path

        if (not path.endswith("/")): path += "/"
        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)

        if (len_parts == 0):
            # list genres
            if (not self.__genres):
                dl = Downloader(_SHOUTCAST_BASE + "/sbin/newxml.phtml",
                                on_load_genres, [""])
            else:
                list_genres()

        elif (len_parts == 1):
            # list stations
            genre = parts[0]
            dl = Downloader(_SHOUTCAST_BASE + "/sbin/newxml.phtml?genre=%s" % genre,
                            on_load_stations, [""], genre)
        


    def __parse_genres(self, data):
        """
        Parses the XML list of genres.
        """

        genres = []
        try:
            dtree = ElementTree.parse(StringIO(data))
            for i in dtree.getiterator():
                if i.tag == "genre":
                    for j,n in i.items():
                        if j == "name":
                            genres.append(n)
        except:
            self.call_service(msgs.UI_ACT_SHOW_INFO,
                              "An error occured while loading the list of genres.\n" \
                              "Check your internet connection and try again.")
            logging.error("SHOUTcast genre listing download failed:\n%s",
                          logging.stacktrace())
            
        genres.sort()
        return genres


    def __parse_stations(self, data, genre):
        """
        Parses the XML list of stations.
        """

        stations = []
        try:
            dtree = ElementTree.parse(StringIO(data))
            for i in dtree.getiterator():
                if i.tag == "station":
                    # build station object
                    station = File(self)
                    bitrate = "-"
                    now_playing = "-"
                    
                    for j,n in i.items():
                        if j == "name":
                            station.name = n
                        elif j == "ct":
                            now_playing = n
                        elif j == "id":
                            station.resource = _SHOUTCAST_BASE + "/sbin/shoutcast-playlist.pls?rn=%s&file=filename.pls" % n
                        elif j == "br":
                            bitrate = n
                        elif j == "mt":
                            station.mimetype = n

                    station.path = "/" + genre + "/" + \
                                   self.__encode_station(station.name,
                                                         bitrate,
                                                         station.mimetype,
                                                         station.resource,
                                                         genre)
                    station.info = "Bitrate: %s kb\n" \
                                   "Now playing: %s" % (bitrate, now_playing)
                    station.icon = theme.shoutcast_station.get_path()
                    stations.append(station)

        except:
            self.call_service(msgs.UI_ACT_SHOW_INFO,
                              "An error occured while loading the list of stations.\n" \
                              "Check your internet connection and try again.")
            logging.error("SHOUTcast station listing download failed\n%s",
                          logging.stacktrace())

        stations.sort()
        return stations



    def __encode_station(self, name, bitrate, mimetype, resource, genre):
    
        s = "\t\t\t".join([name, bitrate, mimetype, resource, genre])
        return urlquote.quote(s, "")


    def __decode_station(self, s):
    
        data = urlquote.unquote(s)
        name, bitrate, mimetype, resource, genre = data.split("\t\t\t")
        return (name, bitrate, mimetype, resource, genre)
