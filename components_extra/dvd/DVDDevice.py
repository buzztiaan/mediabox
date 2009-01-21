from storage import Device, File
from theme import theme

import os


class DVDDevice(Device):

    CATEGORY = Device.CATEGORY_LOCAL
    TYPE = Device.TYPE_VIDEO
    

    def __init__(self, path):
            
        self.__name = os.path.basename(path)
        self.__path = path
    
        Device.__init__(self)

        

    def get_icon(self):
    
        return theme.mb_unknown_album
        
        
    def get_prefix(self):
    
        return "dvd://%s" % self.__name
        
        
    def get_name(self):
    
        return self.__name
        
        
    def get_root(self):
    
        f = File(self)
        f.path = "/"
        f.name = self.__name
        f.mimetype = "video/x-dvd-image"
        f.resource = "dvd://%s" % self.__path
        
        return f


    def ls(self, path):
    
        return [self.get_root()]

