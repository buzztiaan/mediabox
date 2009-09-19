from com import msgs
from storage import Device, File
from utils import mimetypes
from theme import theme


# store this many entries in the history
_HISTORY_SIZE = 20

# blacklisted places
_BLACKLIST = ["media:///",
              "history:///",
              "bookmarks://generic/"]


class HistoryDevice(Device):
    """
    Device for collecting and listing the runtime history of visited folders.
    """

    CATEGORY = Device.CATEGORY_HIDDEN
    TYPE = Device.TYPE_GENERIC


    def __init__(self):
    
        # history of visited folders
        self.__history = []
        
        Device.__init__(self)
        
        
        
    def get_prefix(self):
        
        return "history://"
        
        
    def get_name(self):
    
        return "History"
        

    def get_icon(self):
    
        return theme.mb_device_folders
        
        
    def get_root(self):
    
        f = File(self)
        f.name = self.get_name()
        f.info = "History of visited places"
        f.path = "/"
        f.mimetype = f.DIRECTORY

        return f
        
        
    def get_file(self, path):
    
        return self.get_root()


    def get_contents(self, path, begin_at, end_at, cb, *args):

        for f in self.__history:
            cb(f, *args)
        cb(None, *args)


    def handle_CORE_EV_FOLDER_VISITED(self, f):
    
        if (not f.full_path in _BLACKLIST):
            if (f in self.__history):
                self.__history.remove(f)
                
            self.__history = [f] + self.__history[:_HISTORY_SIZE - 1]
        #end if

