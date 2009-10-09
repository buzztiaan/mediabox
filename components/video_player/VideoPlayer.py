from com import Player, msgs
from ui.VideoScreen import VideoScreen
from ui.Toolbar import Toolbar
from ui.ImageButton import ImageButton
from ui.ProgressBar import ProgressBar
from ui.Slider import Slider
import mediaplayer
import platforms
from theme import theme
from utils import logging

import gobject


class VideoPlayer(Player):

    def __init__(self):

        self.__player = None
        self.__context_id = 0
        self.__is_playing = False
        
        self.__blanking_handler = None

        Player.__init__(self)
        
        # video screen
        self.__screen = VideoScreen()
        self.add(self.__screen)


        # volume slider
        self.__volume_slider = Slider(theme.mb_list_slider)
        self.__volume_slider.set_mode(Slider.VERTICAL)
        self.__volume_slider.connect_value_changed(self.__on_change_volume)
        self.add(self.__volume_slider)


        # progress bar
        self.__progress = ProgressBar()
        self.add(self.__progress)
        self.__progress.connect_changed(self.__on_seek)
        
        
        # toolbar elements
        self.__btn_play = ImageButton(theme.mb_btn_play_1,
                                      theme.mb_btn_play_2)
        self.__btn_play.connect_clicked(self.__on_btn_play)

        btn_previous = ImageButton(theme.mb_btn_previous_1,
                                   theme.mb_btn_previous_2)
        btn_previous.connect_clicked(self.__on_btn_previous)

        btn_next = ImageButton(theme.mb_btn_next_1,
                               theme.mb_btn_next_2)
        btn_next.connect_clicked(self.__on_btn_next)
        
        # toolbar
        self.__toolbar = Toolbar()
        self.add(self.__toolbar)
        self.__toolbar.set_toolbar(btn_previous,
                                   self.__btn_play,
                                   btn_next)


    def __on_btn_play(self):
    
        if (self.__player):
            self.__player.pause()


    def __on_btn_previous(self):
        
        self.emit_message(msgs.MEDIA_ACT_PREVIOUS)


    def __on_btn_next(self):
        
        self.emit_message(msgs.MEDIA_ACT_NEXT)


    def __on_status_changed(self, ctx_id, status):
    
        if (ctx_id == self.__context_id):
            if (status == self.__player.STATUS_PLAYING):
                self.__btn_play.set_images(theme.mb_btn_pause_1,
                                           theme.mb_btn_pause_2)
                self.__is_playing = True
                self.emit_message(msgs.MEDIA_EV_PLAY)
                
                # we need manual unblanking on Maemo5 for videos
                if (not self.__blanking_handler and
                      platforms.PLATFORM == platforms.MAEMO5):
                    self.__blanking_handler = gobject.timeout_add(25000,
                                                      self.__inhibit_blanking)
                #end if
                                           
            elif (status == self.__player.STATUS_STOPPED):
                self.__btn_play.set_images(theme.mb_btn_play_1,
                                           theme.mb_btn_play_2)
                self.__is_playing = False
                self.emit_message(msgs.MEDIA_EV_PAUSE)

            elif (status == self.__player.STATUS_EOF):
                self.__btn_play.set_images(theme.mb_btn_play_1,
                                           theme.mb_btn_play_2)
                self.__is_playing = False
                self.emit_message(msgs.MEDIA_EV_EOF)



    def __on_update_position(self, ctx_id, pos, total):
    
        if (ctx_id == self.__context_id):
            self.__progress.set_position(pos, total)


    def __on_change_volume(self, v):
    
        if (self.__player):
            vol = int(v * 100)
            self.__player.set_volume(vol)


    def __on_seek(self, progress):
    
        if (self.__player):
            self.__player.seek_percent(progress)


    def __inhibit_blanking(self):
    
        if (self.__is_playing):
            platforms.inhibit_screen_blanking()
            return True
        else:
            self.__blanking_handler = None
            return False


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, theme.color_mb_background)
        
        if (w < h):
            # portrait mode
            self.__screen.set_geometry(42, 0, w - 42, h - 70 - 70)
            self.__progress.set_geometry(20, h - 70 - 50, w - 40, 32)
            self.__volume_slider.set_geometry(0, 0, 42, h - 70 - 70)
            self.__toolbar.set_geometry(0, h - 70, w, 70)

        else:
            # landscape mode
            self.__screen.set_geometry(42, 0, w - 70 - 42, h - 70)
            self.__progress.set_geometry(42, h - 50, w - 70 - 84, 32)
            self.__volume_slider.set_geometry(0, 0, 42, h)
            self.__toolbar.set_geometry(w - 70, 0, 70, h)
        
        
    def get_mime_types(self):
    
        return ["video/*"]        

        
    def load(self, f):
    
        self.__player = mediaplayer.get_player_for_mimetype(f.mimetype)
        self.__player.connect_status_changed(self.__on_status_changed)
        self.__player.connect_position_changed(self.__on_update_position)
        
        self.__player.set_window(self.__screen.get_xid())
        
        """
        uri = item.get_resource()
        if (not uri.startswith("/") and
            not "://localhost" in uri and
            not "://127.0.0.1" in uri):                    
            maemo.request_connection()
        #end if
        """
        
        uri = f.get_resource()
        try:
            self.__context_id = self.__player.load_video(uri)
        except:
            logging.error("error loading media file: %s\n%s",
                          uri, logging.stacktrace())

        self.render()
