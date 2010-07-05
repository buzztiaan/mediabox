from com import msgs
from storage import Device, File
from utils import urlquote
from utils import logging
from theme import theme

import os



class AdHocDevice(Device):
    """
    Storage device for adhoc files.
    """

    CATEGORY = Device.CATEGORY_HIDDEN
    TYPE = Device.TYPE_GENERIC
    

    def __init__(self):
    
        Device.__init__(self)
         
        
    def get_prefix(self):
    
        return "adhoc://"
        
        
    def get_name(self):
    
        return "AdHoc"


    def get_icon(self):
    
        return None


    def get_file(self, path):
    
        prefix, path, mimetype = File.unpack_path(path)
        
        f = File(self)
        f.name = path
        f.resource = path
        f.mimetype = mimetype
    
        return f

