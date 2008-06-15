from device import Device, File
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
        
        
    def get_name(self):
    
        return self.__name


    def get_icon(self):
    
        return theme.viewer_folders_tablet


    def get_root(self):
    
        return _ROOT_PATH
        
        
    def __ls_menu(self):
    
        items = []
        for name, path, filetype in \
          [("Sounds", "/home/user/MyDocs/.sounds", File.DIRECTORY),
           ("Videos", "/home/user/MyDocs/.videos", File.DIRECTORY),
           ("Images", "/home/user/MyDocs/.images", File.DIRECTORY),
           ("Documents", "/home/user/MyDocs/.documents", File.DIRECTORY),
           ("Games", "/home/user/MyDocs/.games", File.DIRECTORY),
           ("System", "/", File.DIRECTORY),
           ("Memory Cards", "MMC", File.DIRECTORY)]:
            item = File()
            item.name = name
            item.path = path
            item.filetype = filetype
            items.append(item)
        #end for
        
        return items
        
        
    def ls(self, path):
    
        if (path == _ROOT_PATH):
            return self.__ls_menu()
    
        try:
            files = [ f for f in os.listdir(path)
                     if not f.startswith(".") ]
        except:
            files = []
            
        items = []
        for f in files:
            item = File()
            item.name = f
            item.path = os.path.join(path, f)
            if (os.path.isdir(item.path)):
                item.filetype = item.DIRECTORY
                item.child_count = self.__get_child_count(item.path)
            else:
                item.filetype = item.FILE
            items.append(item)
        #end for
        
        return items
