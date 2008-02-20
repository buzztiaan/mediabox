from viewers.Viewer import Viewer
from VideoThumbnail import VideoThumbnail
from mediaplayer.MPlayer import MPlayer
import mediaplayer
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
        self.__player = mediaplayer.get_player_for_uri("")
        mediaplayer.add_observer(self.__on_observe_player)
        self.__volume = 50

        self.__uri = ""
        self.__context_id = 0
        self.__aspect_ratio = 1.0


        Viewer.__init__(self, esens)                
      
        # video screen        
        self.__screen = gtk.DrawingArea()
        self.__screen.set_double_buffered(False)
        self.__screen.connect("expose-event", self.__on_expose)
        self.__screen.set_events(gtk.gdk.BUTTON_PRESS_MASK |
                                 gtk.gdk.KEY_PRESS_MASK)
        self.__layout.put(self.__screen, 0, 0)
        
        #self.connect(self.EVENT_BUTTON_PRESS, self.__on_drag_start)
        
         
        
    def render_this(self):
            
        vx, vy, vw, vh = self.__get_video_rect()
        screen = self.get_screen()

        screen.fill_area(vx, vy, vw, vh, "#000000")        

        if (not self.__is_fullscreen):
            x, y, w, h = self.__get_frame_rect()
            screen.draw_rect(x, y, w, h, "#000000")
    
        if (not self.__player or not self.__player.has_video()):
            self.__layout.move(self.__screen, vx, vy)
            self.__screen.set_size_request(vw, vh)
            


    def __on_expose(self, src, ev):
    
        if (self.__player.has_video()):
            win = self.__screen.window
            gc = win.new_gc()
            cmap = win.get_colormap()
            gc.set_foreground(cmap.alloc_color("#000000"))
            x, y, w, h = ev.area
            self.__player.handle_expose(win, gc, x, y, w, h)

            
            
    def __on_drag_start(self, px, py):
    
        print "CLICKED"
        x, y = self.get_screen_pos()
        w, h = self.get_size()

        pos = px - x
        self.update_observer(self.OBS_POSITION, pos, w)
        



    def __on_observe_player(self, src, cmd, *args):
    
        if (not self.is_active()): return            
            
        if (cmd == src.OBS_STARTED):
            print "Started Player"
            self.update_observer(self.OBS_STATE_PAUSED)
            
        elif (cmd == src.OBS_KILLED):
            print "Killed Player"
            self.__uri = ""
            self.set_title("")
            self.__screen.hide()
            self.update_observer(self.OBS_STATE_PAUSED)

        elif (cmd == src.OBS_ERROR):
            ctx, err = args
            if (ctx == self.__context_id):
                self.__show_error(err)
                self.set_title("")                
                self.__screen.hide()
            
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

                # unfullscreen
                if (self.__is_fullscreen): self.do_fullscreen()
                
                self.update_observer(self.OBS_STATE_PAUSED)
           
        elif (cmd == src.OBS_ASPECT):
            ctx, ratio = args            
            self.__aspect_ratio = ratio
            self.__set_aspect_ratio(ratio)
            self.__screen.show()


    def __show_error(self, errcode):
    
        if (errcode == self.__player.ERR_INVALID):
            dialogs.error("Invalid Stream", "Cannot load this stream.")
        elif (errcode == self.__player.ERR_NOT_FOUND):
            dialogs.error("Not found", "Cannot find a stream to play.")
        elif (errcode == self.__player.ERR_CONNECTION_TIMEOUT):
            dialogs.error("Timeout", "Connection timed out.")       
        elif (errcode == self.__player.ERR_NOT_SUPPORTED):
            dialogs.error("Not supported", "The media format is not supported.")


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
        print  x + (w - w2) / 2, y + (h - h2) / 2, w2, h2
        
        while (gtk.events_pending()): gtk.main_iteration()


    def __scale_video(self):
        """
        Scales the video to fill the available space while retaining the
        original aspect ratio.
        """
            
        self.__set_aspect_ratio(self.__aspect_ratio)
        self.__player.set_window(self.__screen.window.xid)


    def clear_items(self):
    
        self.__items = []


    def update_media(self, mscanner):
    
        self.__items = []
        for item in mscanner.get_media(mscanner.MEDIA_VIDEO):
            if (not item.thumbnail_pmap):
                tn = VideoThumbnail(item.thumbnail, item.name)
                item.thumbnail_pmap = tn
            self.__items.append(item)
           

    def shutdown(self):

        # the music viewer already closes the player for us
        #mediaplayer.close()
        pass
        

    def load(self, item):

        self.update_observer(self.OBS_STOP_PLAYING, self)
        
        self.update_observer(self.OBS_SHOW_MESSAGE, "Loading...")
        self.__screen.show()
    
        def f():
            if (self.__screen.window.xid):
                uri = item.uri
                if (uri == self.__uri): return
                
                self.__player = mediaplayer.get_player_for_uri(uri)
                self.__player.set_window(self.__screen.window.xid)
                if (_IS_MAEMO):
                    self.__player.set_options("-vo xv")
                    # the Nokia 770 would require something like this, instead
                    #self.__player.set_options("-ao gst -ac dspmp3 "
                    #                      "-vo xv,nokia770:fb_overlay_only:"
                    #                      "x=%d:y=%d:w=%d:h=%d" % (x, y, w, h))
                else:
                    self.__player.set_options("-vo xv")
                    
                try:
                    self.__context_id = self.__player.load_video(uri)
                except:
                    import traceback; traceback.print_exc()
                    self.__screen.hide()
                    return
                                
                self.__player.set_volume(self.__volume)
                self.__player.show_text(os.path.basename(uri), 2000)
                self.set_title(os.path.basename(uri))                
                self.__uri = uri
                
                self.update_observer(self.OBS_SHOW_PANEL)
                
        gobject.idle_add(f)


    def do_enter(self):
    
        self.__player.pause()
                        

    def do_increment(self):
    
        if (self.__volume + 5 <= 100):
            self.__volume += 5
        self.__player.set_volume(self.__volume)
        self.update_observer(self.OBS_VOLUME, self.__volume)

        if (self.__is_fullscreen):
            self.__player.show_text("Volume %d %%" % self.__volume, 500)
        
        
    def do_decrement(self):

        if (self.__volume - 5 >= 0):
            self.__volume -= 5
        self.__player.set_volume(self.__volume)
        self.update_observer(self.OBS_VOLUME, self.__volume)        

        if (self.__is_fullscreen):
            self.__player.show_text("Volume %d %%" % self.__volume, 500)

        
    def do_set_position(self, pos):
    
        self.__player.seek_percent(pos)


    def do_play_pause(self):
    
        self.__player.pause()



    def stop_playing(self, issued_by):
    
        if (issued_by != self):
            self.__player.stop()


    def show(self):
    
        Viewer.show(self)
        self.update_observer(self.OBS_SET_COLLECTION, self.__items)
        if (self.__player and self.__player.has_video()):
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
        else:
            self.update_observer(self.OBS_UNFULLSCREEN)
        
        #while (gtk.events_pending()): gtk.main_iteration()        
        
        self.update_observer(self.OBS_RENDER)

        if (self.__player.has_video()):
            self.__scale_video()
            self.__screen.show()

