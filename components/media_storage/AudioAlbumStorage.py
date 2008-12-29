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
    
        return "By Album"


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
        
        return f
          
    
    
    def ls_async(self, path, cb, *args):

        if (not path.endswith("/")): path += "/"        
        num_of_slash = len(path) - len(path.replace("/", ""))
        
        if (num_of_slash == 1):
            seen = []
            artists = self._list_artists()
            artists.sort()
            for artist in artists:
                albums = self._list_albums(artist)
                albums.sort()
            
                for album, fp in albums:
                    if (album in seen): continue
                    
                    seen.append(album)
                    album_f = self.call_service(msgs.CORE_SVC_GET_FILE, fp)
                    f = File(self)
                    f.is_local = True
                    f.path = path + urlquote.quote(artist + "/" + album)
                    f.can_skip = True
                    f.name = album
                    f.info = artist
                    #f.info = "%d items" % len(self.__albums[(artist, album)])
                    f.mimetype = "application/x-music-folder" #f.DIRECTORY
                    if (album_f):
                        f.resource = album_f.resource
                        #f.thumbnail_md5 = album_f.md5

                    cb(f, *args)
                #end for
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
                al = tags.get("ALBUM")
                
                if (album != al
                    and album != os.path.basename(os.path.dirname(f.resource))):
                    continue
                #if ((artist, album) != (f.info, al)): continue
                
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

