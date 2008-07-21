class File(object):

    FILE = "application/x-other"
    DIRECTORY = "application/x-directory"
    

    def __init__(self, device):
    
        self.__device = device
        self.path = ""

        self.name = ""
        
        self.title = ""
        self.artist = ""
        self.album = ""
        self.trackno = 0
        self.child_count = 0
        self.info = ""
        self.mimetype = self.FILE
        self.emblem = None
        self.resource = ""
        self.md5 = ""
        self.thumbnail = ""
        
        self.tags = None


    def __cmp__(self, other):
    
        if (other):
            return cmp((self.name, self.resource), (other.name, other.resource))
        else:
            return 1

        
    def get_children(self):
    
        return self.__device.ls(self.path)


    def get_children_async(self, cb, *args):
        
        self.__device.ls_async(self.path, cb, *args)


    def get_fd(self):
    
        return self.__device.get_fd(self.resource)
        
        
    def get_resource(self):
    
        return self.__device.get_resource(self.resource)
        
