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
        f.path = File.pack_path("/artists", artist)
        f.name = artist
        f.acoustic_name = f.name
        f.mimetype = f.DIRECTORY
        f.icon = theme.mb_folder_artist.get_path()
        f.folder_flags = f.ITEMS_ENQUEUEABLE | \
                            f.ITEMS_COMPACT
        return f


    def __make_album(self, ffolder, album):
    
        path = File.pack_path("/albums", ffolder, album)
        f = self.call_service(msgs.CORE_SVC_GET_FILE,
                              "audio://albums" + path)
        return f
 

    def get_file(self, path):

        parts = File.unpack_path(path)
        prefix = parts[0]

        f = None
        if (prefix == "/"):
            # root folder
            f = File(self)
            f.is_local = True
            f.path = "/"
            f.mimetype = f.DEVICE_ROOT
            f.resource = ""
            f.name = self.get_name()
            f.icon = self.get_icon().get_path()
            f.info = "Browse your music library by artist"
            #f.folder_flags = f.ITEMS_COMPACT
            
        elif (prefix == "/artists"):
            # artist
            artist = parts[1]
            f = self.__make_artist(artist)
    
        return f
    
    
    def get_contents(self, folder, begin_at, end_at, cb, *args):
    
        path = folder.path
        parts = File.unpack_path(path)
        prefix = parts[0]
        
        items = []
        if (prefix == "/"):
            # list artists
            res = self.call_service(msgs.FILEINDEX_SVC_QUERY,
                                    "Audio.Artist of File.Type='audio'")
            for artist, in res:
                f = self.__make_artist(artist)
                if (f): items.append(f)
            #end for                                    
                       
        elif (prefix == "/artists"):
            # list albums
            artist = parts[1]
            res = self.call_service(msgs.FILEINDEX_SVC_QUERY,
                      "File.Folder, Audio.Album " \
                      "of and File.Type='audio' Audio.Artist='%s'",
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

