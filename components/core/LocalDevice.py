from storage import Device, File
from utils import mimetypes
from utils import maemo
from utils import logging
import theme

import os
import commands



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
    
        return theme.mb_device_n800


    def get_root(self):
    
        f = File(self)
        f.path = "MENU"
        f.mimetype = f.DIRECTORY
        f.resource = ""
        f.name = self.__name
        
        return f
        
        
    def __ls_menu(self):
    
        items = []
        for name, path, mimetype, emblem in \
          [("Memory Cards", "MMC", File.DIRECTORY, None),
           ("Sounds", "/home/user/MyDocs/.sounds", File.DIRECTORY, theme.mb_filetype_audio),
           ("Videos", "/home/user/MyDocs/.videos", File.DIRECTORY, theme.mb_filetype_video),
           ("Images", "/home/user/MyDocs/.images", File.DIRECTORY, theme.mb_filetype_image),
           ("Documents", maemo.IS_MAEMO and "/home/user/MyDocs/.documents"
                                        or os.path.expanduser("~"),
                                        File.DIRECTORY, None),
           ("Games", "/home/user/MyDocs/.games", File.DIRECTORY, None),
           ("System", "/", File.DIRECTORY, None)]:
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
        
        
    def __ls_mmcs(self):
    
        items = []
        for f in [ f for f in os.listdir("/media")
                   if os.path.isdir(os.path.join("/media", f)) ]:
            path = os.path.join("/media", f)
            item = File(self)
            item.path = path
            item.resource = path
            item.child_count = self.__get_child_count(path)
            item.name = f
            item.mimetype = File.DIRECTORY
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
        
        return item
    
        
        
        
    def ls(self, path):
                   
        def comp(a, b):
            if (a.mimetype != b.mimetype):
                if (a.mimetype == a.DIRECTORY):
                    return -1
                elif (b.mimetype == b.DIRECTORY):
                    return 1
                else:
                    return cmp(a.name.lower(), b.name.lower())
            else:
                return cmp(a.name.lower(), b.name.lower())
                
                   
        if (path == "MENU"):
            return self.__ls_menu()
            
        elif (path == "MMC"):
            return self.__ls_mmcs()
    
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
                #item.emblem = theme.filetype_image

            if (item.mimetype.startswith("audio/") or
                item.mimetype.startswith("image/") or
                item.mimetype.startswith("video/") or
                item.mimetype == item.DIRECTORY):
                items.append(item)
        #end for
        
        items.sort(comp)
        
        return items
        
        
    def load(self, resource, maxlen, cb, *args):
    
        fd = open(resource, "r")
        fd.seek(0, 2)
        total_size = fd.tell()
        fd.seek(0)
        read_size = 0
        while (True):
            d = fd.read(65536)
            read_size += len(d)
            
            cb(d, read_size, total_size, *args)
            
            if (d and maxlen > 0 and read_size >= maxlen):
                cb ("", read_size, total_size, *args)
                break
            elif (not d):
                break
        #end while

        
        
    def get_fd(self, resource):
    
        fd = open(resource, "r")
        return fd
