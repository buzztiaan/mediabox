from com import msgs
from Playlist import Playlist
from storage import Device, File
from mediabox import values
from utils import urlquote
from utils import logging
from theme import theme

import os

_PLAYLIST_DIR = os.path.join(values.USER_DIR, "playlists")


class PlaylistDevice(Device):

    CATEGORY = Device.CATEGORY_INDEX
    TYPE = Device.TYPE_GENERIC


    def __init__(self):
    
        # table: name -> playlist
        self.__lists = {}
        self.__current_list = None
        self.__current_items = []

        self.__needs_playlist_reload = True
    
        Device.__init__(self)
        
        
        
    def get_prefix(self):
        
        return "playlist://"
        
        
    def get_name(self):
    
        return "Playlists"
        
        
    def get_icon(self):
    
        return theme.mb_viewer_playlist
        
        
    def get_root(self):
    
        f = File(self)
        f.name = self.get_name()
        f.path = "/"
        f.mimetype = f.DIRECTORY

        return f


    def new_file(self, f):
        """
        Creates a new playlist.
        """
        
        resp, name = self.call_service(msgs.DIALOG_SVC_TEXT_INPUT,
                                       "Create New Playlist",
                                       "Enter name of playlist:")
        #dlg = Dialog()
        #dlg.add_entry("Name of Playlist:")
        #dlg.set_title("New Playlist")
        #values = dlg.wait_for_values()

        if (resp == 0 and name):
        #if (values):
        #    name = values[0]
            if (self.__lists.has_key(name)):
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
    
        f = self.__current_items[idx]
        is_playlist = (f.mimetype == f.DIRECTORY)

        if (is_playlist):
            pl = self.__lists[f.name]
            ret = self.call_service(msgs.DIALOG_SVC_QUESTION,
                                    "Delete Playlist",
                            u"Delete the playlist \xbb%s\xab?" % pl.get_name())
            if (ret == 0):
                pl.delete_playlist()
                del self.__lists[f.name]
                self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, folder)
            #end if
            
        else:
            pl = self.__current_list
            pl.remove(idx)
            pl.save()
            self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, folder)
        #end if
        

    def swap(self, f, idx1, idx2):
    
        self.__current_list.swap(idx1, idx2)
        self.__current_list.save()


    def __create_playlist(self, name):
        """
        Creates a new playlist with the given name.
        Returns the file object representing the list.
        """

        pl_path = os.path.join(_PLAYLIST_DIR,
                                urlquote.quote(name, safe = "") + ".m3u")
        logging.info("creating playlist '%s'" % pl_path)
        pl = Playlist()
        pl.set_name(name)
        pl.save_as(pl_path)
        self.__lists[name] = pl
        
        f = File(self)
        f.path = "/" + name.replace("/", "_")
        f.name = name
        f.info = "%d items" % 0
        f.mimetype = f.DIRECTORY
        f.folder_flags = f.ITEMS_DELETABLE | f.ITEMS_SKIPPABLE
        
        return f
        

    def __load_playlists(self):
        """
        Loads the available playlists.
        """

        def cb(pl, name, location):
            f = self.call_service(msgs.CORE_SVC_GET_FILE, location)
            if (f):
                pl.append(None, None, f)
                #self.__add_item(pl, f)
            else:
                # insert a placeholder for files that are currently
                # not available
                pl.append(None, None, f)
                #self.__add_item(pl, None)


        # create playlist folder if it does not yet exist
        if (not os.path.exists(_PLAYLIST_DIR)):
            try:
                os.makedirs(_PLAYLIST_DIR)
            except:
                pass

        # initialize playqueue
        #if (self.__lists):
        #    queue = self.__lists["Queue"]
        #else:
        #    queue = Playlist()
        #    queue.set_name("Queue")
            
        #self.__lists["Queue"] = queue

        # load playlists
        files = [ f for f in os.listdir(_PLAYLIST_DIR)
                  if f.endswith(".m3u") ]
        for f in files:
            path = os.path.join(_PLAYLIST_DIR, f)
            pl = Playlist()
            pl.load_from_file(path, cb)

            self.__lists[pl.get_name()] = pl
        #end for
        
        if (not self.__lists):
            self.__create_playlist("Playlist")
        
        names = self.__lists.keys()
        names.sort()
        self.__current_list = self.__lists[names[0]]

        
    def __save_playlists(self):
        """
        Saves all playlists.
        """
        
        for pl in self.__lists.values():
            pl.save()


    def get_contents(self, folder, begin_at, end_at, cb, *args):

        path = folder.path
        if (self.__needs_playlist_reload):
            self.__load_playlists()
            self.__needs_playlist_reload = False
    
        if (path == "/"):
            folder.folder_flags = folder.ITEMS_ADDABLE
            if (len(self.__lists) > 1):
                folder.folder_flags |= folder.ITEMS_DELETABLE

            self.__ls_playlists(begin_at, end_at, cb, *args)
    
        else:
            pl_name = path.replace("/", "")
            pl = self.__lists[pl_name]
            self.__current_list = pl

            if (end_at == 0):
                entries = pl.get_files()[begin_at:]
            else:
                entries = pl.get_files()[begin_at:end_at]
                
            self.__current_items = []
            for f in entries:
                self.__current_items.append(f)
                cb(f, *args)
            #end for
            
            cb(None, *args)
            
    
    
    def __ls_playlists(self, begin_at, end_at, cb, *args):
    
        if (end_at == 0):
            entries = self.__lists.values()[begin_at:]
        else:
            entries = self.__lists.values()[begin_at:end_at]
            
        self.__current_items = []
        for playlist in entries:
            f = File(self)
            # TODO: use urlquote
            f.path = "/" + playlist.get_name().replace("/", "_")
            f.name = playlist.get_name()
            f.info = "%d items" % len(playlist.get_files())
            f.mimetype = f.DIRECTORY
            f.icon = theme.mb_viewer_playlist.get_path()
            f.folder_flags = f.ITEMS_DELETABLE | \
                             f.ITEMS_SKIPPABLE | \
                             f.ITEMS_SORTABLE

            self.__current_items.append(f)
            cb(f, *args)
        #end for
        cb(None, *args)
        

    def __add_item(self, pl, f, count = [0]):
        """
        Adds the given item to the playlist.
        """
        
        if (count[0] >= 500): return
        
        if (f):
            if (f.mimetype.endswith("-folder")):
                items = [ c for c in f.get_children() ]
                          #if not c.mimetype.endswith("-folder") ]
                for item in items:
                    count[0] += 1
                    self.__add_item(pl, item, count)
                return
            #end if
        #end if

        pl.append(None, None, f)
        

    def handle_PLAYLIST_ACT_APPEND(self, f):        

        pl = self.__current_list
        pl_name = pl.get_name()
        
        #if (len(files) == 1):
        self.call_service(msgs.NOTIFY_SVC_SHOW_INFO,
                          u"adding \xbb%s\xab to %s" % (f.name, pl_name))
        #else:
        #    self.call_service(msgs.NOTIFY_SVC_SHOW_INFO,
        #                    u"adding %d items to %s" % (len(files), pl_name))
                            
        #for f in files:
        #    logging.info("adding '%s' to %s" % (f.name, pl_name))
        self.__add_item(pl, f)
        pl.save()
        #self.__update_playlist_thumbnail()


