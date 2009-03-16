from com import msgs

from storage import Device, File
from utils import logging
from mediabox import tagreader
from theme import theme

import os
import commands



class AudioStorage(Device):

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_AUDIO
    

    def __init__(self):
    
        self.__albums = []
        self.__media_was_updated = False
    
        Device.__init__(self)
        
        
    def handle_message(self, msg, *args):
    
        if (msg == msgs.MEDIASCANNER_EV_SCANNING_FINISHED):
            #self.__update_media()
            self.__media_was_updated = True


    def __update_media(self):
    
        self.__albums = []

        media, nil, nil = self.call_service(msgs.MEDIASCANNER_SVC_GET_MEDIA,
                                            [File.DIRECTORY])
        for f in media:
            self.__albums.append(f)
        #end for
        self.__albums.sort()
        
        self.__media_was_updated = False
          
        
    def get_prefix(self):
    
        return "library://audio-folders"
        
        
    def get_name(self):
    
        return "Music Folders"


    def get_icon(self):
    
        return theme.mb_device_folders


    def get_root(self):
    
        f = File(self)
        f.is_local = True
        f.path = "/"
        f.can_skip = True
        f.mimetype = f.DIRECTORY
        f.resource = ""
        f.name = self.get_name()
        f.info = "Browse your music library by folders"
        
        return f


    def get_file(self, path):
    
        f = File(self)
    
    
    def ls_async(self, path, cb, *args):
    
        if (self.__media_was_updated):
            self.__update_media()
    
        if (path == "/"):
            for album in self.__albums:
                f = File(self)
                f.is_local = True
                f.can_skip = True
                f.name = album.name
                f.info = album.info
                f.mimetype = "application/x-music-folder"
                f.thumbnail_md5 = album.md5
                f.path = album.path
                f.resource = album.resource

                cb(f, *args)
            #end for
            
            cb(None, *args)
            
        else:
            album = None
            for a in self.__albums:
                if (a.path == path):
                    album = a
                    break
            #end for
            
            if (not album): return

            tracks = []
            for f in album.get_children():
                if (not f.mimetype.startswith("audio")):
                    continue
                                   
                tags = tagreader.get_tags(f)
                f.name = tags.get("TITLE") or f.name
                f.info = tags.get("ARTIST") or "unknown"
                try:
                    trackno = tags.get("TRACKNUMBER")
                    trackno = trackno.split("/")[0]
                    trackno = int(trackno)
                except:
                    trackno = 0
                f.index = trackno
                f.thumbnail_md5 = album.thumbnail_md5
                
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

