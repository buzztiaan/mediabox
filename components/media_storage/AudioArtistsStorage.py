from com import msgs

from storage import Device, File
from utils import urlquote
from utils import logging
from mediabox import tagreader
import theme

import os
import commands
import gtk
import gobject
import threading



class AudioArtistsStorage(Device):

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_AUDIO
    

    def __init__(self):
    
        self.__artists = {}
        self.__albums = {}
    
        Device.__init__(self)
        
        
    def handle_event(self, msg, *args):
    
        if (msg == msgs.MEDIASCANNER_EV_SCANNING_FINISHED):
            self.__artists = {}
            self.__albums = {}
            #self.__update_media()


    def __update_media(self, finished):

        def f():
            for folder in media:
                self.emit_event(msgs.UI_ACT_SHOW_MESSAGE,
                                "Scanning Folders",
                                "- %s -" % folder.name,
                                theme.mb_device_artists)
                for f in folder.get_children():
                    if (not f.mimetype.startswith("audio/")): continue
                    
                    tags = tagreader.get_tags(f)
                    artist = (tags.get("ARTIST") or "unknown").encode("utf-8")
                    album = (tags.get("ALBUM") or "unknown").encode("utf-8")
                    
                    if (not artist in self.__artists):
                        self.__artists[artist] = []
                    if (not album in self.__artists[artist]):
                        self.__artists[artist].append(album)
                        
                    if (not (artist, album) in self.__albums):
                        self.__albums[(artist, album)] = []
                    self.__albums[(artist, album)].append(f)
                #end for
            #end for
            
            self.emit_event(msgs.UI_ACT_HIDE_MESSAGE)
            finished.set()
          
          
        self.__artists = {}
        self.__albums = {}
        media = self.call_service(msgs.MEDIASCANNER_SVC_GET_MEDIA,
                                  ["audio/"])
        
        #self.call_service(msgs.NOTIFY_SVC_SHOW_INFO,
        #                  "Please wait...\nScanning %d folders" % len(media))
        
        gobject.idle_add(f)
        
        
    def get_prefix(self):
    
        return "library://audio-artists"
        
        
    def get_name(self):
    
        return "Artists"


    def get_icon(self):
    
        return theme.mb_device_artists


    def get_root(self):
    
        f = File(self)
        f.is_local = True
        f.can_skip = True
        f.path = "/"
        f.mimetype = f.DIRECTORY
        f.resource = ""
        f.name = self.get_name()
        
        return f
          
    
    
    def ls_async(self, path, cb, *args):
        
        if (not self.__artists):
            finished = threading.Event()
            self.__update_media(finished)
            while (not finished.isSet()): gtk.main_iteration(False)
        
        if (not path.endswith("/")): path += "/"        
        num_of_slash = len(path) - len(path.replace("/", ""))
        
        if (num_of_slash == 1):
            artists = self.__artists.keys()
            artists.sort()
            for artist in artists:
                f = File(self)
                f.can_skip = True
                f.path = path + urlquote.quote(artist)
                f.name = artist
                f.info = "%d albums" % len(self.__artists[artist])
                f.mimetype = f.DIRECTORY

                cb(f, *args)
            #end for
            
            cb(None, *args)

        elif (num_of_slash == 2):
            artist = urlquote.unquote(path.replace("/", ""))
            albums = self.__artists[artist]
            albums.sort()
            for album in albums:
                f = File(self)
                f.path = path + urlquote.quote(album)
                f.can_skip = True
                f.name = album
                f.info = "%d items" % len(self.__albums[(artist, album)])
                f.mimetype = f.DIRECTORY
                              
                #try:
                #    sample = self.__albums[(artist, album)][0]
                #    f.thumbnail_md5 = sample.thumbnail_md5
                #except:
                #    pass
                
                cb(f, *args)
            #end for
            
            cb(None, *args)
            
        else:
            parts = path.split("/")
            artist = urlquote.unquote(parts[1])
            album = urlquote.unquote(parts[2])

            for f in self.__albums[(artist, album)]:
                tags = tagreader.get_tags(f)
                f.name = tags.get("TITLE") or f.name
                f.info = tags.get("ARTIST") or "unknown"

                cb(f, *args)
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

