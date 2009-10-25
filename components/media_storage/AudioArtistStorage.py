from com import msgs
from MusicIndex import MusicIndex
from storage import Device, File
from utils import urlquote
from utils import logging
from utils import threads
from mediabox import tagreader
from mediabox import values
from theme import theme

import os
import gtk
import gobject
import threading



class AudioArtistStorage(Device):

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_AUDIO
    
    
    _media_was_updated = [False]
    
    __index = MusicIndex()

    def __init__(self):
    

        Device.__init__(self)

        
 
    def handle_MEDIASCANNER_EV_SCANNING_FINISHED(self):
    
        #self.__index.schedule_scanner(self.__update_media)
        #self.__update_media()
        #self.__index.save()
        self._media_was_updated[0] = True


    def __update_media(self):

        def f():
            # add new files to index
            total_length = len(added)
            cnt = 0
            for path in added:
                cnt += 1
                percent = int((cnt / float(total_length)) * 100)
                self.emit_message(msgs.UI_ACT_SHOW_MESSAGE,
                                  "Updating Index",
                                  #"- %s -" % folder.name,
                                  "- %d%% complete -" % (percent),
                                  self.get_icon())
                                
                #self.__index.remove_file(path)
                self.__index.add_file(path)
            #end for
            
            # delete removed files from index
            for path in removed:
                self.__index.remove_file(path)
            #end for

            self.emit_message(msgs.UI_ACT_HIDE_MESSAGE)
          

        media, added, removed = \
                self.call_service(msgs.MEDIASCANNER_SVC_GET_MEDIA,
                                 ["audio/"])
        print "ADDED", added
        print "REMOVED", removed
        if (not media):
            self.__index.clear()
        #finished = threading.Event()
        #gobject.idle_add(f)        
        #threads.wait_for(lambda :finished.isSet())
        f()
        
        
    def _check_for_updated_media(self):
    
        if (self._media_was_updated[0]):
            self.__update_media()
            self.__index.save()
            self._media_was_updated[0] = False

        
    def get_index(self):
    
        return self.__index
        
        
    def _list_files(self, artist, album):

        if (album == "All Tracks"):
            albums = self.__index.list_albums_by_artist(artist)
        else:
            albums = [album]
            
        files = []
        for album in albums:
            for path in self.__index.list_files(album):
                files.append(path)
            #end for
        #end for

        return files

        
    def get_prefix(self):
    
        return "audio://artists"
        
        
    def get_name(self):
    
        return "Artists"


    def get_icon(self):
    
        return theme.mb_device_artists


    def __make_artist(self, artist):
    
        f = File(self)
        f.path = "/" + urlquote.quote(artist, "")
        f.name = artist
        f.acoustic_name = f.name
        f.mimetype = f.DIRECTORY
        f.icon = theme.mb_device_artists.get_path()
        f.folder_flags = f.ITEMS_ENQUEUEABLE | \
                            f.ITEMS_SKIPPABLE | \
                            f.ITEMS_COMPACT
        return f


    def __make_album(self, artist, album):
    
        f = self.call_service(msgs.CORE_SVC_GET_FILE,
                              "audio://albums/%s/%s" \
                              % (urlquote.quote(artist, ""),
                                 urlquote.quote(album, "")))
        return f
 

    def get_file(self, path):

        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)

        f = None
        if (len_parts == 0):
            # root folder
            f = File(self)
            f.is_local = True
            f.can_skip = True
            f.path = "/"
            f.mimetype = f.DEVICE_ROOT
            f.resource = ""
            f.name = self.get_name()
            f.icon = self.get_icon().get_path()
            f.info = "Browse your music library by artist"
            f.folder_flags = f.ITEMS_COMPACT
            
        elif (len_parts == 1):
            # artist
            artist = urlquote.unquote(parts[0])
            f = self.__make_artist(artist)
    
        return f
    
    
    def get_contents(self, folder, begin_at, end_at, cb, *args):
    
        self._check_for_updated_media()
        path = folder.path

        if (not path.endswith("/")): path += "/"
        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)
        index = self.get_index()
        
        items = []
        if (len_parts == 0):
            # list artists
            for artist in index.list_artists():
                f = self.__make_artist(artist)
                if (f): items.append(f)
            #end for
            
        elif (len_parts == 1):
            # list albums
            artist = urlquote.unquote(parts[0])
            for album in ["All Tracks"] + index.list_albums_by_artist(artist):
                f = self.__make_album(artist, album)
                if (f): items.append(f)
            #end for
        
        items.sort()
        cnt = -1
        for item in items:
            cnt += 1
            if (cnt < begin_at): continue
            if (end_at and cnt > end_at): break
            cb(item, *args)
        #end for
        cb(None, *args)
    

    def __on_put_on_dashboard(self, folder, f):
    
        f.bookmarked = True


    def get_file_actions(self, folder, f):
    
        actions = []
        actions.append((None, "Put on Dashboard", self.__on_put_on_dashboard))
        return actions



    def load(self, resource, maxlen, cb, *args):
    
        fd = open(resource, "r")
        fd.seek(0, 2)
        total_size = fd.tell()
        fd.seek(0)
        read_size = 0
        while (True):
            d = fd.read(65536)
            read_size += len(d)
            
            try:
                cb(d, read_size, total_size, *args)
            except:
                break
            
            if (d and maxlen > 0 and read_size >= maxlen):
                try:
                    cb("", read_size, total_size, *args)
                except:
                    pass
                break
            elif (not d):
                break
        #end while

