from storage import Device, File
from com import msgs
from io import Downloader
from utils import logging
from utils import urlquote
from utils.BeautifulSoup import BeautifulSoup
from theme import theme


_SHOUTCAST_BASE = "http://www.shoutcast.com"
#_SHOUTCAST_BASE = "http://yp.shoutcast.com"



class ShoutcastDirectory(Device):
    """
    Storage device for browsing the SHOUTcast internet radio directory.
    """

    CATEGORY = Device.CATEGORY_WAN
    TYPE = Device.TYPE_AUDIO


    def __init__(self):

        # genre list
        self.__genres = []
        
        self.__current_folder = None
        
    
        Device.__init__(self)
        
        
        
    def get_prefix(self):
    
        return "iradio-shoutcast://"
        
        
    def get_name(self):
    
        return "SHOUTcast Radio"


    def get_icon(self):
    
        return theme.shoutcast_folder


    def __on_add_radio(self, folder, f):
    
        self.emit_message(msgs.IRADIO_ACT_ADD_STATION, f.name, f.resource)


    def get_file_actions(self, folder, f):
    
        options = Device.get_file_actions(self, folder, f)
        options.append((None, "Add to my Internet Radios", self.__on_add_radio))

        return options


    def __make_genre(self, genre):

        f = File(self)    
        f.name = genre.replace("&amp;", "&")
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
            f.folder_flags = f.ITEMS_ENQUEUEABLE #| f.ITEMS_COMPACT
    
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
        self.__current_folder = folder

        if (not path.endswith("/")): path += "/"
        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)

        if (len_parts == 0):
            # list genres
            if (not self.__genres):
                dl = Downloader(_SHOUTCAST_BASE + "/",
                                on_load_genres, [""])
            else:
                list_genres()

        elif (len_parts == 1):
            # list stations
            genre = parts[0]
            dl = Downloader(_SHOUTCAST_BASE + "/radio/%s" % genre,
                            on_load_stations, [""], genre)
        


    def __parse_genres(self, data):
        """
        Parses the list of genres.
        """
        
        self.call_service(msgs.UI_ACT_SHOW_INFO,
                          "SHOUTcast made it illegal for free software to access\n" \
                          "their full directory.\n" \
                          "You will only get the Top 10 stations listed per genre.")
        
        genres = []
        soup = BeautifulSoup(data)
        radiopicker = soup.find("div", {"id": "radiopicker"})
        #print radiopicker
        if (radiopicker):
            for genre_tag in radiopicker.findAll("li", {"class": "prigen"}):
                #print genre_tag
                name = genre_tag.a.contents[0]
                genres.append(name)
            #end for
        #end if
    
        if (not genres):
            self.__current_folder.message = "genre list not available"
            logging.error("SHOUTcast genre listing download failed:\n%s",
                          logging.stacktrace())
            
        genres.sort()
        return genres


    def __parse_stations(self, data, genre):
        """
        Parses the list of stations.
        """

        stations = []
        soup = BeautifulSoup(data)
        resulttable = soup.find("div", {"id": "resulttable"})
        if (resulttable):
            for entry in resulttable.findAll("div", {"class": "dirlist"}):
                #print entry
                station = File(self)
                a_tag = entry.find("a", {"class": "playbutton playimage"})
                playing_tag = entry.find("div", {"class": "playingtext"})
                bitrate_tag = entry.find("div", {"class": "dirbitrate"})
                type_tag = entry.find("div", {"class": "dirtype"})
                
                if (not a_tag or
                    not playing_tag or
                    not bitrate_tag or
                    not type_tag): continue
                
                station.resource = a_tag["href"]
                station.name = a_tag["title"]
                now_playing = playing_tag["title"]
                bitrate = bitrate_tag.contents[0].strip()

                typename = type_tag.contents[0].strip()
                if (typename == "MP3"):
                    station.mimetype = "audio/mpeg"
                elif (typename == "AAC+"):
                    station.mimetype = "audio/mp4"
                else:
                    station.mimetype = "audio/x-unknown"
                
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
            #end for
        #end if
        
        if (not stations):
            self.__current_folder.message = "station list not available"
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
        
