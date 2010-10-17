from com import msgs
from Playlist import Playlist
from storage import Device, File
from mediabox import values
from ui.dialog import InputDialog
from ui.dialog import OptionDialog
from utils import urlquote
from utils import logging
from theme import theme

import os
import time

_PLAYLIST_DIR = os.path.join(values.USER_DIR, "playlists")

_PLAYLIST_DEFAULT = "Playlist"
_PLAYLIST_RECENT_50 = "Recent 50"
_SPECIAL_PLAYLISTS = [_PLAYLIST_DEFAULT,
                      _PLAYLIST_RECENT_50]


class PlaylistDevice(Device):
    """
    Storage device for browsing and manipulating playlists.
    """

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_SYSTEM


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
    
        return "Playlists"
        
        
    def get_icon(self):
    
        return theme.mb_folder_playlist


    def shift_file(self, folder, pos, amount):
    
        self.__current_list.shift(pos, amount)
        self.__current_list.save()


    def new_file(self, f):
        """
        Creates a new playlist.
        """
        
        dlg = InputDialog("Create New List")
        dlg.add_input("Name:", "")
        resp = dlg.run()
        name = dlg.get_values()[0]

        names = [ n for n, pl in self.__lists ]
        if (resp == dlg.RETURN_OK and name):
            if (name in names):
                self.emit_message(msgs.UI_ACT_SHOW_INFO,
                                  u"There is already a list with name " \
                                  u"\xbb%s\xab." % name)

            else:
                pl = self.__create_playlist(name)
                self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, f)
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

        now = time.time()

        # load playlists
        self.__lists = []
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
        self.__current_folder = None
        
        logging.profile(now, "[playlist] loaded playlists")

        
    def __save_playlists(self):
        """
        Saves all playlists.
        """
        
        now = time.time()
        for n, pl in self.__lists:
            pl.save()
        logging.profile(now, "[playlist] saved playlists")


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
        f.mimetype = f.DEVICE_ROOT
        f.folder_flags = f.ITEMS_ADDABLE #| f.ITEMS_COMPACT
        f.icon = self.get_icon().get_path()

        return f


    def get_file(self, path):

        if (self.__needs_playlist_reload):
            self.__load_playlists()
            self.__needs_playlist_reload = False

        if (path == "/"):
            return self.get_root()
            
        name = urlquote.unquote(path[1:])
        pl = self.__lookup_playlist(name)
        
        if (pl):
            f = File(self)
            f.name = pl.get_name()
            #f.info = "%d items" % pl.get_size()
            f.path = path
            f.mimetype = f.DIRECTORY
            f.icon = theme.mb_folder_playlist.get_path()

            if (pl.get_name() != _PLAYLIST_RECENT_50):
                f.folder_flags |= f.ITEMS_SORTABLE
            return f
        else:
            return None


    def get_contents(self, folder, begin_at, end_at, cb, *args):

        if (self.__needs_playlist_reload):
            self.__load_playlists()
            self.__needs_playlist_reload = False

        if (folder.path == "/"):
            self.__ls_playlists(begin_at, end_at, cb, *args)
            
        else:
            pl = self.__lookup_playlist(folder.name)
            self.__current_list = pl
            self.__current_folder = folder
            
            if (end_at == 0):
                files = pl.get_files()[begin_at:]
            else:
                files = pl.get_files()[begin_at:end_at]
              
            #print "FILES", files  
            for f in files:
                ret = cb(f, *args)
                if (not ret): return
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
            #f.info = "%d items" % pl.get_size()
            f.path = "/" + urlquote.quote(f.name)
            f.mimetype = f.DIRECTORY
            f.icon = theme.mb_folder_playlist.get_path()
            f.folder_flags |= f.ITEMS_UNSORTED

            if (pl.get_name() != _PLAYLIST_RECENT_50):
                f.folder_flags |= f.ITEMS_SORTABLE

            cb(f, *args)
        #end for
        
        cb(None, *args)


    def __add_item_to_playlist(self, pl, f, count = [0]):
        """
        Adds the given item to the playlist.
        """
        
        #if (count[0] >= 500): return
        
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


    def __on_delete_playlist(self, folder, f):

        playlists = [ pl for n, pl in self.__lists if f.name == n ]
        pl = playlists[0]

        self.__lists = [ (n, p) for n, p in self.__lists
                         if (p != pl) ]
        pl.delete_playlist()
        self.__ensure_special_playlists()
        self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, folder)


    def __on_clear_playlist(self, folder, f):
    
        playlists = [ pl for n, pl in self.__lists if f.name == n ]
        pl = playlists[0]       
        
        pl.clear()
        pl.save()
        self.emit_message(msgs.UI_ACT_SHOW_INFO, u"\xbb%s\xab cleared." % f.name)


    def __on_delete_item(self, folder, *files):
    
        pl = self.__current_list
        for f in files:
            idx = pl.get_files().index(f)
            pl.remove(idx)
        #end for
        pl.save()
        self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, folder)


    def __on_put_on_shelf(self, folder, f):
    
        f.bookmarked = True


    def get_file_actions(self, folder, f):
    
        options = []
        if (folder.path == "/"):
            options.append((None, "Put on Shelf", self.__on_put_on_shelf))
            options.append((None, "Clear List", self.__on_clear_playlist))

            if (not f.name in _SPECIAL_PLAYLISTS):
                options.append((None, "Delete List", self.__on_delete_playlist))
                #options.append((None, "Rename", self.__on_delete_playlist))

        else:
            options.append((None, "Remove from List", self.__on_delete_item))

        return options
        
        
    def get_bulk_actions(self, folder):

        options = []
        if (folder.path != "/"):
            options.append((None, "Remove from List", self.__on_delete_item))

        return options
    
        
        
        
    def handle_PLAYLIST_SVC_GET_LISTS(self):

        if (self.__needs_playlist_reload):
            self.__load_playlists()
            self.__needs_playlist_reload = False

        names = [ n for n, pl in self.__lists
                  if not n in [_PLAYLIST_RECENT_50] ]
        return names


    def handle_PLAYLIST_ACT_APPEND(self, pl_name, *files):        

        if (self.__needs_playlist_reload):
            self.__load_playlists()
            self.__needs_playlist_reload = False

        playlist = None
        if (not pl_name):
            dlg = OptionDialog("Select a Playlist")
        
            playlists = [ pl for n, pl in self.__lists
                          if not n in [_PLAYLIST_RECENT_50] ]
            for pl in playlists:
                dlg.add_option(None, pl.get_name())
            if (dlg.run() == 0):
                choice = dlg.get_choice()
                playlist = playlists[choice]
                
        else:
            playlist = self.__lookup_playlist(pl_name)

        #end if

        if (playlist):
            now = time.time()

            self.emit_message(msgs.UI_ACT_SHOW_INFO,
                          u"Adding %d items to %s" \
                          % (len(files), playlist.get_name()))
            count = [0]
            for f in files:
                self.__add_item_to_playlist(playlist, f, count)

            logging.profile(now, "[playlist] added %d items to %s",
                            count[0], playlist.get_name())

            playlist.save()
            self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED,
                              self.__current_folder)
        #end if


    def handle_MEDIA_EV_LOADED(self, viewer, f):
    
        if (self.__needs_playlist_reload):
            self.__load_playlists()
            self.__needs_playlist_reload = False
    
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


    def handle_CORE_EV_DEVICE_ADDED(self, dev_id, device):
        
        self.__needs_playlist_reload = True
        self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, self.__current_folder)

