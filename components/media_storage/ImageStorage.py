from com import msgs

from storage import Device, File
from utils import logging
import idtags
import theme

import os
import commands



class ImageStorage(Device):

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_IMAGE
    

    def __init__(self):
    
        self.__folders = {}
    
        Device.__init__(self)
        
        
    def handle_event(self, msg, *args):
    
        if (msg == msgs.MEDIASCANNER_EV_SCANNING_FINISHED):
            self.__update_media()


    def __update_media(self):

        self.__folders = {"All Images": []}
        media = self.call_service(msgs.MEDIASCANNER_SVC_GET_MEDIA,
                                  ["image/"])
        for f in media:
            parent = f.parent
            if (not parent in self.__folders):
                self.__folders[parent] = []
            self.__folders[parent].append(f)
            self.__folders["All Images"].append(f)        
        #end for
          
        
    def get_prefix(self):
    
        return "library://image"
        
        
    def get_name(self):
    
        return "Image Library"


    def get_icon(self):
    
        return theme.mb_device_image


    def get_root(self):
    
        f = File(self)
        f.is_local = True
        f.path = "/"
        f.mimetype = f.DIRECTORY
        f.resource = ""
        f.name = self.get_name()
        
        return f
          
    
    
    def ls_async(self, path, cb, *args):

        def folder_cmp(a, b):
            if (a == "All Images"):
                return -1
            if (b == "All Images"):
                return 1
            else:
                return cmp(a, b)

    
        if (path == "/"):
            folders = self.__folders.keys()
            folders.sort(folder_cmp)
            for folder in folders:
                f = File(self)
                f.is_local = True
                f.path = "/" + folder
                f.mimetype = f.DIRECTORY
                f.resource = ""
                f.name = folder
                f.info = "%d items" % len(self.__folders.get(folder, []))
                cb(f, *args)
                
        else:
            images = self.__folders.get(path[1:], [])
            for img in images:
                cb(img, *args)
            #end for
        
        cb(None, *args)

