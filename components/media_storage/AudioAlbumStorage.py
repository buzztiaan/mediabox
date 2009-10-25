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



class AudioAlbumStorage(AudioArtistStorage):

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_AUDIO
    

    def __init__(self):
    
        AudioArtistStorage.__init__(self)


        
    def get_prefix(self):
    
        return "audio://albums"
        
        
    def get_name(self):
    
        return "Albums"


    def get_icon(self):
    
        return theme.mb_device_audio


    def __make_album(self, artist, album):

        f = File(self)
        f.is_local = True
        f.path = "/" + urlquote.quote(artist, "") + \
                 "/" + urlquote.quote(album, "")
        f.name = album
        f.acoustic_name = f.name
        #f.info = artist
        f.mimetype = "application/x-music-folder"
        f.folder_flags = f.ITEMS_ENQUEUEABLE | \
                         f.ITEMS_SKIPPABLE

        return f
        
        
    def __make_track(self, artist, album, resource):
    
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
        f.index = trackno
        
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
            f.mimetype = f.DIRECTORY
            f.resource = ""
            f.name = self.get_name()
            f.info = "Browse your music library by album"
            f.icon = self.get_icon().get_path()
            f.folder_flags = f.ITEMS_ENQUEUEABLE | f.ITEMS_COMPACT            
            
        elif (len_parts == 2):
            # album
            artist = urlquote.unquote(parts[0])
            album = urlquote.unquote(parts[1])
            f = self.__make_album(artist, album)

        elif (len_parts == 3):
            # track
            artist = urlquote.unquote(parts[0])
            album = urlquote.unquote(parts[1])
            resource = urlquote.unquote(parts[1])
            f = self.__make_track(artist, album, resource)
        
        return f

   
    def get_contents(self, folder, begin_at, end_at, cb, *args):
    
        self._check_for_updated_media()
        path = folder.path

        if (not path.endswith("/")): path += "/"
        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)
        index = self.get_index()
        
        items = []
        alphabetical = False
        if (len_parts == 0):
            # list albums
            for artist in self.get_index().list_artists():
                for album in self.get_index().list_albums_by_artist(artist):
                    f = self.__make_album(artist, album)
                    if (f): items.append(f)
                #end for
            #end for
            
        elif (len_parts == 2):
            # list tracks
            artist = urlquote.unquote(parts[0])
            album = urlquote.unquote(parts[1])
            if (album == "All Tracks"):
                album = "*"
                alphabetical = True
            query = "artist=%s,album=%s" % (artist, album)
            for filepath in self.get_index().query_files(query):
                f = self.__make_track(artist, album, filepath)
                if (f): items.append(f)
            #end for
        #end if
        
        if (alphabetical):
            items.sort(lambda a,b:cmp(a.name, b.name))
        else:
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

