from storage import Device, File
from utils.MiniXML import MiniXML
from mediabox import values
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
_WORLDTV_XML = os.path.join(values.USER_DIR, "WorldTV99.xml")

# these don't work with MediaBox yet
_BLACKLISTED = ["USA-VCURLs72"]



class WorldTV(Device):

    CATEGORY = Device.CATEGORY_WAN
    TYPE = Device.TYPE_VIDEO
    

    def __init__(self):

        self.__tv_dom = None
    
        Device.__init__(self)

        if (os.path.exists(_WORLDTV_XML)):
            xmlfile = _WORLDTV_XML
        else:
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
        
        
    def get_file(self, path):
            
        if (path == "/"):
            f = File(self)
            f.path = "/"
            f.name = "World TV"
            f.mimetype = f.DIRECTORY
            f.resource = ""
            f.info = "Watch TV streams from all over the world"
        else:
            f = File(self)
            f.path = path
            f.mimetype = "video/x-unknown"

        return f


    def get_contents(self, folder, begin_at, end_at, cb, *args):

        if (not self.__tv_dom):
            folder.message = "Please install WorldTV"
            cb(None, *args)
            return
        else:
            folder.message = ""
    
        path = folder.path
        if (path[-1] == "/"): path = path[:-1]
        parts = [ p for p in folder.path.split("/") if p ]
        len_parts = len(parts)

        node = self.__tv_dom
        for p in parts:
            if (not p): continue
            node = node.get_children()[int(p)]
        #end for
        
        cnt = 0
        items = []
        for c in node.get_children():
            c_path = path + "/" + str(cnt)
            
            if (c.get_name() == "group"):
                f = self.__parse_group(c_path, c)
            elif (c.get_name() == "item"):
                f = self.__parse_item(c_path, c)
            else:
                f = None

            if (f):
                items.append(f)

            cnt += 1
        #end for

        items.sort()
        
        cnt = -1
        for item in items:
            cnt += 1
            if (cnt < begin_at): continue
            if (end_at and cnt > end_at): break
            cb(item, *args)
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

