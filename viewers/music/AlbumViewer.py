from viewers.Viewer import Viewer
from MusicItem import MusicItem
from AlbumThumbnail import AlbumThumbnail
from ui.KineticScroller import KineticScroller
from ui.ImageStrip import ImageStrip
from mediabox.MPlayer import MPlayer
from mediabox import caps
import theme
#import mutagen
#from utils.ID3 import ID3
#from utils import id3reader
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
    PRIORITY = 20
    CAPS = caps.PLAYING | caps.POSITIONING
    BORDER_WIDTH = 0
    IS_EXPERIMENTAL = False
    

    def __init__(self):
    
        self.__items = []
    
        self.__mplayer = MPlayer()
        self.__mplayer.add_observer(self.__on_observe_mplayer)
        self.__volume = 50
                
        self.__tracks = []        
        self.__list_items = []
        self.__playing_items = []
        self.__current_index = -1
        self.__current_uri = ""
        
        self.__context_id = 0
        
        self.__render_pixmap = gtk.gdk.Pixmap(None, 600, 80,
                                  gtk.gdk.get_default_root_window().get_depth())
        self.__item_pbuf = theme.item
        self.__item_act_pbuf = theme.item_active
    
        Viewer.__init__(self)
    
        box = gtk.HBox()
        self.set_widget(box)
        
        self.__strip = ImageStrip(600, 80, 10)
        self.__strip.set_selection_offset(0)
        self.__strip.set_wrap_around(False)
        self.__strip.set_background(theme.background.subpixbuf(185, 0, 600, 400))
        self.__strip.show()
        kscr = KineticScroller(self.__strip)
        kscr.add_observer(self.__on_observe_scroller)
        kscr.show()
        box.pack_start(kscr, True, True, 10)


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

            cover = ""
            for c in candidates:
                if (os.path.exists(c)):
                    cover = c
                    break
        
            if (cover):
                thumbnailer.set_thumbnail_for_uri(uri, cover)
        #end if
                
        tn = AlbumThumbnail(thumbnailer.get_thumbnail(uri),
                            os.path.basename(uri))
        item.set_thumbnail(tn)
        
        #    tn = AlbumThumbnail(cover)
        #    thumbnailer.set_thumbnail(item, tn)
        #    del tn
        #    import gc; gc.collect()
        #else:
        #    thumbnailer.load_thumbnail(item)
            
        self.__items.append(item)
       
       
    def __on_observe_mplayer(self, src, cmd, *args):
    
        #if (not self.is_active()): return        
    
        if (cmd == src.OBS_STARTED):
            print "Started MPlayer"
            
        elif (cmd == src.OBS_KILLED):
            self.__current_uri = ""
            print "Killed MPlayer"
            self.set_title("")            
            
        elif (cmd == src.OBS_PLAYING):
            print "Playing"
            
        elif (cmd == src.OBS_STOPPED):
            self.__current_uri = ""
            print "Stopped"
            #self.__next_track()
            
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
                self.__next_track()
       
        
        
    def __on_observe_scroller(self, src, cmd, *args):
    
        if (cmd == src.OBS_CLICKED):                       
            x, y = args
            if (x > 400):
                idx = self.__strip.get_index_at(y)
                self.__play_track(idx)
              

            
            
            
    def __create_item(self, idx, title, is_playing):

        pc = self.get_widget().get_pango_context()
        layout = pango.Layout(pc)
        layout.set_font_description(theme.font_plain)
        layout.set_text(`idx` + " - " + title)
        layout.set_width(580 * pango.SCALE)        
            
        pmap = self.__render_pixmap
        cmap = self.get_widget().get_colormap()
        gc = pmap.new_gc()

        if (is_playing):
            fgcolor = "#444466"
            bgcolor = "#ffffff"
            pmap.draw_pixbuf(gc, self.__item_act_pbuf, 0, 0, 0, 0, 600, 80)
        else:
            fgcolor = "#444466"
            bgcolor = "#aaaacc"
            pmap.draw_pixbuf(gc, self.__item_pbuf, 0, 0, 0, 0, 600, 80)
            
        #pmap.draw_pixbuf(gc, self.__item_pbuf, 0, 0, 0, 0, 600, 80)
        
        #gc.set_foreground(cmap.alloc_color(bgcolor))
        #pmap.draw_rectangle(gc, True, 0, 0, 600, 80)
        
        #gc.set_foreground(cmap.alloc_color("#222244"))
        #pmap.draw_rectangle(gc, False, 0, 0, 599, 79)
        
            
        gc.set_foreground(theme.item_foreground)
        pmap.draw_layout(gc, 8, 16, layout)

        pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 600, 80)
        pbuf.get_from_drawable(pmap, cmap, 0, 0, 0, 0, 600, 80)
    
        return pbuf
        
        
        
    def __hilight(self, idx):
    
        if (self.__current_index >= 0):
            self.__strip.replace_image(self.__current_index,
                                       self.__list_items[self.__current_index])
        if (idx >= 0):                                 
            self.__strip.replace_image(idx, self.__playing_items[idx])
            self.__current_index = idx
        
        
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
    
        self.__hilight(idx)
        
        def f():    
            track = self.__tracks[idx]
            try:
                self.__context_id = self.__mplayer.load(track)            
                self.__current_uri = track
                self.__mplayer.set_volume(self.__volume)

                tags = idtags.read(track)
                title = tags.get("TITLE", os.path.basename(track))
                self.set_title(title)
                
            except:
                self.__hilight(-1)
        gobject.idle_add(f)
        
    def __stop_current_track(self):
    
        self.__hilight(-1)          
            
        
        
    def load(self, item):
        """
        Loads the given album.
        """

        self.update_observer(self.OBS_SHOW_MESSAGE, "Loading...")

        def f():        
            #self.__strip.push_out()                
            uri = item.get_uri()
        
            self.__tracks = []
            self.__list_items = []
            self.__playing_items = []
            self.__current_index = -1
        
            files = os.listdir(uri)
            files.sort()
            idx = 1
            for f in files:
                filepath = os.path.join(uri, f)
                ext = os.path.splitext(f)[-1].lower()
                if (ext in _MUSIC_EXT):
                    #id3 = ID3(filepath)
                    #print id3.items()
                    #title = id3.get("TITLE", "f[:-len(ext)]")
                    #artist = id3.get("ARTIST", "")
                    
                    #id3 = id3reader.Reader(filepath)
                    #id3.dump()
                    #title = id3.getValue("title") or "..."
                    #artist = id3.getValue("artist") or ""
                    
                    #tags = mutagen.File(filepath)
                    #print tags
                    #title = tags.get("TITLE")[0]
                    #if (not title): title = tags.get("TIT2")[0]
                    #if (not title): title = "..."
                    #title = tags.get("TITLE", ["f[:-len(ext)]"])[0]
                    #artist = tags.get("ARTIST", [""])[0]
                    
                    tags = idtags.read(filepath)
                    title = tags.get("TITLE", f)
                    artist = tags.get("ARTIST", "")
                    
                    #title = f
                    self.__tracks.append(filepath)
                    #if (artist): title += " - " + artist
                    self.__list_items.append(self.__create_item(idx, title, False))
                    self.__playing_items.append(self.__create_item(idx, title, True))
                    idx += 1
            #end for

            self.__strip.set_images(self.__list_items)
            
            if (self.__current_uri in self.__tracks):
                idx = self.__tracks.index(self.__current_uri)
                self.__hilight(idx)
            
            import gc; gc.collect()
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
        

    def show(self):
    
        Viewer.show(self)
        self.update_observer(self.OBS_SET_COLLECTION, self.__items)        

