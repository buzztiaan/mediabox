from storage import Device, File
from com import msgs
from io import Downloader
from utils import logging
from utils import urlquote
from theme import theme

from xml.etree import ElementTree
from cStringIO import StringIO


_SHOUTCAST_BASE = "http://www.shoutcast.com"


class ShoutcastStorage(Device):

    CATEGORY = Device.CATEGORY_WAN
    TYPE = Device.TYPE_PRIVATE


    def __init__(self):

        # genre list
        self.__genres = []
    
        Device.__init__(self)
        
        
        
    def get_prefix(self):
    
        return "iradio-shoutcast://"
        
        
    def get_name(self):
    
        return "SHOUTcast Directory"


    def get_icon(self):
    
        return theme.iradio_shoutcast


    def get_root(self):
    
        f = File(self)
        f.path = "/"
        f.mimetype = f.DIRECTORY
        f.resource = ""
        f.name = self.get_name()
        f.info = "Browse the SHOUTcast directory"
        f.icon = self.get_icon()
        f.folder_flags = f.ITEMS_ENQUEUEABLE

        return f


    def get_file(self, path):
    
        try:
            name, bitrate, mimetype, location = self.__decode_path(path)
        except:
            logging.error("error decoding iradio path: %s\n%s",
                          path, logging.stacktrace())
            return None
            
        f = File(self)
        f.name = name
        f.info = "Bitrate: %s kb" % bitrate
        f.resource = location
        f.path = path
        f.mimetype = mimetype
        f.icon = theme.iradio_shoutcast
        
        return f
        
        
    def get_contents(self, folder, begin_at, end_at, cb, *args):

        def on_load_genres(d, amount, total, data):
            if (d):
                data[0] += d

            else:
                #open("/tmp/shoutcast-genres.html", "w").write(data[0])
                self.__genres = self.__parse_genres(data[0])
                # list genres
                cnt = 0
                for name in self.__genres:
                    if (begin_at <= cnt <= end_at):
                        f = File(self)
                        f.name = name
                        f.path = "/" + urlquote.quote(name)
                        f.mimetype = f.DIRECTORY
                        f.folder_flags = f.ITEMS_ENQUEUEABLE

                        cb(f, *args)
                    #end if
                    cnt += 1
                #end for
                cb(None, *args)


        def on_load_stations(d, amount, total, data, genre):
            if (d):
                data[0] += d

            else:
                #open("/tmp/shoutcast-stations.html", "w").write(data[0])
                stations = self.__parse_stations(data[0], genre)
                cnt = 0
                for station in stations:
                    if (begin_at <= cnt <= end_at):
                        cb(station, *args)
                    #end if
                    cnt += 1
                #end for
                cb(None, *args)


        if (end_at == 0):
            end_at = 999999999
    
        if (not self.__genres):
            dl = Downloader(_SHOUTCAST_BASE + "/sbin/newxml.phtml",
                            on_load_genres, [""])

        elif (folder.path == "/"):
            # list genres
            cnt = 0
            for name in self.__genres:
                if (begin_at <= cnt <= end_at):
                    f = File(self)
                    f.name = name
                    f.path = "/" + urlquote.quote(name)
                    f.mimetype = f.DIRECTORY
                    f.folder_flags = f.ITEMS_ENQUEUEABLE

                    cb(f, *args)
                #end if
                cnt += 1
            #end for
            cb(None, *args)

        else:
            print folder.path
            genre = folder.path[1:]
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
            self.call_service(msgs.DIALOG_SVC_ERROR,
                              "Cannot Load",
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

                    station.path = self.__encode_path(station.name,
                                                      bitrate,
                                                      station.mimetype,
                                                      station.resource)
                    station.info = "Bitrate: %s kb\n" \
                                   "Now playing: %s" % (bitrate, now_playing)
                    station.icon = theme.iradio_shoutcast
                    stations.append(station)

        except:
            self.call_service(msgs.DIALOG_SVC_ERROR,
                              "Cannot Load",
                              "An error occured while loading the list of stations.\n" \
                              "Check your internet connection and try again.")
            logging.error("SHOUTcast station listing download failed\n%s",
                          logging.stacktrace())

        stations.sort()
        return stations



    def __encode_path(self, name, bitrate, mimetype, resource):
    
        path = "/" + "\t\t\t".join([name, bitrate, mimetype, resource])
        return urlquote.quote(path)


    def __decode_path(self, path):
    
        data = urlquote.unquote(path[1:])
        name, bitrate, mimetype, resource = data.split("\t\t\t")
        return (name, bitrate, mimetype, resource)
