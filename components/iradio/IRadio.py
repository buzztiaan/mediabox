from storage import Device, File
from ShoutcastDirectory import ShoutcastDirectory
import theme


class IRadio(Device):

    CATEGORY = Device.CATEGORY_WAN

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
        f.source_icon = self.get_icon()
        f.path = "/"
        f.name = "Internet Radio"
        f.mimetype = f.DIRECTORY
        f.resource = ""
        
        return f


    def __ls_root(self):
    
        items = []
        for name, path, mimetype, emblem, can_add in \
          [("Favorites", "/favorites", File.DIRECTORY, None, True),
           ("SHOUTcast", "/shoutcast", File.DIRECTORY, None, False)]:
            item = File(self)
            item.can_add = can_add
            item.source_icon = self.get_icon()
            item.path = path
            item.resource = path
            item.name = name
            item.mimetype = mimetype
            item.emblem = emblem
            items.append(item)
        #end for

        items.append(None)
        return items


    def ls_async(self, path, cb, *args):
    
        def on_child(is_station, item):
            if (item):
                f = File(self)
                f.source_icon = self.get_icon()
                f.path = "/shoutcast/" + item.path
                f.resource = item.resource
                f.name = item.name
                if (item.now_playing):
                    f.info = "Now Playing: " + item.now_playing
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

