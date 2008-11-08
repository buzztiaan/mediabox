from com import msgs

from storage import Device, File
from utils import logging
from mediabox import tagreader
import theme

import os
import commands



class AudioStorage(Device):

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_AUDIO
    

    def __init__(self):
    
        self.__albums = []
    
        Device.__init__(self)
        
        
    def handle_event(self, msg, *args):
    
        if (msg == msgs.MEDIASCANNER_EV_SCANNING_FINISHED):
            self.__update_media()


    def __update_media(self):
    
        self.__albums = []
        
        media = self.call_service(msgs.MEDIASCANNER_SVC_GET_MEDIA,
                                  ["audio/"])
        for f in media:
            self.__albums.append(f)            
        #end for
          
        
    def get_prefix(self):
    
        return "library://audio"
        
        
    def get_name(self):
    
        return "Albums"


    def get_icon(self):
    
        return theme.mb_device_audio


    def get_root(self):
    
        f = File(self)
        f.is_local = True
        f.path = "/"
        f.can_skip = True
        f.mimetype = f.DIRECTORY
        f.resource = ""
        f.name = self.get_name()
        
        return f
          
    
    
    def ls_async(self, path, cb, *args):
    
        if (path == "/"):
            for album in self.__albums:
                f = File(self)
                f.is_local = True
                f.can_skip = True
                f.name = album.name
                f.info = album.info
                f.mimetype = album.mimetype
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

            for trk in album.get_children():
                if (trk.mimetype.startswith("audio")):
                    tags = tagreader.get_tags(trk)
                    title = tags.get("TITLE", trk.name)
                    artist = tags.get("ARTIST", "")
                    album_name = tags.get("ALBUM", "")
                    try:
                        trackno = tags.get("TRACKNUMBER")
                        trackno = trackno.split("/")[0]
                        trackno = int(trackno)
                    except:
                        trackno = 0

                    f = File(self)
                    f.is_local = True
                    f.name = title
                    f.info = artist
                    f.mimetype = trk.mimetype
                    f.thumbnail_md5 = album.thumbnail_md5
                    f.path = trk.path                   
                    f.resource = trk.resource
                    
                    cb(f, *args)
                #end if
            #end for
            
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

