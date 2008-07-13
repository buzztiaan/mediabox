from mediabox.MediaWidget import MediaWidget
from ui.EventBox import EventBox
from ui.ImageButton import ImageButton
from ui.ProgressBar import ProgressBar
import mediaplayer
from utils import maemo
import theme

import gtk
import gobject


class VideoWidget(MediaWidget):
    """
    Media widget for viewing videos.
    """


    def __init__(self):
    
        self.__player = mediaplayer.get_player_for_uri("")
        mediaplayer.add_observer(self.__on_observe_player)
        self.__volume = 50
        self.__aspect_ratio = 1.0

        self.__uri = ""
        self.__context_id = 0

        MediaWidget.__init__(self)
        self.__layout = self.get_window()
      
        # video screen
        self.__screen = gtk.DrawingArea()
        self.__screen.set_double_buffered(False)
        self.__screen.connect("expose-event", self.__on_expose)
        self.__screen.set_events(gtk.gdk.BUTTON_PRESS_MASK |
                                 gtk.gdk.KEY_PRESS_MASK)
        self.__layout.put(self.__screen, 0, 0)
        
        self.__ebox = EventBox()
        self.add(self.__ebox)
        self.__ebox.connect_button_pressed(self.__on_click)


        # controls
        self.__btn_play = ImageButton(theme.btn_play_1,
                                      theme.btn_play_2)
        self.__btn_play.connect_clicked(self.__on_play_pause)

        self.__progress = ProgressBar()
        self.__progress.connect_changed(self.__on_set_position)
        
        self._set_controls(self.__btn_play, self.__progress)


    def render_this(self):

        while (gtk.events_pending()): gtk.main_iteration()
            
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()    

        self.__ebox.set_geometry(0, 0, w, h)

        fx, fy, fw, fh = x, y, w, h
        vx, vy, vw, vh = x + 2, y + 2, w - 4, h - 4

        if (w < 800):
            screen.draw_rect(fx, fy, fw, fh, "#000000")
            screen.fill_area(vx, vy, vw, vh, "#000000")
            self.__layout.move(self.__screen, vx, vy  + 10)
            self.__screen.set_size_request(vw, vh - 20)
        else:
            screen.fill_area(x, y, w, h, "#000000")
            self.__layout.move(self.__screen, x, y)
            self.__screen.set_size_request(w, h)

        if (self.__player.has_video()):
            self.__scale_video()            
            self.__screen.show()


    def set_frozen(self, value):
    
        MediaWidget.set_frozen(self, value)
        if (not value and self.may_render() and self.__player.has_video()):
            self.__screen.show()
        else:
            self.__screen.hide()


    def set_visible(self, value):
        
        MediaWidget.set_visible(self, value)    
        if (value):
            pass
        else:
            self.__screen.hide()

        
    def __on_expose(self, src, ev):
    
        if (self.__player.has_video()):
            win = self.__screen.window
            gc = win.new_gc()
            cmap = win.get_colormap()
            gc.set_foreground(cmap.alloc_color("#000000"))
            x, y, w, h = ev.area
            self.__player.handle_expose(win, gc, x, y, w, h)

            
            
    def __on_click(self, px, py):
            
        self.send_event(self.EVENT_FULLSCREEN_TOGGLED)



    def __on_observe_player(self, src, cmd, *args):
           
        if (cmd == src.OBS_POSITION):
            ctx, pos, total = args
            if (ctx == self.__context_id):
                pos_m = pos / 60
                pos_s = pos % 60
                total_m = total / 60
                total_s = total % 60
                info = "%d:%02d / %d:%02d" % (pos_m, pos_s, total_m, total_s)

                self.send_event(self.EVENT_MEDIA_POSITION, info)
                self.__progress.set_position(pos, total)

        elif (cmd == src.OBS_STARTED):
            print "Started Player"
            self.__btn_play.set_images(theme.btn_play_1,
                                       theme.btn_play_2)
            
        elif (cmd == src.OBS_KILLED):
            print "Killed Player"
            self.__uri = ""
            #self.set_title("")
            self.__screen.hide()
            self.__btn_play.set_images(theme.btn_play_1,
                                       theme.btn_play_2)

        elif (cmd == src.OBS_ERROR):
            ctx, err = args
            if (ctx == self.__context_id):
                #self.__show_error(err)
                #self.set_title("")
                self.__screen.hide()
            
        elif (cmd == src.OBS_PLAYING):
            ctx = args[0]
            if (ctx == self.__context_id):
                print "Playing"
                self.__btn_play.set_images(theme.btn_pause_1,
                                           theme.btn_pause_2)                
            
        elif (cmd == src.OBS_STOPPED):
            ctx = args[0]
            if (ctx == self.__context_id):
                print "Stopped"
                self.__btn_play.set_images(theme.btn_play_1,
                                           theme.btn_play_2)
            
        elif (cmd == src.OBS_EOF):
            ctx = args[0]
            if (ctx == self.__context_id):        
                self.__uri = ""
                self.__screen.hide()

                # unfullscreen
                #if (self.__is_fullscreen): self.__on_fullscreen()
                
                self.__btn_play.set_images(theme.btn_play_1,
                                           theme.btn_play_2)                

        elif (cmd == src.OBS_ASPECT):
            ctx, ratio = args
            self.__aspect_ratio = ratio
            self.__set_aspect_ratio(ratio)


    def __on_set_position(self, pos):
    
        self.__player.seek_percent(pos)


    def __on_play_pause(self):
    
        self.__player.pause()


    def __scale_video(self):
        """
        Scales the video to fill the available space while retaining the
        original aspect ratio.
        """
           
        self.__set_aspect_ratio(self.__aspect_ratio)


    def __set_aspect_ratio(self, ratio):
        """
        Sets the aspect ratio of the screen to the given value.
        """
    
        if (ratio == 0): return

        #self.__screen.hide()
        
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        if (w < 800):
            x, y, w, h = x + 2, y + 2, w - 4, h - 4
            y += 10
            h -= 20
        else:
            x, y, w, h = x, y, w, h

        w2 = int(ratio * h)
        h2 = int(w / ratio)
         
        #print ratio, w, h, w2, h2
        if (w2 > w):
            if (w > 0): self.__screen.set_size_request(w, h2)
            w2, h2 = w, h2
        else:
            if (w2 > 0): self.__screen.set_size_request(w2, h)
            w2, h2 = w2, h

        self.__layout.move(self.__screen, x + (w - w2) / 2, y + (h - h2) / 2)
        print  x + (w - w2) / 2, y + (h - h2) / 2, w2, h2
        
        while (gtk.events_pending()): gtk.main_iteration()
        self.__screen.show()


    def load(self, uri):
    
        self.__screen.show()
    
        def f():
            if (self.__screen.window.xid):
                if (uri == self.__uri): return
                
                # TODO: get player for MIME type
                self.__player = mediaplayer.get_player_for_uri(uri)
                
                self.__player.set_window(self.__screen.window.xid)
                if (maemo.IS_MAEMO):
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
                #self.__player.show_text(os.path.basename(uri), 2000)
                #self.set_title(os.path.basename(uri))                
                self.__uri = uri
                
                #self.update_observer(self.OBS_SHOW_PANEL)
                
        gobject.idle_add(f)

