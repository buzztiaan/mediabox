from device import Device, File
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
        
        
    def get_name(self):
    
        return self.__name


    def get_icon(self):
    
        return theme.viewer_folders_tablet
        
        
    def ls(self, path):
    
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
