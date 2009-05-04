from com import msgs
from Playlist import Playlist
from storage import Device, File
from mediabox import media_bookmarks
from mediabox import values
from utils import urlquote
from utils import logging
from theme import theme

import os

_PLAYLIST_DIR = os.path.join(values.USER_DIR, "playlists")

_PLAYLIST_DEFAULT = "Playlist"
_PLAYLIST_RECENT_50 = "50 Recently Played"
_PLAYLIST_BOOKMARKS = "Bookmarked Files"
_SPECIAL_PLAYLISTS = [_PLAYLIST_DEFAULT,
                      _PLAYLIST_RECENT_50,
                      _PLAYLIST_BOOKMARKS]


class PlaylistDevice(Device):

    CATEGORY = Device.CATEGORY_INDEX
    TYPE = Device.TYPE_GENERIC


    def __init__(self):

        # list of (name, playlist) tuples
        self.__lists = []
        
        # the currently selected playlist
        self.__current_list = None
        
        # the folder of the currently selected playlist
        self.__current_folder = None
        
        # whether the playlists need to be reloaded from files
        self.__needs_playlist_reload = True
               

        Device.__init__(self)


    def get_prefix(self):
        
        return "playlist://"
        
        
    def get_name(self):
    
        return "Lists"
        
        
    def get_icon(self):
    
        return theme.mb_viewer_playlist


    def swap(self, f, idx1, idx2):
    
        self.__current_list.swap(idx1, idx2)
        self.__current_list.save()


    def new_file(self, f):
        """
        Creates a new playlist.
        """
        
        resp, name = self.call_service(msgs.DIALOG_SVC_TEXT_INPUT,
                                       "Create New List",
                                       "Enter name of list:")

        names = [ n for n, pl in self.__lists ]
        if (resp == 0 and name):
            if (name in names):
                self.call_service(msgs.DIALOG_SVC_ERROR,
                                  "Error",
                                  u"There is already a playlist with name " \
                                  "\302\273%s\302\253." % name)

                return None

            pl = self.__create_playlist(name)
            self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, f)
            return pl
            
        else:
            return None
                        
        #end if


    def delete_file(self, folder, idx):
        """
        Removes a playlist or a file from a playlist.
        """
    
        if (folder.path == "/"):
            playlists = [ pl for n, pl in self.__lists ]
            pl = playlists[idx]

            ret = self.call_service(msgs.DIALOG_SVC_QUESTION,
                                    "Delete List",
                            u"Delete the list \xbb%s\xab?" % pl.get_name())
            if (ret == 0):
                if (pl.get_name() == _PLAYLIST_BOOKMARKS):
                    media_bookmarks.clear_all()
                    
                self.__lists = [ (n, p) for n, p in self.__lists
                                 if (p != pl) ]
                pl.delete_playlist()
                self.__ensure_special_playlists()
                self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, folder)
            #end if

        else:
            pl = self.__current_list
            if (pl.get_name() == _PLAYLIST_BOOKMARKS):
                 self.__remove_bookmarks(pl.get_files()[idx])
            
            pl.remove(idx)
            pl.save()
            self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, folder)
            self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, self.get_root())

        #end if


    def __ensure_special_playlists(self):
        """
        Creates the special playlists that are currently missing.
        """

        # create special playlists
        for name in _SPECIAL_PLAYLISTS:
            if (not self.__lookup_playlist(name)):
                self.__create_playlist(name)
        #end for


    def __create_playlist(self, name):
        """
        Creates a new playlist with the given name.
        Returns the file object representing the list.
        """
        
        name = name.encode("utf-8")
        pl_path = os.path.join(_PLAYLIST_DIR,
                               urlquote.quote(name, safe = "") + ".m3u")
        logging.info("creating playlist '%s'" % pl_path)
        pl = Playlist()
        pl.set_name(name)
        pl.save_as(pl_path)
        self.__lists.append((name, pl))


    def __load_playlists(self):
        """
        Loads the available playlists.
        """

        def cb(pl, name, location):
            f = self.call_service(msgs.CORE_SVC_GET_FILE, location)
            if (f):
                pl.append(f)
            else:
                # insert a placeholder for files that are currently
                # not available
                f = File(self)
                f.name = name
                f.info = location
                pl.append(f)


        # create playlist folder if it does not yet exist
        if (not os.path.exists(_PLAYLIST_DIR)):
            try:
                os.makedirs(_PLAYLIST_DIR)
            except:
                pass


        # load playlists
        files = [ f for f in os.listdir(_PLAYLIST_DIR)
                  if f.endswith(".m3u") ]
        for f in files:
            path = os.path.join(_PLAYLIST_DIR, f)
            pl = Playlist()
            pl.load_from_file(path, cb)

            self.__lists.append((pl.get_name(), pl))
        #end for
        
        self.__ensure_special_playlists()            

        # sort by name        
        self.__lists.sort(lambda a,b:cmp(a[0],b[0]))
        self.__current_list = self.__lists[0][1]

        
    def __save_playlists(self):
        """
        Saves all playlists.
        """
        
        for n, pl in self.__lists:
            pl.save()


    def __lookup_playlist(self, name):
    
        for n, pl in self.__lists:
            if (n == name):
                return pl
        #end for
        
        return None
        
        
    def get_root(self):
    
        f = File(self)
        f.name = self.get_name()
        f.path = "/"
        f.mimetype = f.DIRECTORY
        f.folder_flags = f.ITEMS_DELETABLE

        return f


    def get_contents(self, folder, begin_at, end_at, cb, *args):

        if (self.__needs_playlist_reload):
            self.__load_playlists()
            self.__needs_playlist_reload = False

        if (folder.path == "/"):
            folder.folder_flags = folder.ITEMS_ADDABLE
            if (len(self.__lists) > 1):
                folder.folder_flags |= folder.ITEMS_DELETABLE
                
            self.__ls_playlists(begin_at, end_at, cb, *args)
            
        else:
            pl = self.__lookup_playlist(folder.name)
            self.__current_list = pl
            self.__current_folder = folder
            
            if (end_at == 0):
                files = pl.get_files()[begin_at:]
            else:
                files = pl.get_files()[begin_at:end_at]
                
            for f in files:
                cb(f, *args)
            cb(None, *args)


    def __ls_playlists(self, begin_at, end_at, cb, *args):
    
        self.__lists.sort(lambda a,b:cmp(a[0],b[0]))
        playlists = [ pl for n, pl in self.__lists ]
        if (end_at == 0):
            playlists = playlists[begin_at:]
        else:
            playlists = playlists[begin_at:end_at]


        for pl in playlists:
            f = File(self)
            f.name = pl.get_name()
            f.info = "%d items" % pl.get_size()
            f.path = "/" + urlquote.quote(f.name)
            f.mimetype = f.DIRECTORY
            f.icon = theme.mb_viewer_playlist.get_path()
            f.folder_flags = f.ITEMS_SKIPPABLE

            if (pl.get_name() != _PLAYLIST_RECENT_50):
                f.folder_flags |= f.ITEMS_SORTABLE
                f.folder_flags |= f.ITEMS_DELETABLE | \
                                  f.ITEMS_BULK_DELETABLE
            cb(f, *args)
        #end for
        
        cb(None, *args)


    def __add_item_to_playlist(self, pl, f, count = [0]):
        """
        Adds the given item to the playlist.
        """
        
        if (count[0] >= 500): return
        
        if (f):
            # recurse into subfolders
            if (f.mimetype.endswith("-folder")):
                items = [ c for c in f.get_children() ]

                for item in items:
                    count[0] += 1
                    self.__add_item_to_playlist(pl, item, count)
                return
            #end if
        #end if

        pl.append(f)
        
        
    def __remove_bookmarks(self, *files):
    
        for f in files:
            media_bookmarks.set_bookmarks(f, [])


        
    def handle_PLAYLIST_ACT_APPEND(self, f):        

        pl = self.__current_list
        if (pl.get_name() in _SPECIAL_PLAYLISTS):
            pl = self.__lookup_playlist(_PLAYLIST_DEFAULT)
        
        pl_name = pl.get_name()
                
        self.call_service(msgs.NOTIFY_SVC_SHOW_INFO,
                          u"adding \xbb%s\xab to %s" % (f.name, pl_name))
        self.__add_item_to_playlist(pl, f)

        pl.save()
        self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, self.__current_folder)
        self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, self.get_root())


    def handle_MEDIA_EV_LOADED(self, viewer, f):
    
        pl = self.__lookup_playlist(_PLAYLIST_RECENT_50)
        if (not pl): return
        
        #files = pl.get_files()
        paths = [ fl.full_path for fl in pl.get_files() ]
        if (not f.full_path in paths):
            if (len(paths) == 50):
                pl.remove(49)
        else:
            idx = paths.index(f.full_path)
            pl.remove(idx)
        #end if
        pl.prepend(f)
        pl.save()
        
        if (self.__current_list == pl):
            self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED,
                              self.__current_folder)
        self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, self.get_root())


    def handle_MEDIA_EV_BOOKMARKED(self, f, bookmarks):
    
        pl = self.__lookup_playlist(_PLAYLIST_BOOKMARKS)
        if (not pl): return

        paths = [ fl.full_path for fl in pl.get_files() ]
        if (bookmarks and not f.full_path in paths):
            pl.append(f)
        elif (not bookmarks and f.full_path in paths):
            idx = paths.index(f.full_path)
            pl.remove(idx)
        #end if
        pl.save()
        
        if (self.__current_list == pl):
            self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED,
                              self.__current_folder)
        self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, self.get_root())

