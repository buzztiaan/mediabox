class File(object):

    FILE = 0
    DIRECTORY = 1
    

    def __init__(self):
    
        self.name = ""
        self.child_count = 0
        self.info = ""
        self.filetype = self.FILE
        self.mimetype = "application/x-other"
        self.path = ""

