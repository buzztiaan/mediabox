from com import msgs
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
    """
    Storage device for browsing music artists.
    """

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_AUDIO
    
    
    _media_was_updated = [False]
    

    def __init__(self):
    

        Device.__init__(self)

        
    def get_prefix(self):
    
        return "audio://artists"
        
        
    def get_name(self):
    
        return "Artists"


    def get_icon(self):
    
        return theme.mb_folder_artist


    def __make_artist(self, artist):
    
        f = File(self)
        f.path = "/" + urlquote.quote(artist, "")
        f.name = artist
        f.acoustic_name = f.name
        f.mimetype = f.DIRECTORY
        f.icon = theme.mb_folder_artist.get_path()
        f.folder_flags = f.ITEMS_ENQUEUEABLE | \
                            f.ITEMS_SKIPPABLE | \
                            f.ITEMS_COMPACT
        return f


    def __make_album(self, ffolder, album):
    
        f = self.call_service(msgs.CORE_SVC_GET_FILE,
                              "audio://albums/%s/%s" \
                              % (urlquote.quote(ffolder, ""),
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
            #f.folder_flags = f.ITEMS_COMPACT
            
        elif (len_parts == 1):
            # artist
            artist = urlquote.unquote(parts[0])
            f = self.__make_artist(artist)
    
        return f
    
    
    def get_contents(self, folder, begin_at, end_at, cb, *args):
    
        path = folder.path

        if (not path.endswith("/")): path += "/"
        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)
        
        items = []
        if (len_parts == 0):
            # list artists
            res = self.call_service(msgs.FILEINDEX_SVC_QUERY,
                                    "Audio.Artist of File.Type='audio'")
            for artist, in res:
                f = self.__make_artist(artist)
                if (f): items.append(f)
            #end for                                    
                       
        elif (len_parts == 1):
            # list albums
            artist = urlquote.unquote(parts[0])
            res = self.call_service(msgs.FILEINDEX_SVC_QUERY,
                      "File.Folder, Audio.Album of and File.Type='audio' Audio.Artist='%s'",
                      artist)
            #res.add(("All Tracks",))
            for ffolder, album in res:
                f = self.__make_album(ffolder, album)
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



    """
    def __on_add_to_playlist(self, folder, f):
    
        self.emit_message(msgs.PLAYLIST_ACT_APPEND, "", f)


    def __on_put_on_dashboard(self, folder, f):
        
        f.bookmarked = True


    def __on_add_to_library(self, folder, f):
    
        self.emit_message(msgs,LIBRARY_ACT_ADD_MEDIAROOT, f)


    def get_file_actions(self, folder, f):
    
        actions = []
        actions.append((None, "Add to Playlist", self.__on_add_to_playlist))
        actions.append((None, "Put on Dashboard", self.__on_put_on_dashboard))
        
        return actions
    """


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

