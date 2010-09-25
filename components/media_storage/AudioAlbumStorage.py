from com import msgs
from AudioArtistStorage import AudioArtistStorage
from storage import Device, File
from utils import urlquote
from utils import logging
from mediabox import tagreader
from mediabox import values
from theme import theme

import os



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
        f.path = File.pack_path("/albums", ffolder, album)
        f.name = album
        f.acoustic_name = f.name
        #f.info = artist
        f.mimetype = "application/x-music-folder"
        f.folder_flags = f.ITEMS_ENQUEUEABLE
        f.comparable = f.name

        if (album == "All Tracks"):
            f.icon = theme.mb_folder_audio.get_path()

        return f
        
        
    #def __make_track(self, ffolder, album, resource, mimetype = "", f_title = "", f_artist = ""):
    
    def __make_track(self, artist, album, title, trackno, resource, mimetype):
    
        #f = self.call_service(msgs.CORE_SVC_GET_FILE, resource)
        #if (not f): return None

        path = File.pack_path("/tracks", artist, album, title, trackno,
                              resource, mimetype)
        
        f = File(self)
        f.path = path
        f.is_local = True
        f.resource = resource
        f.name = title
        f.info = artist or "unknown"
        f.mimetype = mimetype
        f.acoustic_name = f.name + ", by " + f.info

        if (album == "All Tracks"):
            f.comparable = f.name.upper()
        else:
            f.comparable = trackno
        
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
            f.mimetype = f.DIRECTORY
            f.resource = ""
            f.name = self.get_name()
            f.info = "Browse your music library by album"
            f.icon = self.get_icon().get_path()
            f.folder_flags = f.ITEMS_ENQUEUEABLE | f.ITEMS_COMPACT            
            
        elif (prefix == "/albums"):
            # album
            ffolder, album = parts[1:]
            f = self.__make_album(ffolder, album)

        elif (prefix == "/tracks"):
            # track
            artist, album, title, trackno, resource, mimetype = parts[1:]
            f = self.__make_track(artist, album, title, trackno, resource, mimetype)
        
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
        parts = File.unpack_path(path)
        prefix = parts[0]

        
        items = []
        
        if (prefix == "/"):
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
                         
        elif (prefix == "/albums"):
            # list tracks
            ffolder, album = parts[1:]
            
            if (album == "All Tracks"):
                query = "File.Path, File.Format, " \
                        "Audio.Title, Audio.Artist, Audio.Tracknumber " \
                        "of File.Type='audio'"
                query_args = ()
            else:
                query = "File.Path, File.Format, " \
                        "Audio.Title, Audio.Artist, Audio.Tracknumber " \
                        "of and and File.Type='audio' " \
                        "File.Folder='%s' Audio.Album='%s'"
                query_args = (ffolder, album)
            
            res = self.call_service(msgs.FILEINDEX_SVC_QUERY,
                                    query, *query_args)
            for filepath, mimetype, title, artist, trackno in res:
                f = self.__make_track(artist, album, title, trackno, filepath, mimetype)
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
    

    def handle_FILEINDEX_ACT_SCAN(self):
    
        self.__cache = []
        
        
    def handle_FILEINDEX_ACT_SCAN_FOLDER(self, path):
    
        self.__cache = []


    def handle_FILEINDEX_EV_FINISHED_SCANNING(self):
    
        self.__cache = []

