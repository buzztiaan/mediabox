from storage import Device, File
from utils.MiniXML import MiniXML
from ui import dialogs
from theme import theme

import os

try:
    # GNOME
    import gconf
except:
    try:
        # Maemo    
        import gnome.gconf as gconf
    except:
        # last resort...
        from utils import gconftool as gconf




_GCONF_KEY = "/apps/maemo/kmplayer/lists/WorldTV99"

# these don't work with MediaBox yet
_BLACKLISTED = ["USA-VCURLs72"]



class WorldTV(Device):

    CATEGORY = Device.CATEGORY_WAN
    TYPE = Device.TYPE_VIDEO
    

    def __init__(self):

        self.__tv_dom = None
    
        Device.__init__(self)

        xmlfile = gconf.client_get_default().get_string(_GCONF_KEY)

        if (xmlfile and os.path.exists(xmlfile)):
            try:
                data = open(xmlfile).read()
                self.__tv_dom = MiniXML(data).get_dom()
            except:
                pass
        

    def get_icon(self):
    
        return theme.worldtv_device
        
        
    def get_prefix(self):
    
        return "worldtv://"
        
        
    def get_name(self):
    
        return "World TV"
        
        
    def get_root(self):
    
        f = File(self)
        f.path = "/"
        f.name = "World TV"
        f.mimetype = f.DIRECTORY
        f.resource = ""
        f.info = "Watch TV streams from all over the world"
        
        return f
        
        
    def get_file(self, path):
    
        f = File(self)
        f.path = path
        f.mimetype = "video/x-unknown"
        
        return f


    def ls_async(self, path, cb, *args):

        if (not self.__tv_dom):
            dialogs.error("No stations available",
                          "Please install the package 'worldtv99'\n" \
                          "from the maemo-extras repository.\n"
                          "Then restart MediaBox.")

        if (path[-1] == "/"): path = path[:-1]

        path_parts = path.split("/")
        node = self.__tv_dom
        for p in path_parts:
            if (not p): continue
            node = node.get_children()[int(p)]
        #end for
        
        cnt = 0
        for c in node.get_children():
            c_path = path + "/" + str(cnt)
            
            if (c.get_name() == "group"):
                f = self.__parse_group(c_path, c)
            elif (c.get_name() == "item"):
                f = self.__parse_item(c_path, c)
            else:
                f = None

            if (f):
                cb(f, *args)

            cnt += 1
        #end for
        cb(None, *args)


    def __parse_group(self, path, node):
    
        f = File(self)
        try:
            f.name = node.get_attr("title")
        except:
            return None
        f.path = path
        f.mimetype = f.DIRECTORY

        if (f.name in _BLACKLISTED):
            return None

        return f
        
        
    def __parse_item(self, path, node):
    
        try:
            name = node.get_attr("title")
            url = node.get_attr("url")
        except:
            return None
    
        if (name in _BLACKLISTED):
            return None
    
        if (not url.strip()):
            return None
        elif (url.endswith(".xml")):
            return None
      
        f = File(self)
        f.name = name
        f.resource = url
        f.path = path
        f.mimetype = "video/x-unknown"
        f.thumbnail = theme.worldtv_device.get_path()
        
        return f

