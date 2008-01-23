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


try:
    import hildon
    _IS_MAEMO = True
except:
    _IS_MAEMO = False


_VIDEO_EXT = (".avi", ".flv", ".mov", ".mpeg",
              ".mpg", ".rm", ".wmv", ".asf",
              ".m4v", ".mp4", ".rmvb")


class VideoViewer(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_video
    ICON_ACTIVE = theme.viewer_video_active
    PRIORITY = 10
    CAPS = caps.PLAYING | caps.POSITIONING


    def __init__(self, esens):
    
        self.__layout = esens
        self.__is_fullscreen = False
    
        self.__items = []
        self.__mplayer = MPlayer()    
        self.__mplayer.add_observer(self.__on_observe_mplayer)
        self.__volume = 50

        self.__uri = ""
        self.__context_id = 0
        self.__aspect_ratio = 1.0


        Viewer.__init__(self, esens)                
      
        # video screen        
        self.__screen = gtk.DrawingArea()
        self.__screen.set_double_buffered(False)
        #self.__screen.set_sensitive(False)
        self.__screen.connect("expose-event", self.__on_expose)
        self.__layout.put(self.__screen, 0, 0)
        
        
    def render_this(self):
            
        vx, vy, vw, vh = self.__get_video_rect()
        screen = self.get_screen()

        screen.fill_area(vx, vy, vw, vh, "#000000")        

        if (not self.__is_fullscreen):
            x, y, w, h = self.__get_frame_rect()
            screen.draw_rect(x, y, w, h, "#000000")
    
        if (not self.__mplayer.has_video()):
            self.__layout.move(self.__screen, vx, vy)
            self.__screen.set_size_request(vw, vh)
            


    def __on_expose(self, src, ev):
    
        if (self.__mplayer.has_video()):
            win = self.__screen.window
            gc = win.new_gc()
            cmap = win.get_colormap()
            gc.set_foreground(cmap.alloc_color("#000000"))
            nil, nil, w, h = src.get_allocation()

            # mplayer has a bug where it doesn't draw over the right and
            # bottom edges, so we have to do this ourselves
            win.draw_rectangle(gc, False, w - 1, 0, 1, h)
            win.draw_rectangle(gc, False, 0, h - 1, w, 1)
            



    def __on_observe_mplayer(self, src, cmd, *args):
    
        if (not self.is_active()): return            
            
        if (cmd == src.OBS_STARTED):
            print "Started MPlayer"
            self.update_observer(self.OBS_STATE_PAUSED)
            
        elif (cmd == src.OBS_KILLED):
            print "Killed MPlayer"
            self.__uri = ""
            self.set_title("")
            self.__screen.hide()
            self.update_observer(self.OBS_STATE_PAUSED)
            
        elif (cmd == src.OBS_PLAYING):
            ctx = args[0]
            if (ctx == self.__context_id):
                print "Playing"
                self.update_observer(self.OBS_STATE_PLAYING)
            
        elif (cmd == src.OBS_STOPPED):
            ctx = args[0]
            if (ctx == self.__context_id):
                print "Stopped"
                self.update_observer(self.OBS_STATE_PAUSED)
            
        elif (cmd == src.OBS_POSITION):
            ctx, pos, total = args            
            if (not self.__is_fullscreen and ctx == self.__context_id):
                self.update_observer(self.OBS_POSITION, pos, total)

        elif (cmd == src.OBS_EOF):
            ctx = args[0]
            if (ctx == self.__context_id):        
                self.__uri = ""
                self.__screen.hide()
                self.update_observer(self.OBS_STATE_PAUSED)
           
        elif (cmd == src.OBS_ASPECT):
            ctx, ratio = args            
            self.__aspect_ratio = ratio
            self.__set_aspect_ratio(ratio)
            self.__screen.show()


    def __get_frame_rect(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        x += 4; y += 4
        w -= 8; h -= 8
        return (x, y, w, h)
            
            
    def __get_video_rect(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        if (not self.__is_fullscreen):
            x += 6; y += 6
            w -= 12; h -= 12
        return (x, y, w, h)
            
            
    def __set_aspect_ratio(self, ratio):
        """
        Sets the aspect ratio of the screen to the given value.
        """
    
        if (ratio == 0): return
        
        #self.__screen.hide()
        x, y, w, h = self.__get_video_rect()
        w2 = int(ratio * h)
        h2 = int(w / ratio)
         
        #print ratio, w, h, w2, h2
        if (w2 > w):
            self.__screen.set_size_request(w, h2)
            w2, h2 = w, h2
        else:
            self.__screen.set_size_request(w2, h)
            w2, h2 = w2, h
        self.__layout.move(self.__screen, x + (w - w2) / 2, y + (h - h2) / 2)

        while (gtk.events_pending()): gtk.main_iteration()


    def __scale_video(self):
        """
        Scales the video to fill the available space while retaining the
        original aspect ratio.
        """
            
        self.__set_aspect_ratio(self.__aspect_ratio)



    def __is_video(self, uri):
        
        ext = os.path.splitext(uri)[1].lower()
        return (ext in _VIDEO_EXT)


    def clear_items(self):
    
        self.__items = []


    def update_media(self, mscanner):
    
        self.__items = []
        for item in mscanner.get_media(mscanner.MEDIA_VIDEO):
            vitem = VideoItem(item.uri)
            tn = VideoThumbnail(item.thumbnail,
                                os.path.basename(item.uri))
            vitem.set_thumbnail(tn)
            self.__items.append(vitem)
           

    def shutdown(self):

        # the music viewer already closes mplayer for us
        #self.__mplayer.close()
        pass
        

    def load(self, item):
    
        self.update_observer(self.OBS_SHOW_MESSAGE, "Loading...")
        self.__screen.show()
    
        def f():
            if (self.__screen.window.xid):
                uri = item.get_uri()
                if (uri == self.__uri): return
                
                self.__mplayer.set_window(self.__screen.window.xid)
                if (_IS_MAEMO):
                    self.__mplayer.set_options("-vo xv")
                    # the Nokia 770 would require something like this, instead
                    #self.__mplayer.set_options("-ao gst -ac dspmp3 "
                    #                      "-vo xv,nokia770:fb_overlay_only:"
                    #                      "x=%d:y=%d:w=%d:h=%d" % (x, y, w, h))
                else:
                    self.__mplayer.set_options("-vo xv")
                    
                try:
                    self.__context_id = self.__mplayer.load(uri)
                except:
                    self.__screen.hide()
                    return
                                
                #self.__scale_video()
                self.__mplayer.set_volume(self.__volume)
                self.__mplayer.show_text(os.path.basename(uri), 2000)
                self.set_title(os.path.basename(uri))                
                self.__uri = uri
                
                self.update_observer(self.OBS_SHOW_PANEL)
                
        gobject.idle_add(f)


    def do_enter(self):
    
        self.__mplayer.pause()
                        

    def do_increment(self):
    
        if (self.__volume + 5 <= 100):
            self.__volume += 5
        self.__mplayer.set_volume(self.__volume)
        self.update_observer(self.OBS_VOLUME, self.__volume)

        if (self.__is_fullscreen):
            self.__mplayer.show_text("Volume %d %%" % self.__volume, 500)
        
        
    def do_decrement(self):

        if (self.__volume - 5 >= 0):
            self.__volume -= 5
        self.__mplayer.set_volume(self.__volume)
        self.update_observer(self.OBS_VOLUME, self.__volume)        

        if (self.__is_fullscreen):
            self.__mplayer.show_text("Volume %d %%" % self.__volume, 500)

        
    def do_set_position(self, pos):
    
        self.__mplayer.seek_percent(pos)


    def do_play_pause(self):
    
        self.__mplayer.pause()


    def show(self):
    
        Viewer.show(self)
        self.update_observer(self.OBS_SET_COLLECTION, self.__items)
        if (self.__mplayer.has_video()):
            self.__scale_video()
            self.__screen.show()
        
        
    def hide(self):
    
        Viewer.hide(self)
        self.__screen.hide()


    def do_fullscreen(self):
        
        self.__is_fullscreen = not self.__is_fullscreen        
        
        self.__screen.hide()
        while (gtk.events_pending()): gtk.main_iteration()
        
        if (self.__is_fullscreen):
            self.update_observer(self.OBS_FULLSCREEN)
            # what a hack! but it works and it allows to unfullscreen mplayer!
            gtk.gdk.keyboard_grab(self.__screen.get_toplevel().window)
        else:
            self.update_observer(self.OBS_UNFULLSCREEN)
            gtk.gdk.keyboard_ungrab()
        
        #while (gtk.events_pending()): gtk.main_iteration()        
        
        self.update_observer(self.OBS_RENDER)

        if (self.__mplayer.has_video()):
            self.__scale_video()
            self.__screen.show()

