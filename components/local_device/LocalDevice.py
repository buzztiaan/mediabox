from storage import Device, File
from utils import mimetypes
from utils import maemo
from utils import mmc
from utils import logging
from theme import theme

import os
import commands
import gobject



class LocalDevice(Device):

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_GENERIC
    

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
        f.is_local = True
        f.can_add_to_library = True
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
            item.is_local = True
            item.can_add_to_library = True
            item.path = path
            item.resource = path
            #item.child_count = self.__get_child_count(path)
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
            item.is_local = True
            item.can_add_to_library = True
            item.path = path
            item.resource = path
            #item.child_count = self.__get_child_count(path)            
            item.name = mmc.get_label(path)
            item.mimetype = File.DIRECTORY
            items.append(item)
        #end for
        
        return items
        
        
    def get_file(self, path):

        item = File(self)
        item.is_local = True
        item.can_add_to_library = True
        item.path = path
        item.name = os.path.basename(path)
        item.resource = path
        item.parent = os.path.basename(os.path.dirname(path))
        if (os.path.isdir(item.resource)):
            item.mimetype = item.DIRECTORY
            #children = item.get_children()
            #for c in children:
            #    if (c.mimetype.startswith("audio/")
            #        and c.mimetype != "application/x-music-folder"):
            #        item.mimetype = "application/x-music-folder"
            #        break
            ##end for
            #item.child_count = len(children)
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
    
        #logging.debug("listing [%s]" % path)
        try:
            files = [ f for f in os.listdir(path)
                      if not f.startswith(".") ]
        except:
            files = []
        files.sort()
            
        items = []
        for f in files:
            item = self.get_file(os.path.join(path, f))
            #item = File(self)
            #item.is_local = True
            #item.can_add_to_library = True
            #item.path = os.path.join(path, f)
            #item.name = f
            #item.parent = os.path.basename(path)
            #item.resource = os.path.join(path, f)

            #if (os.path.isdir(item.resource)):
            #    item.mimetype = item.DIRECTORY
            #    item.child_count = self.__get_child_count(item.path)
            #else:
            #    ext = os.path.splitext(f)[-1].lower()
            #    item.mimetype = mimetypes.lookup_ext(ext)
            #    #item.emblem = theme.filetype_image

            if (item.mimetype.startswith("audio/") or
                item.mimetype.startswith("image/") or
                item.mimetype.startswith("video/") or
                item.mimetype == item.DIRECTORY):
                items.append(item)
        #end for
        
        items.sort(comp)
        
        return items
        
        
    def load(self, f, maxlen, cb, *args):
    
        def on_data(fd, read_size, total_size):
            data = fd.read(0xffff)
            read_size[0] += len(data)
            
            try:
                cb(data, read_size[0], total_size, *args)
            except:
                fd.close()
                return False
                
            if (data and maxlen > 0 and read_size[0] >= maxlen):
                try:
                    cb("", read_size[0], total_size, *args)
                except:
                    pass
                fd.close()
                return False

            elif (not data):
                fd.close()
                return False
            
            return True
        

        fd = open(f.resource, "r")
        fd.seek(0, 2)
        total_size = fd.tell()
        fd.seek(0)
        
        gobject.timeout_add(50, on_data, fd, [0], total_size)
