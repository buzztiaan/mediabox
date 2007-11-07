from viewers.Viewer import Viewer
from VideoItem import VideoItem
from VideoThumbnail import VideoThumbnail
from mediabox.MPlayer import MPlayer
from mediabox import caps
from ui import dialogs
import theme

import gtk
import gobject
import os
import time


_VIDEO_EXT = (".avi", ".flv", ".mov", ".mpeg",
              ".mpg", ".rm", ".wmv", ".asf",
              ".m4v")


class VideoViewer(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_video
    PRIORITY = 10
    CAPS = caps.PLAYING | caps.POSITIONING
    IS_EXPERIMENTAL = False

    def __init__(self):
    
        self.__is_fullscreen = False
    
        self.__items = []
        self.__mplayer = MPlayer()    
        self.__mplayer.add_observer(self.__on_observe_mplayer)
        self.__volume = 50

        self.__uri = ""
        self.__context_id = 0

        Viewer.__init__(self)                
        
        box = gtk.VBox()
        
        #frame = gtk.EventBox()
        #frame.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        #frame.show()
        #box.pack_start(frame, True, True, 0)
        
        # video screen        
        self.__screen = gtk.DrawingArea()
        self.__screen.set_double_buffered(False)
        self.__screen.set_sensitive(False)
        self.__screen.show()
        self.__screen.connect("expose-event", self.__on_expose)
        box.pack_start(self.__screen, True, True)
        #frame.add(self.__screen)
        self.set_widget(box) #self.__screen)
        
        
        
    def __on_expose(self, src, ev):
    
        if (not self.__mplayer.is_playing() or not self.__mplayer.has_video()):
            win = self.__screen.window
            gc = win.new_gc()
            gc.set_foreground(gtk.gdk.color_parse("#000000"))
            win.draw_rectangle(gc, True, ev.area.x, ev.area.y,
                               ev.area.width, ev.area.height)



    def __on_observe_mplayer(self, src, cmd, *args):
    
        if (not self.is_active()): return            
            
        if (cmd == src.OBS_STARTED):
            print "Started MPlayer"
            self.update_observer(self.OBS_STATE_PAUSED)
            
        elif (cmd == src.OBS_KILLED):
            print "Killed MPlayer"
            self.set_title("")
            self.update_observer(self.OBS_STATE_PAUSED)
            
        elif (cmd == src.OBS_PLAYING):
            print "Playing"
            self.update_observer(self.OBS_STATE_PLAYING)
            
        elif (cmd == src.OBS_STOPPED):
            print "Stopped"
            self.update_observer(self.OBS_STATE_PAUSED)
            
        elif (cmd == src.OBS_POSITION):
            ctx, pos, total = args
            if (ctx == self.__context_id):
                self.update_observer(self.OBS_POSITION, pos, total)
                if (pos < 0.01): return

        elif (cmd == src.OBS_EOF):
            self.update_observer(self.OBS_STATE_PAUSED)


    def __is_video(self, uri):
        
        ext = os.path.splitext(uri)[1].lower()
        return (ext in _VIDEO_EXT)


    def clear_items(self):
    
        self.__items = []


    def make_item_for(self, uri, thumbnailer):
    
        if (os.path.isdir(uri)): return
        if (not self.__is_video(uri)): return                

        item = VideoItem(uri)        
        if (not thumbnailer.has_thumbnail(uri)):        
            # make video thumbnail
            self.__mplayer.set_window(-1)
            self.__mplayer.set_options("-vf scale=134:-3,screenshot -vo null "
                                       "-nosound -speed 10")
            try:
                self.__mplayer.load(uri)
            except:
                return
        
            # not all videos support seeking, but try it for those that do
            self.__mplayer.seek(20)            
            time.sleep(0.1)
            os.system("rm -f /tmp/shot*.png")
            self.__mplayer.screenshot()
            time.sleep(0.1)
                
            thumbs = [ os.path.join("/tmp", f) for f in os.listdir("/tmp")
                       if f.startswith("shot") ]
            if (not thumbs): return
            thumbs.sort()
            thumb = thumbs[-1]
            
            thumbnailer.set_thumbnail_for_uri(uri, thumb)            
            os.system("rm -f /tmp/shot*.png")
        #end if
        
        tn = VideoThumbnail(thumbnailer.get_thumbnail(uri),
                            os.path.basename(uri))
        item.set_thumbnail(tn)        
        self.__items.append(item)
        


    def load(self, item):
    
        self.update_observer(self.OBS_SHOW_MESSAGE, "Loading...")
    
        def f():
            if (self.__screen.window.xid):
                uri = item.get_uri()
                if (uri == self.__uri): return
                
                self.__mplayer.set_window(self.__screen.window.xid)
                self.__mplayer.set_options("-vo xv")

                try:
                    self.__context_id = self.__mplayer.load(uri)
                    self.__mplayer.set_volume(self.__volume)
                except:
                    return
                    
                self.__mplayer.show_text(os.path.basename(uri), 2000)
                self.set_title(os.path.basename(uri))                
                self.__uri = uri
                
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


    def fullscreen(self):
        
        dialogs.warning("Fullscreen mode not available",
                        "Fullscreen video mode is currently causing problems\n"
                        "and is thus not available in this release.")
        return
        
        self.__is_fullscreen = not self.__is_fullscreen        
        
        self.__screen.hide()
        if (self.__is_fullscreen):
            self.update_observer(self.OBS_FULLSCREEN)
        else:
            self.update_observer(self.OBS_UNFULLSCREEN)
        while (gtk.events_pending()): gtk.main_iteration()
        self.__screen.show()
        #gobject.timeout_add(500, self.__screen.show)
        
