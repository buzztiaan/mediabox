from com import Player, msgs
from ui.decorators import Gestures
from ui.VideoScreen import VideoScreen
from ui.Toolbar import Toolbar
from ui.ToolbarButton import ToolbarButton
from ui.ImageButton import ImageButton
from ui.MediaProgressBar import MediaProgressBar
from ui.Slider import Slider
from ui.layout import Arrangement
from ui import windowflags
from mediabox import media_bookmarks
import mediaplayer
import platforms
from theme import theme
from utils import logging

import gobject
import gtk


_LANDSCAPE_ARRANGEMENT = """
  <arrangement>
    <if-visible name="toolbar">
      <widget name="toolbar" x1="-100" y1="0" x2="100%" y2="100%"/>
      <widget name="screen" x1="40" y1="4" x2="-100" y2="-48"/>
      <widget name="progress" x1="0" y1="-48" x2="-100" y2="100%"/>
      <!-- <widget name="btn_star" x1="0" y1="-48" x2="48" y2="100%"/> -->
      <widget name="slider" x1="0" y1="0" x2="40" y2="-48"/>
    </if-visible>
    
    <!-- fullscreen mode -->
    <if-invisible name="toolbar">
      <widget name="screen" x1="1" y1="1" x2="-1" y2="-1"/>
    </if-invisible>
  </arrangement>
"""

# hmm, there is no such thing as portrait mode video. Fremantle either does not
# rotate or will just crash, depending on the firmware version
# we simply hide the video screen while in portrait mode and play sound only
_PORTRAIT_ARRANGEMENT = """
  <arrangement>
    <widget name="toolbar" x1="0" y1="-100" x2="100%" y2="100%"/>
    <widget name="screen" x1="40" y1="0" x2="100%" y2="-172"/>
    <widget name="progress" x1="48" y1="-172" x2="100%" y2="-100"/>
    <!-- <widget name="btn_star" x1="0" y1="-172" x2="48" y2="-100"/> -->
    <widget name="slider" x1="0" y1="0" x2="40" y2="-172"/>
  </arrangement>
"""


class VideoPlayer(Player):
    """
    Player component for playing videos.
    """

    def __init__(self):

        self.__is_fullscreen = False
        self.__volume = 50

        self.__player = None
        self.__context_id = 0
        self.__is_playing = False
        
        self.__blanking_handler = None
        self.__load_failed_handler = None

        # the currently playing file object (e.g. used for bookmarking)
        self.__current_file = None


        Player.__init__(self)
        
        # video screen
        self.__screen = VideoScreen()

        gestures = Gestures(self.__screen)
        gestures.connect_tap(self.__on_tap)
        gestures.connect_tap_tap(self.__on_tap_tap)
        gestures.connect_swipe(self.__on_swipe)

        # volume slider
        self.__volume_slider = Slider(theme.mb_list_slider)
        self.__volume_slider.set_mode(Slider.VERTICAL)
        self.__volume_slider.connect_value_changed(self.__on_change_volume)


        # progress bar
        self.__progress = MediaProgressBar(MediaProgressBar.UP)
        self.__progress.connect_changed(self.__on_seek)
        self.__progress.connect_bookmark_changed(self.__on_change_bookmark)


        # star button for bookmarks
        #self.__btn_star = ImageButton(theme.mb_btn_bookmark_1,
        #                              theme.mb_btn_bookmark_2)
        #self.__btn_star.connect_clicked(self.__on_btn_star)

        
        # toolbar elements
        self.__btn_play = ToolbarButton(theme.mb_btn_play_1)
        self.__btn_play.connect_clicked(self.__on_btn_play)

        btn_previous = ToolbarButton(theme.mb_btn_previous_1)
        btn_previous.connect_clicked(self.__on_btn_previous)

        btn_next = ToolbarButton(theme.mb_btn_next_1)
        btn_next.connect_clicked(self.__on_btn_next)
        
        # toolbar
        self.__toolbar = Toolbar()
        self.__toolbar.set_toolbar(btn_previous,
                                   self.__btn_play,
                                   btn_next)


        # arrangement
        self.__arr = Arrangement()
        self.__arr.connect_resized(self.__update_layout)
        self.__arr.add(self.__screen, "screen")
        self.__arr.add(self.__toolbar, "toolbar")
        self.__arr.add(self.__progress, "progress")
        #self.__arr.add(self.__btn_star, "btn_star")
        self.__arr.add(self.__volume_slider, "slider")
        self.add(self.__arr)


    def __update_layout(self):
    
        w, h = self.get_size()
        #if (self.__is_fullscreen):
        #    self.__btn_star.set_visible(False)
        #else:
        #    self.__btn_star.set_visible(True)
        
        if (w < h):
            self.__arr.set_xml(_PORTRAIT_ARRANGEMENT)           
        else:
            self.__arr.set_xml(_LANDSCAPE_ARRANGEMENT)


    def __on_btn_play(self):

        if (self.__player):
            if (not self.__is_playing):
                self.__wait_for_dsp()
            self.__player.pause()


    def __on_btn_previous(self):
        
        self.emit_message(msgs.MEDIA_ACT_PREVIOUS)


    def __on_btn_next(self):
        
        self.emit_message(msgs.MEDIA_ACT_NEXT)


    def __on_tap(self, px, py):
    
        self.__toggle_fullscreen()


    def __on_tap_tap(self, px, py):
    
        self.__toggle_fullscreen()
        
        
    def __on_swipe(self, direction):
    
        if (self.__player):
            if (direction < 0):
                self.__player.rewind()
            elif (direction > 0):
                self.__player.forward()
        #end if


    def __on_status_changed(self, ctx_id, status):
    
        if (ctx_id == self.__context_id):
            if (status == self.__player.STATUS_PLAYING):
                self.__btn_play.set_icon(theme.mb_btn_pause_1)
                
                if (self.__load_failed_handler):
                    gobject.source_remove(self.__load_failed_handler)

                self.__is_playing = True
                self.__progress.set_message("")
                self.emit_message(msgs.MEDIA_EV_PLAY)
                
                # we need manual unblanking on Maemo5 for videos
                if (not self.__blanking_handler and
                      platforms.PLATFORM == platforms.MAEMO5):
                    self.__blanking_handler = gobject.timeout_add(23000,
                                                      self.__inhibit_blanking)
                #end if
                                           
            elif (status == self.__player.STATUS_STOPPED):
                self.__btn_play.set_icon(theme.mb_btn_play_1)
                self.__is_playing = False
                self.call_service(msgs.VIDEOPLAYER_SVC_RELEASE_DSP)
                self.emit_message(msgs.MEDIA_EV_PAUSE)

            elif (status == self.__player.STATUS_EOF):
                self.__btn_play.set_icon(theme.mb_btn_play_1)
                self.__is_playing = False
                self.call_service(msgs.VIDEOPLAYER_SVC_RELEASE_DSP)
                self.emit_message(msgs.MEDIA_EV_EOF)
                self.emit_message(msgs.MEDIA_ACT_NEXT)

            elif (status == self.__player.STATUS_CONNECTING):
                self.__progress.set_message("Connecting")

            elif (status == self.__player.STATUS_BUFFERING):
                self.__progress.set_message("Buffering")
                

    def __on_update_position(self, ctx_id, pos, total):
    
        if (ctx_id == self.__context_id):
            self.__progress.set_position(pos, total)
            self.__progress.set_message("%s / %s" \
                                        % (self.seconds_to_hms(pos),
                                           self.seconds_to_hms(total)))
            self.emit_message(msgs.MEDIA_EV_POSITION, pos, total)


    def __on_change_volume(self, v):
    
        if (self.__player):
            vol = int(v * 100)
            self.__player.set_volume(vol)
            self.__volume = vol


    def __on_change_player_volume(self, v):
    
        if (v != self.__volume):
            self.__volume_slider.set_value(v / 100.0)
            self.__volume = v


    def __on_change_player_aspect_ratio(self, ctx_id, r):
    
        if (ctx_id == self.__context_id and self.__player):
            self.__screen.set_aspect_ratio(r)
        

    def __on_change_bookmark(self):
    
        media_bookmarks.set_bookmarks(self.__current_file,
                                      self.__progress.get_bookmarks())


    def __on_error(self, ctx_id, err):
    
        if (ctx_id == self.__context_id and self.__player):
            self.emit_message(msgs.UI_ACT_SHOW_INFO, self.__player.ERRORS[err])


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


    def __toggle_fullscreen(self):
    
        self.__is_fullscreen = not self.__is_fullscreen
        if (self.__is_fullscreen):
            self.__progress.set_visible(False)
            self.__volume_slider.set_visible(False)
            self.__toolbar.set_visible(False)
            #self.__btn_star.set_visible(False)
        else:
            self.__progress.set_visible(True)
            self.__volume_slider.set_visible(True)
            self.__toolbar.set_visible(True)
            #self.__btn_star.set_visible(True)

        self.__update_layout()
        self.emit_message(msgs.UI_ACT_FULLSCREEN, self.__is_fullscreen)
        #self.render()


    def _visibility_changed(self):
    
        # force video to landscape mode on Maemo
        win = self.get_window()
        if (win): # and platforms.MAEMO5):
            if (self.is_visible()):
                print "show video"
                logging.debug("[videoplayer] forcing landscape mode")
                self.emit_message(msgs.ASR_ACT_ENABLE, False)
                self.emit_message(msgs.ASR_EV_LANDSCAPE)
            
            else:
                print "hide video"
                self.emit_message(msgs.ASR_ACT_RESTORE)
        #end if
        
        self.__screen.render() #set_visible(self.is_visible())


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        if (w == 0 or h == 0): return
        
        if (self.__is_fullscreen):
            screen.fill_area(x, y, w, h, "#000000")
        else:
            screen.fill_area(x, y, w, h, theme.color_mb_background)
        self.__arr.set_geometry(0, 0, w, h)
        
        if (w < h):
            self.__screen.set_visible(False)
            if (platforms.MAEMO4):
                screen.draw_centered_text("Video cannot be displayed in\n" \
                                          "portrait mode.",
                                          theme.font_mb_plain,
                                          0, h / 2 - 80, w, 0, theme.color_mb_text)
        else:
            self.__screen.set_visible(True)

        
    def get_mime_types(self):
    
        return ["video/*"]        


    def __wait_for_dsp(self):

        self.__progress.set_message("Waiting for DSP")
        self.call_service(msgs.VIDEOPLAYER_SVC_LOCK_DSP)
        self.__progress.set_message("")


    def __on_load_failed(self):
    
        self.__load_failed_handler = None
        self.call_service(msgs.VIDEOPLAYER_SVC_RELEASE_DSP)

        
    def load(self, f):

        self.render()
        self.__wait_for_dsp()

        self.__player = self.call_service(msgs.MEDIA_SVC_GET_OUTPUT)
        self.__player.connect_status_changed(self.__on_status_changed)
        self.__player.connect_position_changed(self.__on_update_position)
        self.__player.connect_volume_changed(self.__on_change_player_volume)
        self.__player.connect_aspect_changed(self.__on_change_player_aspect_ratio)
        self.__player.connect_error(self.__on_error)
        
        self.__player.set_window(self.__screen.get_xid())
        
        # loading may fail, so we need to setup a handler that frees the DSP
        # semaphore after some time
        if (self.__load_failed_handler):
                    gobject.source_remove(self.__load_failed_handler)
        self.__load_failed_handler = gobject.timeout_add(30000,
                                                         self.__on_load_failed)
        
        try:
            self.__progress.set_message("Loading")
            self.__context_id = self.__player.load_video(f)

            self.__current_file = f

            # load bookmarks
            self.__progress.set_bookmarks(media_bookmarks.get_bookmarks(f))

            self.emit_message(msgs.MEDIA_EV_LOADED, self, f)
        except:
            self.__progress.set_message("Error")
            logging.error("[videoplayer] error loading media file: %s\n%s",
                          f, logging.stacktrace())


    def set_bookmark(self):
    
        self.__progress.add_bookmark()


    def handle_MEDIA_ACT_PLAY(self):
    
        if (self.__player and self.is_player_active()):
            if (not self.__is_playing):
                self.__wait_for_dsp()
            self.__player.play()


    def handle_MEDIA_ACT_PAUSE(self):
    
        if (self.__player and self.is_player_active()):
            if (not self.__is_playing):
                self.__wait_for_dsp()
            self.__player.pause()                


    def handle_MEDIA_ACT_STOP(self):
    
        if (self.__player and self.is_player_active()):
            self.__player.stop()


    def handle_MEDIA_ACT_SEEK(self, pos):
    
        if (self.__player and self.is_player_active()):
            self.__player.seek(pos)

        
    def handle_INPUT_EV_FULLSCREEN(self, pressed):

        if (self.is_visible()):
            self.__toggle_fullscreen()


    def handle_INPUT_EV_VOLUME_UP(self, pressed):

        self.__volume = min(100, self.__volume + 5)
        self.__volume_slider.set_value(self.__volume / 100.0)
        if (self.__player):
            self.__player.set_volume(self.__volume)
        
        
    def handle_INPUT_EV_VOLUME_DOWN(self, pressed):

        self.__volume = max(0, self.__volume - 5)
        self.__volume_slider.set_value(self.__volume / 100.0)
        if (self.__player):
            self.__player.set_volume(self.__volume)


    def handle_COM_EV_APP_SHUTDOWN(self):
    
        if (self.__player):
            self.__player.close()

