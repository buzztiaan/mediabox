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


    def handle_message(self, msg, *args):
    
        pass

        
    def get_prefix(self):
    
        return "library://audio-albums"
        
        
    def get_name(self):
    
        return "Albums"


    def get_icon(self):
    
        return theme.mb_device_audio



    def get_root(self):
    
        f = File(self)
        f.is_local = True
        f.can_skip = True
        f.path = "/"
        f.mimetype = f.DIRECTORY
        f.resource = ""
        f.name = self.get_name()
        f.info = "Browse your music library by album"
        
        return f
          
    
    
    def ls_async(self, path, cb, *args):

        if (not path.endswith("/")): path += "/"
        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)
        index = self.get_index()
        
        if (len_parts == 0):
            for album in index.list_albums():
                #children = index.list_files(album)
                #if (children):
                #    f = self.call_service(msgs.CORE_SVC_GET_FILE, children[0])
                #    tags = tagreader.get_tags(f)
                #    artist = tags.get("ARTIST") or "unknown"
                #else:
                #    artist = "unknown"
            
                f = File(self)
                f.is_local = True
                f.path = path + urlquote.quote(album, "")
                f.can_skip = True
                f.name = album
                #f.info = artist
                f.mimetype = "application/x-music-folder"

                cb(f, *args)
            #end for

            cb(None, *args)
            
        else:
            album = urlquote.unquote(parts[0])
            tracks = []
            
            for filepath in index.list_files(album):
                f = self.call_service(msgs.CORE_SVC_GET_FILE, filepath)
                
                tags = tagreader.get_tags(f)
                f.name = tags.get("TITLE") or f.name
                f.info = tags.get("ARTIST") or "unknown"
                al = tags.get("ALBUM")

                try:
                    trackno = tags.get("TRACKNUMBER")
                    trackno = trackno.split("/")[0]
                    trackno = int(trackno)
                except:
                    trackno = 0
                f.index = trackno

                tracks.append(f)
            #end for

            tracks.sort()
            for trk in tracks:            
                cb(trk, *args)
            cb(None, *args)
            
        #end if        




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

