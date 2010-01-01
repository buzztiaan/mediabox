from com import Component, msgs
from mediabox import media_bookmarks
from mediabox import values
from utils import logging

import os


_BOOKMARK_FILE = os.path.join(values.USER_DIR, "bookmarks")

# provide some useful initial bookmarks
_INITIAL_BOOKMARKS = """
file:///home/user/MyDocs
file:///media/mmc1
preferences:///Tour
"""


class BookmarkService(Component):
    """
    Service for persisting bookmarks.
    """

    def __init__(self):
    
        # list of bookmarked files
        self.__items = []
        
        # whether the bookmarks need to be reloaded
        self.__needs_reload = True
        
        # whether there are unsaved changes
        self.__is_dirty = False
        
    
        Component.__init__(self)

        if (not os.path.exists(_BOOKMARK_FILE)):
            try:
                open(_BOOKMARK_FILE, "w").write(_INITIAL_BOOKMARKS)
            except:
                pass
        #end if
        
        
    def __load_bookmarks(self):
    
        self.__needs_reload = False

        self.__items = []
        try:
            lines = open(_BOOKMARK_FILE, "r").readlines()
        except:
            #logging.error("could not load bookmarks\n%s", logging.stacktrace())
            return
        
        for line in lines:
            f = self.call_service(msgs.CORE_SVC_GET_FILE, line.strip())
            if (f):
                self.__items.append(f)
        #end for
        
        self.__is_dirty = False
        self.emit_message(msgs.BOOKMARK_EV_INVALIDATED)
        
        
    def __save_bookmarks(self):

        if (not self.__is_dirty): return
            
        locations = [ f.full_path for f in self.__items ]
        try:
            open(_BOOKMARK_FILE, "w").write("\n".join(locations))
        except:
            logging.error("could not save bookmarks\n%s", logging.stacktrace())
            return

        self.__is_dirty = False
        
        
    def handle_BOOKMARK_SVC_LIST(self, mimetypes):
    
        if (self.__needs_reload): self.__load_bookmarks()

        if (mimetypes):
            out = [ f for f in self.__items if f.mimetype in mimetypes ]
        else:
            out = self.__items[:]
        
        return out

           
        
    def handle_BOOKMARK_SVC_ADD(self, f):

        if (self.__needs_reload): self.__load_bookmarks()

        paths = [ fl.full_path for fl in self.__items ]
        if (not f.full_path in paths):
            self.__items.append(f)
            self.__is_dirty = True

        self.__save_bookmarks()
        self.emit_message(msgs.BOOKMARK_EV_INVALIDATED)
        
        return 0
        

    def handle_BOOKMARK_SVC_DELETE(self, f):
    
        if (self.__needs_reload): self.__load_bookmarks()
        
        paths = [ fl.full_path for fl in self.__items ]
        if (f.full_path in paths):
            idx = paths.index(f.full_path)
            del self.__items[idx]
            media_bookmarks.set_bookmarks(f, [])
            self.__is_dirty = True

        self.__save_bookmarks()       
        self.emit_message(msgs.BOOKMARK_EV_INVALIDATED)

        return 0


    def handle_MEDIA_EV_BOOKMARKED(self, f, bookmarks):
    
        if (self.__needs_reload): self.__load_bookmarks()
        
        paths = [ fl.full_path for fl in self.__items ]
        
        if (bookmarks and not f.full_path in paths):
            self.__items.append(f)
            self.__is_dirty = True

        elif (not bookmarks and f.full_path in paths):
            idx = paths.index(f.full_path)
            del self.__items[idx]
            media_bookmarks.set_bookmarks(f, [])
            self.__is_dirty = True

        self.__save_bookmarks()
        self.emit_message(msgs.BOOKMARK_EV_INVALIDATED)


    def handle_CORE_EV_DEVICE_ADDED(self, dev_id, device):
        
        self.__needs_reload = True

