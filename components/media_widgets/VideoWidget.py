from mediabox.MediaWidget import MediaWidget
from ui.EventBox import EventBox
import mediaplayer
from utils import maemo

import gtk
import gobject


class VideoWidget(MediaWidget):
    """
    Widget for viewing videos.
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
        self.__ebox.connect_clicked(self.__on_click)




    def render_this(self):
            
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()    

        self.__ebox.set_size(w, h)

        fx, fy, fw, fh = x + 4, y + 32, w - 16, h - 92
        vx, vy, vw, vh = x + 6, y + 40, w - 20, h - 110

        if (w < 800):
            screen.draw_rect(fx, fy, fw, fh, "#000000")
            screen.fill_area(fx + 2, fy + 2, fw - 4, fh - 4, "#000000")
            self.__layout.move(self.__screen, vx, vy)
            self.__screen.set_size_request(vw, vh)
        else:
            screen.fill_area(x, y, w, h, "#000000")
            self.__layout.move(self.__screen, x, y)
            self.__screen.set_size_request(w, h)


    def set_visible(self, value):
    
        if (value):
            self.__screen.show()
        else:
            self.__screen.hide()
            
        MediaWidget.set_visible(self, value)

        
    def __on_expose(self, src, ev):
    
        return
        if (self.__player.has_video()):
            win = self.__screen.window
            gc = win.new_gc()
            cmap = win.get_colormap()
            gc.set_foreground(cmap.alloc_color("#000000"))
            x, y, w, h = ev.area
            self.__player.handle_expose(win, gc, x, y, w, h)

            
            
    def __on_click(self):
    
        return
        #vx, vy, vw, vh = self.__get_video_rect()
        #if (vx <= px <= vx + vw and vy <= py <= py + vh):
        self.__on_fullscreen()



    def __on_observe_player(self, src, cmd, *args):
           
        """  
        if (cmd == src.OBS_STARTED):
            print "Started Player"
            self.__btn_play.set_images(theme.btn_play_1,
                                       theme.btn_play_2)
            #self.update_observer(self.OBS_STATE_PAUSED)
            
        elif (cmd == src.OBS_KILLED):
            print "Killed Player"
            self.__uri = ""
            self.set_title("")
            self.__screen.hide()
            self.__btn_play.set_images(theme.btn_play_1,
                                       theme.btn_play_2)
            #self.update_observer(self.OBS_STATE_PAUSED)

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
                self.__btn_play.set_images(theme.btn_pause_1,
                                           theme.btn_pause_2)                
                #self.update_observer(self.OBS_STATE_PLAYING)
            
        elif (cmd == src.OBS_STOPPED):
            ctx = args[0]
            if (ctx == self.__context_id):
                print "Stopped"
                self.__btn_play.set_images(theme.btn_play_1,
                                           theme.btn_play_2)
                #self.update_observer(self.OBS_STATE_PAUSED)
            
        elif (cmd == src.OBS_POSITION):
            ctx, pos, total = args            
            if (not self.__is_fullscreen and ctx == self.__context_id):
                pos_m = pos / 60
                pos_s = pos % 60
                total_m = total / 60
                total_s = total % 60
                info = "%d:%02d / %d:%02d" % (pos_m, pos_s, total_m, total_s)
                self.set_info(info)

                self.__progress.set_position(pos, total)

        elif (cmd == src.OBS_EOF):
            ctx = args[0]
            if (ctx == self.__context_id):        
                self.__uri = ""
                self.__screen.hide()

                # unfullscreen
                if (self.__is_fullscreen): self.__on_fullscreen()
                
                self.__btn_play.set_images(theme.btn_play_1,
                                           theme.btn_play_2)                
                #self.update_observer(self.OBS_STATE_PAUSED)
        """   
        if (cmd == src.OBS_ASPECT):
            ctx, ratio = args            
            self.__aspect_ratio = ratio
            self.__set_aspect_ratio(ratio)
            #self.__screen.show()


    def __set_aspect_ratio(self, ratio):
        """
        Sets the aspect ratio of the screen to the given value.
        """
    
        if (ratio == 0): return
        
        #self.__screen.hide()
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        x, y, w, h = x + 6, y + 40, w - 20, h - 110

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
