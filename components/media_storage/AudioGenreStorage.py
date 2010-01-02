from com import msgs
from storage import Device, File
from utils import urlquote
from utils import logging
from mediabox import tagreader
from mediabox import values
from theme import theme

import os
import gtk
import gobject
import threading



class AudioGenreStorage(Device):
    """
    Storage device for browsing music genres.
    """

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_AUDIO
    

    def __init__(self):
    
        Device.__init__(self)

       
    def get_prefix(self):
    
        return "audio://genres"
        
        
    def get_name(self):
    
        return "Genres"


    def get_icon(self):
    
        return theme.mb_folder_genre

        
    def __make_genre(self, genre):
    
        f = File(self)
        f.path = "/" + urlquote.quote(genre, "")
        f.name = genre
        f.acoustic_name = genre
        f.mimetype = f.DIRECTORY
        f.icon = theme.mb_folder_genre.get_path()
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
            f.info = "Browse your music library by genre"

        elif (len_parts == 1):
            # genre
            genre = urlquote.unquote(parts[0])
            f = self.__make_genre(genre)

        return f
        
        
    def get_contents(self, folder, begin_at, end_at, cb, *args):
    
        path = folder.path

        if (not path.endswith("/")): path += "/"
        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)
        
        items = []
        if (len_parts == 0):
            # list genres
            res = self.call_service(msgs.FILEINDEX_SVC_QUERY,
                                    "Audio.Genre of File.Type='audio'")
            for genre, in res:
                f = self.__make_genre(genre)
                if (f): items.append(f)
            #end for
            
        elif (len_parts == 1):
            # list albums
            genre = urlquote.unquote(parts[0])
            res = self.call_service(msgs.FILEINDEX_SVC_QUERY,
                         "Audio.Artist, Audio.Album of and File.Type='audio'" \
                         "Audio.Genre='%s'",
                         genre)
            for artist, album in res:
                f = self.__make_album(artist, album)
                if (f): items.append(f)
            #end for
        #end if
        
        items.sort()
        cnt = -1
        for item in items:
            cnt += 1
            if (cnt < begin_at): continue
            if (end_at and cnt > end_at): break
            cb(item, *args)
        #end for
        cb(None, *args)


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

