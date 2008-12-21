from com import msgs
from MusicIndex import MusicIndex
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

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_AUDIO
    

    def __init__(self):
    
        self.__index = MusicIndex()


        Device.__init__(self)

        
 
    def handle_event(self, msg, *args):
    
        if (msg == msgs.MEDIASCANNER_EV_SCANNING_FINISHED):
            self.__index.schedule_scanner(self.__update_media)


    def __update_media(self):

        def f():
            # add new files to index
            total_length = len(added)
            cnt = 0
            for folder in added:
                cnt += 1
                percent = int((cnt / float(total_length)) * 100)
                self.emit_event(msgs.UI_ACT_SHOW_MESSAGE,
                                "Updating Index",
                                #"- %s -" % folder.name,
                                "- %d%% complete -" % (percent),
                                self.get_icon())
                                
                self.__index.add_album(folder)
            #end for
            
            # delete removed files from index
            for folder in removed:
                self.__index.remove_album(folder)
            #end for

            self.emit_event(msgs.UI_ACT_HIDE_MESSAGE)
            #finished.set()
          

        media, added, removed = \
                self.call_service(msgs.MEDIASCANNER_SVC_GET_MEDIA,
                                 [File.DIRECTORY])

        #finished = threading.Event()
        #gobject.idle_add(f)        
        #threads.wait_for(lambda :finished.isSet())
        f()
        
        
    def _list_artists(self):
    
        return self.__index.list_artists()  


    def _list_albums(self, artist):
    
        return self.__index.list_albums(artist)  
        

    def _list_files(self, artist, album):

        album_fp = self.__index.get_album(artist, album)
        f = self.call_service(msgs.CORE_SVC_GET_FILE, album_fp)

        if (f):
            files = [ c for c in f.get_children()
                      if c.mimetype.startswith("audio/") ]
            return files
        else:
            return []

        
    def get_prefix(self):
    
        return "library://audio-artists"
        
        
    def get_name(self):
    
        return "By Artist"


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

        if (not path.endswith("/")): path += "/"        
        num_of_slash = len(path) - len(path.replace("/", ""))
        
        if (num_of_slash == 1):        
            artists = self._list_artists()
            artists.sort()
            for artist in artists:
                f = File(self)
                f.can_skip = True
                f.path = path + urlquote.quote(artist)
                f.name = artist
                #f.info = "%d albums" % len(self.__artists[artist])
                f.mimetype = f.DIRECTORY

                cb(f, *args)
            #end for
            
            cb(None, *args)

        elif (num_of_slash == 2):
            artist = urlquote.unquote(path.replace("/", ""))
            albums = self._list_albums(artist)
            albums.sort()
            for album, fp in albums:
                album_f = self.call_service(msgs.CORE_SVC_GET_FILE, fp)
                f = File(self)
                f.is_local = True
                f.path = path + urlquote.quote(album)
                f.can_skip = True
                f.name = album
                f.info = artist
                #f.info = "%d items" % len(self.__albums[(artist, album)])
                f.mimetype = "application/x-music-folder" #f.DIRECTORY
                if (album_f):
                    f.resource = album_f.resource
                    f.thumbnail_md5 = album_f.md5

                cb(f, *args)
            #end for
            
            cb(None, *args)
            
        else:
            parts = path.split("/")
            artist = urlquote.unquote(parts[1])
            album = urlquote.unquote(parts[2])

            tracks = []
            for f in self._list_files(artist, album):
                tags = tagreader.get_tags(f)
                f.name = tags.get("TITLE") or f.name
                f.info = tags.get("ARTIST") or "unknown"
                al = tags.get("ALBUM") or "unknown"
                
                print (artist, album), (f.info, al)
                if (artist != f.info): continue
                
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

