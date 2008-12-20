from mediabox.MediaWidget import MediaWidget
from mediabox import media_bookmarks
from mediabox import config as mb_config
from ui.EventBox import EventBox
from ui.ImageButton import ImageButton
from ui.Image import Image
from ui.ProgressBar import ProgressBar
import mediaplayer
from ui import dialogs
from utils import maemo
from utils import logging
from theme import theme

import gtk
import gobject


class VideoWidget(MediaWidget):
    """
    Media widget for viewing videos.
    """


    def __init__(self):
    
        self.__player = None
        self.__load_handler = None
        mediaplayer.add_observer(self.__on_observe_player)

        self.__aspect_ratio = 1.0

        self.__current_file = None
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
        self.__btn_play = ImageButton(theme.mb_btn_play_1,
                                      theme.mb_btn_play_2)
        self.__btn_play.connect_clicked(self.__on_play_pause)

        self.__progress = ProgressBar()
        self.__progress.connect_changed(self.__on_set_position)
        self.__progress.connect_bookmark_changed(self.__on_change_bookmark)
        
        btn_bookmark = ImageButton(theme.mb_btn_bookmark_1,
                                   theme.mb_btn_bookmark_2)
        btn_bookmark.connect_clicked(self.__on_add_bookmark)
        
        self._set_controls(Image(theme.mb_toolbar_space_1),
                           self.__btn_play,
                           Image(theme.mb_toolbar_space_2),
                           self.__progress,
                           Image(theme.mb_toolbar_space_2),
                           btn_bookmark,
                           Image(theme.mb_toolbar_space_1))        


    def _visibility_changed(self):

        if (not self.may_render()):
            self.__hide_video_screen()
        else:
            pass #self.__show_video_screen()


    def set_frozen(self, v):
    
        if (v):
            self.__hide_video_screen()
        #else:
        #    self.__show_video_screen()

    def set_size(self, w, h):
    
        if ((w, h) != self.get_size()):
            MediaWidget.set_size(self, w, h)
            self.__scale_video()


    def __show_video_screen(self):
    
        if (not self.get_screen().is_offscreen() and
            self.may_render() and
            self.__player and
            self.__player.has_video()):
            self.__screen.show()
            
    
    def __hide_video_screen(self):
    
        self.__screen.hide()


    def render_this(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()    

        self.__ebox.set_geometry(0, 0, w, h)

        fx, fy, fw, fh = x, y, w, h
        vx, vy, vw, vh = x + 2, y + 2, w - 4, h - 4

        if (w < 800):
            screen.draw_rect(fx, fy, fw, fh, "#000000")
            screen.fill_area(vx, vy, vw, vh, "#000000")
        else:
            screen.fill_area(x, y, w, h, "#000000")

        gobject.idle_add(self.__show_video_screen)
        
    def __on_expose(self, src, ev):

        if (self.__player and self.__player.has_video()):
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
                if (total > 0.001):
                    total_m = total / 60
                    total_s = total % 60
                    info = "%d:%02d / %d:%02d" % (pos_m, pos_s, total_m, total_s)
                else:
                    info = "%d:%02d" % (pos_m, pos_s)            

                self.send_event(self.EVENT_MEDIA_POSITION, info)
                self.__progress.set_position(pos, total)

        elif (cmd == src.OBS_STARTED):
            print "Started Player"
            self.__progress.set_message("")
            #self.__btn_play.set_images(theme.btn_play_1,
            #                           theme.btn_play_2)
            
        elif (cmd == src.OBS_KILLED):
            print "Killed Player"
            self.__uri = ""
            self.__progress.set_message("")
            self.__hide_video_screen()
            self.__btn_play.set_images(theme.mb_btn_play_1,
                                       theme.mb_btn_play_2)

        elif (cmd == src.OBS_ERROR):
            ctx, err = args
            if (ctx == self.__context_id):
                self.__current_file = None
                self.__btn_play.set_images(theme.mb_btn_play_1,
                                           theme.mb_btn_play_2)
                self.__progress.set_message("error")
                self.__show_error(err)
                self.__hide_video_screen()
            
        elif (cmd == src.OBS_PLAYING):
            ctx = args[0]
            if (ctx == self.__context_id):
                print "Playing"
                self.__progress.set_message("")
                self.__btn_play.set_images(theme.mb_btn_pause_1,
                                           theme.mb_btn_pause_2)
                self.__show_video_screen()
            
        elif (cmd == src.OBS_STOPPED):
            ctx = args[0]
            if (ctx == self.__context_id):
                print "Stopped"
                self.__progress.set_message("")
                self.__btn_play.set_images(theme.mb_btn_play_1,
                                           theme.mb_btn_play_2)
            
        elif (cmd == src.OBS_EOF):
            ctx = args[0]
            if (ctx == self.__context_id):        
                self.__uri = ""
                self.__hide_video_screen()

                # unfullscreen
                #if (self.__is_fullscreen): self.__on_fullscreen()
                
                self.__btn_play.set_images(theme.mb_btn_play_1,
                                           theme.mb_btn_play_2)                
                self.send_event(self.EVENT_MEDIA_EOF)


        elif (cmd == src.OBS_ASPECT):
            ctx, ratio = args
            if (ctx == self.__context_id):
                self.__aspect_ratio = ratio
                self.__set_aspect_ratio(ratio)



    def __show_error(self, errcode):
    
        if (errcode == self.__player.ERR_INVALID):
            dialogs.error("Invalid Stream", "Cannot load this stream.")
        elif (errcode == self.__player.ERR_NOT_FOUND):
            dialogs.error("Not found", "Cannot find a stream to play.")
        elif (errcode == self.__player.ERR_CONNECTION_TIMEOUT):
            dialogs.error("Timeout", "Connection timed out.")       
        elif (errcode == self.__player.ERR_NOT_SUPPORTED):
            dialogs.error("Not supported", "The media format is not supported.")


    def __on_set_position(self, pos):
    
        self.__player.set_volume(mb_config.volume())
        self.__player.seek_percent(pos)


    def __on_play_pause(self):
    
        self.__player.set_volume(mb_config.volume())
        self.__player.pause()
        
   
    def __on_add_bookmark(self):
    
        if (self.__current_file):
            self.__progress.add_bookmark()


    def __on_change_bookmark(self):
    
        if (self.__current_file):
            bookmarks = self.__progress.get_bookmarks()
            media_bookmarks.set_bookmarks(self.__current_file, bookmarks)


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
         
        #print ratio, w, h, w2, h2, self
        if (w2 > w):
            if (w > 0): self.__screen.set_size_request(w, h2)
            w2, h2 = w, h2
        else:
            if (w2 > 0): self.__screen.set_size_request(w2, h)
            w2, h2 = w2, h

        self.__layout.move(self.__screen, x + (w - w2) / 2, y + (h - h2) / 2)
        #print  x + (w - w2) / 2, y + (h - h2) / 2, w2, h2
        
        cnt = 0
        while (gtk.events_pending() and cnt < 10):
            gtk.main_iteration(False)
            cnt += 1
        #self.__show_video_screen()


    def load(self, item):
    
        self.__show_video_screen()
    
        def f():
            self.__load_handler = None
            uri = item.get_resource()
            if (not uri.startswith("/") and
                not "://localhost" in uri and
                not "://127.0.0.1" in uri):                    
                maemo.request_connection()
            #end if
            
            if (self.__screen.window.xid):
                #if (uri == self.__uri): return
                
                # TODO: get player for MIME type
                self.__player = mediaplayer.get_player_for_mimetype(item.mimetype)
                
                self.__player.set_window(self.__screen.window.xid)
                product = maemo.get_product_code()
                if (product == "?"):
                    self.__player.set_options("-vo xv")
                elif (product == "SU-18"):
                    self.__player.set_options("-vo nokia770:" \
                                              "fb_overlay_only:" \
                                              "x=174:y=60:w=600:h=360")
                else:
                    self.__player.set_options("-vo xv")
                    
                try:
                    self.__context_id = self.__player.load(uri)
                except:
                    logging.error("could not load video '%s'\n%s" \
                                  % (uri, logging.stacktrace()))
                    self.__hide_video_screen()
                    return
                                
                self.__player.set_volume(mb_config.volume())
                bookmarks = media_bookmarks.get_bookmarks(item)
                self.__progress.set_bookmarks(bookmarks)
                #self.__player.show_text(os.path.basename(uri), 2000)
                #self.set_title(os.path.basename(uri))                
                self.__uri = uri
                self.__current_file = item
                
                #self.update_observer(self.OBS_SHOW_PANEL)

        if (self.__load_handler):
            gobject.source_remove(self.__load_handler)
            
        self.__load_handler = gobject.idle_add(f)                



    def stop(self):
    
        if (self.__player):
            self.__player.stop()


    def close(self):
        
        if (self.__player):
            self.__player.close()
            

    def increment(self):

        vol = mb_config.volume()
        vol = min(100, vol + 5)
        mb_config.set_volume(vol)        
        if (self.__player):
            self.__player.set_volume(vol)
        self.send_event(self.EVENT_MEDIA_VOLUME, vol)

       
        
    def decrement(self):

        vol = mb_config.volume()
        vol = max(0, vol - 5)
        mb_config.set_volume(vol)        
        if (self.__player):
            self.__player.set_volume(vol)
        self.send_event(self.EVENT_MEDIA_VOLUME, vol)

