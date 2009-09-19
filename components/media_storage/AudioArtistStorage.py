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
    
    
    _media_was_updated = [False]
    
    __index = MusicIndex()

    def __init__(self):
    

        Device.__init__(self)

        
 
    def handle_message(self, msg, *args):
    
        if (msg == msgs.MEDIASCANNER_EV_SCANNING_FINISHED):
            #self.__index.schedule_scanner(self.__update_media)
            #self.__update_media()
            #self.__index.save()
            self._media_was_updated[0] = True


    def __update_media(self):

        def f():
            # add new files to index
            total_length = len(added)
            cnt = 0
            for folder in added:
                cnt += 1
                percent = int((cnt / float(total_length)) * 100)
                self.emit_message(msgs.UI_ACT_SHOW_MESSAGE,
                                  "Updating Index",
                                  #"- %s -" % folder.name,
                                  "- %d%% complete -" % (percent),
                                  self.get_icon())
                                
                self.__index.remove_album(folder)
                self.__index.add_album(folder)
            #end for
            
            # delete removed files from index
            for folder in removed:
                self.__index.remove_album(folder)
            #end for

            self.emit_message(msgs.UI_ACT_HIDE_MESSAGE)
            #finished.set()
          

        media, added, removed = \
                self.call_service(msgs.MEDIASCANNER_SVC_GET_MEDIA,
                                 [File.DIRECTORY])
        print "ADDED", added
        print "REMOVED", removed
        if (not media):
            self.__index.clear()
        #finished = threading.Event()
        #gobject.idle_add(f)        
        #threads.wait_for(lambda :finished.isSet())
        f()
        
        
    def _check_for_updated_media(self):
    
        if (self._media_was_updated[0]):
            self.__update_media()
            self.__index.save()
            self._media_was_updated[0] = False

        
    def get_index(self):
    
        return self.__index
        
        
    def _list_files(self, artist, album):

        if (album == "All Tracks"):
            albums = self.__index.list_albums_by_artist(artist)
        else:
            albums = [album]
            
        files = []
        for album in albums:
            for path in self.__index.list_files(album):
                f = self.call_service(msgs.CORE_SVC_GET_FILE, path)
                if (f):
                    files.append(f)
            #end for
        #end for

        return files

        
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
        f.info = "Browse your music library by artist"
        
        return f
          
    
    
    def ls_async(self, path, cb, *args):

        self._check_for_updated_media()

        if (not path.endswith("/")): path += "/"
        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)
        index = self.get_index()

        if (len_parts == 0):
            for artist in index.list_artists():
                f = File(self)
                f.path = path + urlquote.quote(artist, "")
                f.name = artist
                f.acoustic_name = f.name
                f.mimetype = f.DIRECTORY
                f.icon = theme.mb_device_artists.get_path()
                f.folder_flags = f.ITEMS_ENQUEUEABLE | \
                                 f.ITEMS_SKIPPABLE

                cb(f, *args)
            #end for
            
            cb(None, *args)

        elif (len_parts == 1):
            artist = urlquote.unquote(parts[0])
            for album in ["All Tracks"] + index.list_albums_by_artist(artist):
                f = File(self)
                f.is_local = True
                f.path = path + urlquote.quote(album, "")
                f.name = album
                f.acoustic_name = f.name
                f.info = artist
                f.mimetype = "application/x-music-folder"
                f.folder_flags = f.ITEMS_ENQUEUEABLE | \
                                 f.ITEMS_SKIPPABLE

                cb(f, *args)
            #end for
            
            cb(None, *args)
            
        elif (len_parts == 2):
            artist = urlquote.unquote(parts[0])
            album = urlquote.unquote(parts[1])

            tracks = []
            for f in self._list_files(artist, album):
                tags = tagreader.get_tags(f)
                f.name = tags.get("TITLE") or f.name
                f.acoustic_name = f.name
                f.info = tags.get("ARTIST") or "unknown"
                al = tags.get("ALBUM") or "unknown"
                
                if (artist != f.info): continue
                
                try:
                    trackno = tags.get("TRACKNUMBER")
                    trackno = trackno.split("/")[0]
                    trackno = int(trackno)
                except:
                    trackno = 0
                    
                # no sorting by track number in the "All Tracks" folder
                if (album != "All Tracks"):
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

