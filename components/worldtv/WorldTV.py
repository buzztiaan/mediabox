from storage import Device, File
from utils.MiniXML import MiniXML
from ui import dialogs
import theme

import os


_STATIONS_FILE = "/usr/share/applications/worldtv99/WorldTV99.xml"


class WorldTV(Device):

    CATEGORY = Device.CATEGORY_WAN
    TYPE = Device.TYPE_VIDEO
    

    def __init__(self):
            
        self.__tv_dom = None
    
        Device.__init__(self)

        if (os.path.exists(_STATIONS_FILE)):
            try:
                data = open(_STATIONS_FILE).read()
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
        f.source_icon = self.get_icon()
        f.path = "/"
        f.name = "World TV"
        f.mimetype = f.DIRECTORY
        f.resource = ""
        
        return f
        
        
    def get_file(self, path):
    
        f = File(self)
        f.source_icon = self.get_icon()
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
        f.source_icon = self.get_icon()
        f.path = path
        f.mimetype = f.DIRECTORY
        
        return f
        
        
    def __parse_item(self, path, node):
    
        try:
            name = node.get_attr("title")
            url = node.get_attr("url")
        except:
            return None
    
        if (not url.strip()):
            return None
    
        f = File(self)
        f.name = name
        f.resource = url
        f.source_icon = self.get_icon()
        f.path = path
        f.mimetype = "video/x-unknown"
        
        return f

