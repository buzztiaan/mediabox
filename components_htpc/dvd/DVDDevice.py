from storage import Device, File
from theme import theme


class DVDDevice(Device):

    CATEGORY = Device.CATEGORY_LOCAL
    TYPE = Device.TYPE_VIDEO
    

    def __init__(self):
            
        Device.__init__(self)


    def get_name(self):
    
        return "DVD"


    def get_prefix(self):
    
        return "dvd://"

