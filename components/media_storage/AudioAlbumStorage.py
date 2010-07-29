from com import msgs
from AudioArtistStorage import AudioArtistStorage
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



class AudioAlbumStorage(Device):
    """
    Storage device for browsing music albums.
    """

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_AUDIO
    

    def __init__(self):
    
        self.__cache = []
        Device.__init__(self)


        
    def get_prefix(self):
    
        return "audio://albums"
        
        
    def get_name(self):
    
        return "Albums"


    def get_icon(self):
    
        return theme.mb_folder_audio


    def __make_album(self, ffolder, album):

        f = File(self)
        f.is_local = True
        try:
            ff = urlquote.quote(ffolder, "")
        except:
            ff = "?"
        try:
            al = urlquote.quote(album, "")
        except:
            al = "?"
        f.path = "/" + ff + \
                 "/" + al
        f.name = album
        f.acoustic_name = f.name
        #f.info = artist
        f.mimetype = "application/x-music-folder"
        f.folder_flags = f.ITEMS_ENQUEUEABLE
        f.comparable = f.name

        if (album == "All Tracks"):
            f.icon = theme.mb_folder_audio.get_path()

        return f
        
        
    def __make_track(self, ffolder, album, resource):
    
        f = self.call_service(msgs.CORE_SVC_GET_FILE, resource)
        if (not f): return None
        
        tags = tagreader.get_tags(f)
        f.name = tags.get("TITLE") or f.name
        f.info = tags.get("ARTIST") or "unknown"
        f.acoustic_name = f.name + ", by " + f.info
        #f.path = "/" + urlquote.quote(artist, "") + \
        #         "/" + urlquote.quote(album, "") + \
        #         "/" + urlquote.quote(resource, "")

        try:
            trackno = tags.get("TRACKNUMBER")
            trackno = trackno.split("/")[0]
            trackno = int(trackno)
        except:
            trackno = 0

        if (album == "All Tracks"):
            f.comparable = f.name.upper()
        else:
            f.comparable = trackno
        
        return f       


    def get_file(self, path):

        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)
        
        f = None
        if (len_parts == 0):
            # root folder
            f = File(self)
            f.is_local = True
            f.path = "/"
            f.mimetype = f.DIRECTORY
            f.resource = ""
            f.name = self.get_name()
            f.info = "Browse your music library by album"
            f.icon = self.get_icon().get_path()
            f.folder_flags = f.ITEMS_ENQUEUEABLE | f.ITEMS_COMPACT            
            
        elif (len_parts == 2):
            # album
            ffolder = urlquote.unquote(parts[0])
            album = urlquote.unquote(parts[1])
            f = self.__make_album(ffolder, album)

        elif (len_parts == 3):
            # track
            artist = urlquote.unquote(parts[0])
            album = urlquote.unquote(parts[1])
            resource = urlquote.unquote(parts[1])
            f = self.__make_track(artist, album, resource)
        
        return f

   
    def get_contents(self, folder, begin_at, end_at, cb, *args):

        def file_cmp(a, b):
            if (a.name == "All Tracks"):
                return -1
            if (b.name == "All Tracks"):
                return 1
            else:
                return cmp(a.comparable, b.comparable)

        path = folder.path

        if (not path.endswith("/")): path += "/"
        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)
        
        items = []
        
        if (len_parts == 0):
            if (self.__cache):
                items += self.__cache
            else:
                # list albums
                res = self.call_service(msgs.FILEINDEX_SVC_QUERY,
                                  "File.Folder, Audio.Album of File.Type='audio'")
                res.add(("All Tracks", "All Tracks"))
                for ffolder, album in res:
                    if (not album): continue
                    f = self.__make_album(ffolder, album)
                    if (f): items.append(f)
                #end for
                self.__cache = items[:]
            #end if
                         
        elif (len_parts == 2):
            # list tracks
            ffolder = urlquote.unquote(parts[0])
            album = urlquote.unquote(parts[1])
            #if (album == "All Tracks"):
            #    query = "File.Path of and File.Type='audio' File.Folder='%s'"
            #    query_args = (artist,)
            
            if (album == "All Tracks"):
                query = "File.Path of File.Type='audio'"
                query_args = ()
            else:
                query = "File.Path of and and File.Type='audio' " \
                        "File.Folder='%s' Audio.Album='%s'"
                query_args = (ffolder, album)
            
            res = self.call_service(msgs.FILEINDEX_SVC_QUERY,
                                    query, *query_args)
            for filepath, in res:
                f = self.__make_track(ffolder, album, filepath)
                if (f): items.append(f)
            #end for                
            
        #end if
        
        items.sort(file_cmp)

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


    def handle_FILEINDEX_ACT_SCAN(self):
    
        self.__cache = []
        
        
    def handle_FILEINDEX_ACT_SCAN_FOLDER(self, path):
    
        self.__cache = []

