from viewers.Viewer import Viewer
from MusicItem import MusicItem
from AlbumThumbnail import AlbumThumbnail
from ui.KineticScroller import KineticScroller
from ui.ItemList import ItemList
from mediabox.MPlayer import MPlayer
from mediabox.TrackInfo import TrackInfo
from mediabox import caps, config
import theme
import idtags

import gtk
import gobject
import pango
import os


_MUSIC_EXT = (".mp3", ".wav", ".wma", ".ogg",
              ".aac", ".flac", ".m4a")



class AlbumViewer(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_music
    ICON_ACTIVE = theme.viewer_music_active
    PRIORITY = 20
    CAPS = caps.PLAYING | caps.SKIPPING | caps.POSITIONING
    BORDER_WIDTH = 0
    IS_EXPERIMENTAL = False
    

    def __init__(self):
    
        self.__items = []
        self.__is_fullscreen = False
    
        self.__mplayer = MPlayer()
        self.__mplayer.add_observer(self.__on_observe_mplayer)
        self.__volume = 50
                
        self.__tracks = []
        self.__current_index = -1
        self.__current_uri = ""
        
        self.__context_id = 0       
    
        Viewer.__init__(self)
    
        box = gtk.HBox()
        self.set_widget(box)
        
        self.__list = ItemList(600, 80)
        self.__list.set_background(theme.background.subpixbuf(185, 0, 600, 400))
        self.__list.set_graphics(theme.item, theme.item_active)
        self.__list.set_font(theme.font_plain)
        self.__list.set_arrows(theme.arrows)
        self.__list.show()
        self.__kscr = KineticScroller(self.__list)
        self.__kscr.add_observer(self.__on_observe_scroller)
        self.__kscr.show()
        box.pack_start(self.__kscr, True, True, 10)
        
        self.__trackinfo = TrackInfo()
        box.pack_start(self.__trackinfo, True, True, 0)
        


    def __is_album(self, uri):

        files = os.listdir(uri)
        for f in files:
            ext = os.path.splitext(f)[1]
            if (ext.lower() in _MUSIC_EXT):
                return True
        #end for
        
        return False        


    def clear_items(self):
    
        self.__items = []


    def make_item_for(self, uri, thumbnailer):
    
        if (not os.path.isdir(uri)): return
        if (not self.__is_album(uri)): return    

        item = MusicItem(uri)
        if (not thumbnailer.has_thumbnail(uri)):
            candidates = [ os.path.join(uri, ".folder.png"),
                           os.path.join(uri, "cover.jpg"),
                           os.path.join(uri, "cover.jpeg"),
                           os.path.join(uri, "cover.png") ]

            imgs = [ os.path.join(uri, f)
                     for f in os.listdir(uri)
                     if f.lower().endswith(".png") or
                        f.lower().endswith(".jpg") ]

            cover = ""
            for c in candidates + imgs:
                if (os.path.exists(c)):
                    cover = c
                    break
        
            if (cover):
                thumbnailer.set_thumbnail_for_uri(uri, cover)
        #end if
                
        tn = AlbumThumbnail(thumbnailer.get_thumbnail(uri),
                            os.path.basename(uri))
        item.set_thumbnail(tn)
        self.__items.append(item)
       
       
    def __on_observe_mplayer(self, src, cmd, *args):
    
        #if (not self.is_active()): return        
    
        if (cmd == src.OBS_STARTED):
            print "Started MPlayer"
            self.update_observer(self.OBS_STATE_PAUSED)            
            
        elif (cmd == src.OBS_KILLED):
            self.__current_uri = ""
            print "Killed MPlayer"
            self.set_title("")
            self.__list.hilight(-1)
            self.update_observer(self.OBS_STATE_PAUSED)           
            
        elif (cmd == src.OBS_NEW_STREAM_TRACK):
            ctx, title = args
            if (ctx == self.__context_id):
                print "NEW TRACK", title
            
        elif (cmd == src.OBS_PLAYING):
            ctx = args[0]
            if (ctx == self.__context_id):                
                print "Playing"
                self.update_observer(self.OBS_STATE_PLAYING)
            
        elif (cmd == src.OBS_STOPPED):
            ctx = args[0]
            if (ctx == self.__context_id):
                self.__current_uri = ""
                print "Stopped"            
                #self.__next_track()
                self.update_observer(self.OBS_STATE_PAUSED)
            
        elif (cmd == src.OBS_POSITION):
            ctx, pos, total = args
            if (ctx == self.__context_id and self.is_active()):
                #print "%d / %d" % (pos, total)
                self.update_observer(self.OBS_POSITION, pos, total)
            
        elif (cmd == src.OBS_EOF):
            ctx = args[0]
            if (ctx == self.__context_id):
                self.__current_uri = ""        
                print "End of Track"
                self.set_title("")
                self.update_observer(self.OBS_STATE_PAUSED)
                self.__next_track()
       
        
        
    def __on_observe_scroller(self, src, cmd, *args):
    
        if (cmd == src.OBS_CLICKED):                       
            x, y = args
            if (x > 520):
                idx = self.__list.get_index_at(y)
                self.__play_track(idx)
        
        
    def __find_cover(self, uri):
    
        path = os.path.dirname(uri)
        for i in (".folder.png", "cover.jpg", "cover.jpeg", "cover.png"):
            coverpath = os.path.join(path, i)
            if (os.path.exists(coverpath)): return coverpath
            
        return None
        

    def __previous_track(self):
        """
        Jumps to the previous track.
        """
        
        self.__stop_current_track()
        if (self.__current_index > 0):
            self.__play_track(self.__current_index - 1)
        else:
            self.__play_track(self.__current_index)
            
                    
    def __next_track(self):
        """
        Advances to the next track.
        """
        
        self.__stop_current_track()
        if (self.__current_index + 1 < len(self.__tracks)):
            self.__play_track(self.__current_index + 1)

        
        
        
    def __play_track(self, idx):
    
        self.__mplayer.set_window(-1)
        self.__mplayer.set_options("")
        self.__list.hilight(idx)            
            
        def f():    
            track = self.__tracks[idx]
            try:
                self.__context_id = self.__mplayer.load(track)            
                self.__current_uri = track
                self.__current_index = idx
                self.__mplayer.set_volume(self.__volume)

                tags = idtags.read(track)
                title = tags.get("TITLE", os.path.basename(track))
                album = tags.get("ALBUM", os.path.basename(track))
                artist = tags.get("ARTIST", os.path.basename(track))
                self.__list.hilight(idx)
                self.set_title(title)
                self.__trackinfo.set_title(title)
                self.__trackinfo.set_info(album, artist)
                self.__trackinfo.set_cover(self.__find_cover(track))
                
            except:
                self.__list.hilight(-1)
        gobject.idle_add(f)
        

    def __stop_current_track(self):
    
        self.__list.hilight(-1)          
         
         
    def shutdown(self):

        self.__mplayer.close()
        
        
    def load(self, item):
        """
        Loads the given album.
        """

        self.update_observer(self.OBS_SHOW_MESSAGE, "Loading...")

        def f():             
            uri = item.get_uri()
        
            self.__tracks = []
            self.__list.clear_items()
            self.__current_index = -1
        
            files = os.listdir(uri)
            files.sort()
            for f in files:
                filepath = os.path.join(uri, f)
                ext = os.path.splitext(f)[-1].lower()

                if (ext in _MUSIC_EXT):
                    tags = idtags.read(filepath)
                    title = tags.get("TITLE", f)
                    artist = tags.get("ARTIST", "")

                    if (artist):
                        title = "%s\n[%s]" % (title, artist)
                    
                    self.__tracks.append(filepath)
                    idx = self.__list.append_item(title, None)
                    self.__list.overlay_image(idx, theme.btn_load, 540, 24)
                #end if
            #end for

            if (self.__current_uri in self.__tracks):
                idx = self.__tracks.index(self.__current_uri)
                self.__list.hilight(idx)
            
            self.update_observer(self.OBS_SHOW_PANEL)

        gobject.idle_add(f)

        
    def increment(self):
    
        if (self.__volume + 5 <= 100):
            self.__volume += 5
        self.__mplayer.set_volume(self.__volume)
        self.update_observer(self.OBS_VOLUME, self.__volume)
        
        
    def decrement(self):

        if (self.__volume - 5 >= 0):
            self.__volume -= 5
        self.__mplayer.set_volume(self.__volume)
        self.update_observer(self.OBS_VOLUME, self.__volume)        
        
    
    def set_position(self, pos):
    
        self.__mplayer.seek_percent(pos)


    def play_pause(self):
    
        self.__mplayer.pause()

    
    def previous(self):
        
        self.__previous_track()

        
    def next(self):
    
        self.__next_track()
        

    def show(self):
    
        Viewer.show(self)
        self.update_observer(self.OBS_SET_COLLECTION, self.__items)


    def fullscreen(self):
    
        self.__is_fullscreen = not self.__is_fullscreen
        
        if (self.__is_fullscreen):
            self.__kscr.hide()
            self.__trackinfo.show()
            self.update_observer(self.OBS_HIDE_COLLECTION)
        else:
            self.__trackinfo.hide()
            self.__kscr.show()
            self.update_observer(self.OBS_SHOW_COLLECTION)            

