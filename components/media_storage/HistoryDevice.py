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
    Storage device for collecting and listing the history of recently visited
    folders.
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
    
        return "Recently Visited Folders"
        

    def get_icon(self):
    
        return None
        
        
    def get_root(self):
    
        f = File(self)
        f.name = self.get_name()
        f.info = "History of recently visited folders"
        f.path = "/"
        f.mimetype = f.DEVICE_ROOT

        return f
        
        
    def get_file(self, path):
    
        return self.get_root()


    def get_contents(self, path, begin_at, end_at, cb, *args):

        cnt = 0
        for f in self.__history:
            if (cnt < begin_at): continue
            if (end_at and cnt > end_at): break
            cb(f, *args)
            cnt += 1
        #end for
        
        cb(None, *args)



    def handle_CORE_EV_FOLDER_VISITED(self, f):
    
        if (not f.full_path in _BLACKLIST):
            if (f in self.__history):
                self.__history.remove(f)
                
            self.__history = [f] + self.__history[:_HISTORY_SIZE - 1]
        #end if

