class File(object):

    FILE = "application/x-other"
    DIRECTORY = "application/x-directory"
    

    def __init__(self, device):
    
        self.__device = device
        self.path = ""

        self.name = ""
        self.child_count = 0
        self.info = ""
        self.mimetype = self.FILE
        self.emblem = None
        self.resource = ""
        self.md5 = ""
        self.thumbnail = ""

        
    def get_children(self):
    
        return self.__device.ls(self.path)


    def get_fd(self):
    
        return self.__device.get_fd(self.resource)
        
