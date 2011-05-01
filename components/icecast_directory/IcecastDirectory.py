from storage import Device, File
from com import msgs
from io import Downloader
from utils import logging
from utils import urlquote
from utils.BeautifulSoup import BeautifulSoup
from theme import theme


_ICECAST_BASE = "http://dir.xiph.org"



class IcecastDirectory(Device):
    """
    Storage device for browsing the Icecast internet radio directory.
    """

    CATEGORY = Device.CATEGORY_WAN
    TYPE = Device.TYPE_AUDIO


    def __init__(self):

        # genre list
        self.__genres = []
        
        self.__current_folder = None
        
    
        Device.__init__(self)
        
        
        
    def get_prefix(self):
    
        return "iradio-icecast://"
        
        
    def get_name(self):
    
        return "icecast Radio"


    def get_icon(self):
    
        return theme.icecast_station


    def __on_add_radio(self, folder, f):
    
        self.emit_message(msgs.IRADIO_ACT_ADD_STATION, f.name, f.resource)


    def get_file_actions(self, folder, f):
    
        options = Device.get_file_actions(self, folder, f)
        options.append((None, "Add to my Internet Radios", self.__on_add_radio))

        return options


    def __make_genre(self, genre, href):

        f = File(self)    
        f.name = genre
        f.path = href
        f.mimetype = f.DIRECTORY
        f.icon = theme.icecast_folder.get_path()
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
        f.icon = theme.icecast_station.get_path()
        
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
            f.info = "Browse the icecast directory"
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
            for name, href in self.__genres:
                if (cnt < begin_at): continue
                if (end_at and cnt > end_at): break

                f = self.__make_genre(name, href)
                cb(f, *args)
                cnt += 1
            #end for
            cb(None, *args)


        def on_load_genres(d, amount, total, data):
            if (d):
                data[0] += d

            else:
                self.__genres = self.__parse_genres(data[0])
                list_genres()


        path = folder.path
        self.__current_folder = folder
        print path

        if (not path.endswith("/")): path += "/"
        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)

        if (len_parts == 0):
            # list genres
            if (not self.__genres):
                dl = Downloader(_ICECAST_BASE + "/index.php",
                                on_load_genres, [""])
            else:
                list_genres()

        else: #if (len_parts == 1):
            # list stations
            href = path
            self.__load_page(_ICECAST_BASE + href, cb, args)
        
        
    def __load_page(self, url, cb, args):
    
        def on_page_loaded(d, amount, total, data, genre):
            if (d):
                data[0] += d

            else:
                stations, next = self.__parse_stations(data[0], genre)
                cnt = 0
                for station in stations:
                    cb(station, *args)
                #end for
                print "NEXT", next
                if (next):
                    self.__load_page(url + next, cb, args)
                else:
                    cb(None, *args)
    
        base = url
        dl = Downloader(url, on_page_loaded, [""], "")


    def __parse_genres(self, data):
        """
        Parses the list of genres.
        """
        
        genres = []
        soup = BeautifulSoup(data)
        tagcloud = soup.find("ul", {"class": "tag-cloud"})
        #print tagcloud

        if (tagcloud):
            for genre_tag in tagcloud.findAll("a", {"class": "tag"}):
                #print genre_tag
                name = genre_tag["title"]
                href = genre_tag["href"]
                genres.append((name, href))
            #end for
        #end if
    
        if (not genres):
            self.__current_folder.message = "genre list not available"
            logging.error("icecast genre listing download failed:\n%s",
                          logging.stacktrace())
            
        genres.sort(lambda a,b:cmp(a[0],b[0]))
        return genres


    def __parse_stations(self, data, genre):
        """
        Parses the list of stations.
        """

        stations = []
        next_page_url = ""
        
        soup = BeautifulSoup(data)
        resulttable = soup.find("div", {"id": "content"})

        if (resulttable):
            for entry in resulttable.findAll("tr"):
                #print entry                    
                
                station = File(self)
                try:
                    station.name = entry.find("span", {"class": "name"}).a.contents[0]
                except:
                    continue
                try:
                    now_playing = entry.find("p", {"class": "stream-onair"}).contents[1]
                except:
                    now_playing = ""
                station.resource = _ICECAST_BASE + entry.find("td", {"class": "tune-in"}).find("a")["href"]
                try:
                    bitrate = entry.find("td", {"class": "tune-in"}).findAll("p", {"class": "format"})[1]["title"]
                except:
                    bitrate = "-"
                
                try:
                    typename = entry.find("a", {"class": "no-link"}).contents[0].strip()
                except:
                    typename = ""
                    
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
                station.info = "Bitrate: %s\n" \
                               "Now playing: %s" % (bitrate, now_playing)
                station.icon = theme.icecast_station.get_path()
                stations.append(station)
            #end for
            
            pager_tag = resulttable.find("ul", {"class": "pager"})
            if (pager_tag):
                link = pager_tag.findAll("a")[-1]
                if (not link.contents[0].isdigit()):
                    # must be an arrow
                    next_page_url = link["href"]
                #end if
            #end if
            
        #end if
        
        if (not stations):
            self.__current_folder.message = "station list not available"
            logging.error("icecast station listing download failed\n%s",
                          logging.stacktrace())

        return (stations, next_page_url)



    def __encode_station(self, name, bitrate, mimetype, resource, genre):
    
        s = "\t\t\t".join([name, bitrate, mimetype, resource, genre])
        return urlquote.quote(s, "")


    def __decode_station(self, s):
    
        data = urlquote.unquote(s)
        name, bitrate, mimetype, resource, genre = data.split("\t\t\t")
        return (name, bitrate, mimetype, resource, genre)
        
