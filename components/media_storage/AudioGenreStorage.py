from com import msgs
from AudioArtistStorage import AudioArtistStorage
from MusicIndex import MusicIndex
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



class AudioGenreStorage(AudioArtistStorage):

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_AUDIO
    

    def __init__(self):
    
        AudioArtistStorage.__init__(self)

       
    def get_prefix(self):
    
        return "audio://genres"
        
        
    def get_name(self):
    
        return "Genres"


    def get_icon(self):
    
        return theme.mb_device_genres

        
    def __make_genre(self, genre):
    
        f = File(self)
        f.path = "/" + urlquote.quote(genre, "")
        f.name = genre
        f.acoustic_name = genre
        f.mimetype = f.DIRECTORY
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
    
        self._check_for_updated_media()
        path = folder.path

        if (not path.endswith("/")): path += "/"
        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)
        
        items = []
        if (len_parts == 0):
            # list genres
            for genre in self.get_index().list_genres():
                f = self.__make_genre(genre)
                if (f): items.append(f)
            #end for
            
        elif (len_parts == 1):
            # list albums
            genre = urlquote.unquote(parts[0])
            for artist in self.get_index().list_artists():
                query = "genre=%s,artist=%s" % (genre, artist)
                for album in self.get_index().query_albums(query):
                    f = self.__make_album(artist, album)
                    if (f): items.append(f)
                #end for
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

