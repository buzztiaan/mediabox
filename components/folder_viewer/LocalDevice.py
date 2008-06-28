from device import Device, File
from utils import mimetypes
from utils import logging
import theme

import os
import commands


_ROOT_PATH = "MENU"


class LocalDevice(Device):

    def __init__(self):
    
        self.__name = commands.getoutput("hostname")
        Device.__init__(self)
        
        
    def __get_child_count(self, path):
    
        try:
            files = [ f for f in os.listdir(path)
                     if not f.startswith(".") ]
        except:
            files = []

        return len(files)
        
        
    def get_prefix(self):
    
        return "file://"
        
        
    def get_name(self):
    
        return self.__name


    def get_icon(self):
    
        return theme.viewer_folders_tablet


    def get_root(self):
    
        f = File(self)
        f.path = "MENU"
        f.mimetype = f.DIRECTORY
        f.resource = ""
        f.name = ""
        
        return f
        
        
    def __ls_menu(self):
    
        items = []
        for name, path, mimetype, emblem in \
          [("Sounds", "/home/user/MyDocs/.sounds", File.DIRECTORY, theme.filetype_audio),
           ("Videos", "/home/user/MyDocs/.videos", File.DIRECTORY, theme.filetype_video),
           ("Images", "/home/user/MyDocs/.images", File.DIRECTORY, theme.filetype_image),
           ("Documents", "/home/user/MyDocs/.documents", File.DIRECTORY, None),
           ("Games", "/home/user/MyDocs/.games", File.DIRECTORY, None),
           ("System", "/", File.DIRECTORY, None),
           ("Memory Cards", "MMC", File.DIRECTORY, None)]:
            item = File(self)
            item.path = path
            item.resource = path
            item.child_count = self.__get_child_count(path)
            item.name = name
            item.mimetype = mimetype
            item.emblem = emblem
            items.append(item)
        #end for
        
        return items
        
        
    def get_file(self, path):

        item = File(self)
        item.path = path
        item.name = os.path.basename(path)
        item.resource = path
        if (os.path.isdir(item.resource)):
            item.mimetype = item.DIRECTORY
            item.child_count = self.__get_child_count(item.path)
        else:
            ext = os.path.splitext(path)[-1].lower()
            item.mimetype = mimetypes.lookup_ext(ext)
            item.emblem = theme.filetype_image
        
        return item
    
        
        
        
    def ls(self, path):
                   
        if (path == _ROOT_PATH):
            return self.__ls_menu()
    
        logging.debug("listing [%s]" % path)
        try:
            files = [ f for f in os.listdir(path)
                      if not f.startswith(".") ]
        except:
            files = []
        files.sort()
            
        items = []
        for f in files:
            item = File(self)
            item.path = os.path.join(path, f)
            item.name = f
            item.resource = os.path.join(path, f)
            if (os.path.isdir(item.resource)):
                item.mimetype = item.DIRECTORY
                item.child_count = self.__get_child_count(item.path)
            else:
                ext = os.path.splitext(f)[-1].lower()
                item.mimetype = mimetypes.lookup_ext(ext)
                item.emblem = theme.filetype_image
            items.append(item)
        #end for
        
        return items
        
        
    def get_fd(self, resource):
    
        fd = open(resource, "r")
        return fd
