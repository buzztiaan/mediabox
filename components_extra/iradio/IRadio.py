from storage import Device, File
import inetstations
from ShoutcastDirectory import ShoutcastDirectory
from ui.Dialog import Dialog
from utils import urlquote
from theme import theme


class IRadio(Device):

    CATEGORY = Device.CATEGORY_WAN
    TYPE = Device.TYPE_AUDIO

    def __init__(self):
    
        self.__shoutcast_directory = ShoutcastDirectory()
    
        Device.__init__(self)
        
        
    def get_icon(self):
    
        return theme.iradio_device
        
        
    def get_prefix(self):
    
        return "iradio://"
        
        
    def get_name(self):

        return "Internet Radio"

        
    def get_root(self):
    
        f = File(self)
        f.path = "/"
        f.name = self.get_name()
        f.mimetype = f.DIRECTORY
        f.resource = ""
        
        return f


    def get_file(self, path):
    
        f = File(self)
        f.path = path
        f.name = path[1:]
        f.info = path[1:]
        f.mimetype = "audio/x-unknown"
        f.resource = path[1:]
        
        for location, name in inetstations.get_stations():
            if (location == path[1:]):
                f.name = name
                break
        #end for
        
        return f
        

    def __ls_root(self):
    
        items = []
        for name, path, mimetype, emblem, can_add in \
          [("Favorites", "/favorites", File.DIRECTORY, None, True),
           ("SHOUTcast", "/shoutcast", File.DIRECTORY, None, False)]:
            item = File(self)
            item.can_add = can_add
            item.path = path
            item.resource = path
            item.name = name
            item.mimetype = mimetype
            item.emblem = emblem
            items.append(item)
        #end for

        items.append(None)
        return items


    def __ls_favs(self):
    
        items = []
        for location, name in inetstations.get_stations():
            item = File(self)
            item.can_delete = True
            item.path = "/" + urlquote.quote(location, "")
            item.resource = location
            item.name = name
            item.info = location
            if (location.endswith(".ram") or location.endswith(".rm")):
                item.mimetype = "application/vnd.rn-realmedia"
            else:
                item.mimetype = "audio/x-unknown"
            items.append(item)
        #end for
        items.append(None)
        
        return items


    def ls_async(self, path, cb, *args):
    
        def on_child(is_station, item):
            if (item):
                f = File(self)
                f.path = "/shoutcast/" + item.path
                f.resource = item.resource
                f.name = item.name
                f.info = ""
                if (item.bitrate):
                    f.info += "Bitrate: " + item.bitrate + "\n"
                if (item.now_playing):
                    f.info += "Now Playing: " + item.now_playing
                if (is_station):
                    f.mimetype = "audio/x-unknown"
                else:
                    f.mimetype = File.DIRECTORY
                cb(f, *args)
                
            else:
                cb(None, *args)

    
        if (path == "/"):
            items = self.__ls_root()
            for i in items:
                cb(i, *args)

        elif (path.startswith("/shoutcast")):
            self.__shoutcast_directory.get_path(path[10:], on_child)

        elif (path.startswith("/favorites")):
            items = self.__ls_favs()
            for i in items:
                cb(i, *args)


    def new_file(self, path):
    
        # present search dialog            
        dlg = Dialog()
        dlg.add_entry("Name:", "")
        dlg.add_entry("Location:", "http://")
        values = dlg.wait_for_values()
        
        if (values):
            name, location = values
            stations = inetstations.get_stations()
            stations.append((location, name))
            inetstations.save_stations(stations)
        
            item = File(self)
            item.can_delete = True
            item.path = "/" + urlquote.quote(location, "")
            item.resource = location
            item.name = name
            item.info = location
            item.mimetype = "audio/x-unknown"
            
            return item

        else:
            return None


    def delete(self, f):
    
        stations = inetstations.get_stations()
        idx = 0
        found = False
        for location, name in stations:
            print location, name, f.path, f.name
            if ((location, name) == (f.resource, f.name)):
                found = True
                break
            idx += 1
        #end for
        
        if (found):
            del stations[idx]
            inetstations.save_stations(stations)

