from com import Player, msgs
from Image import Image
from ui.decorators import Gestures
from ui.KineticScroller import KineticScroller
from ui.Toolbar import Toolbar
from ui.ToolbarButton import ToolbarButton
from ui.EventBox import EventBox
from ui.layout import Arrangement
from ui.dialog import InputDialog
from theme import theme
from utils import logging

import gtk
import gobject


# maximum slideshow timeout in seconds
_SLIDESHOW_MAX_TIMEOUT = 60


_LANDSCAPE_ARRANGEMENT = """
  <arrangement>
    <if-visible name="toolbar">
      <widget name="toolbar" x1="-80" y1="0" x2="100%" y2="100%"/>
      <widget name="image" x1="0" y1="0" x2="-80" y2="100%"/>
    </if-visible>
    
    <!-- fullscreen mode -->
    <if-invisible name="toolbar">
      <widget name="image" x1="0%" y1="0%" x2="100%" y2="100%"/>
    </if-invisible>
  </arrangement>
"""

_PORTRAIT_ARRANGEMENT = """
  <arrangement>
    <widget name="image" x1="0" y1="0" x2="100%" y2="-80"/>
    <widget name="toolbar" x1="0" y1="-80" x2="100%" y2="100%"/>

    <!-- fullscreen mode -->
    <if-invisible name="toolbar">
      <widget name="image" x1="0%" y1="0%" x2="100%" y2="100%"/>
    </if-invisible>
  </arrangement>
"""


class ImageViewer(Player):
    """
    Player component for viewing images.
    """

    def __init__(self):      

        self.__is_fullscreen = False
        self.__zoom_handler = None

        # whether the slideshow is playing
        self.__is_playing = False
        
        # slideshow handler
        self.__slideshow_handler = None

        # slideshow timeout in milliseconds
        self.__slideshow_timeout = 3000
        

        Player.__init__(self)
        
        self.__image = Image()
        self.__image.set_background(theme.color_image_viewer_background)
        #self.add(self.__image)
        
        kscr = KineticScroller(self.__image)
        
        gestures = Gestures(self.__image)
        gestures.connect_twirl(self.__on_twirl_gesture, kscr)
        gestures.connect_release(self.__on_release, kscr)
        #gestures.connect_hold(self.__on_hold)
        #gestures.connect_tap_hold(self.__on_tap_hold)
        gestures.connect_tap_tap(self.__on_tap_tap)
        gestures.connect_swipe(self.__on_swipe)
        
        # toolbar
        self.__btn_play = ToolbarButton(theme.mb_btn_play_1)
        self.__btn_play.connect_clicked(self.__on_btn_play)

        btn_previous = ToolbarButton(theme.mb_btn_previous_1)
        btn_previous.connect_clicked(self.__on_btn_previous)

        btn_next = ToolbarButton(theme.mb_btn_next_1)
        btn_next.connect_clicked(self.__on_btn_next)

        self.__toolbar = Toolbar()
        self.__toolbar.set_toolbar(btn_previous,
                                   self.__btn_play,
                                   btn_next)


        # arrangement
        self.__arr = Arrangement()
        self.__arr.connect_resized(self.__update_layout)
        self.__arr.add(self.__image, "image")
        self.__arr.add(self.__toolbar, "toolbar")
        #self.__arr.add(self.__volume_slider, "slider")
        self.add(self.__arr)


    def __update_layout(self):
    
        w, h = self.get_size()
        if (w < h):
            self.__arr.set_xml(_PORTRAIT_ARRANGEMENT)           
        else:
            self.__arr.set_xml(_LANDSCAPE_ARRANGEMENT)


    def __slideshow_timer(self):
    
        gtk.main_iteration(False)
        
        if (self.__is_playing and self.may_render()):
            self.__image.slide_from_right()
            self.emit_message(msgs.MEDIA_ACT_NEXT)
            return True
            
        else:
            self.__btn_play.set_icon(theme.mb_btn_play_1)
            self.__slideshow_handler = None
            self.__is_playing = False
            self.emit_message(msgs.MEDIA_EV_PAUSE)

            return False



    def __on_btn_play(self):

        self.__is_playing = not self.__is_playing
        if (self.__is_playing):
            dlg = InputDialog("Slideshow Settings")
            dlg.add_range("Seconds between slides:", 1, _SLIDESHOW_MAX_TIMEOUT, 3)
            ret = dlg.run()

            if (ret != dlg.RETURN_OK): return

            secs = dlg.get_values()[0]
            self.__slideshow_timeout = int(secs * 1000)

            self.__btn_play.set_icon(theme.mb_btn_pause_1)
            
            self.emit_message(msgs.MEDIA_EV_PLAY)

            if (self.__slideshow_handler):
                gobject.source_remove(self.__slideshow_handler)
            self.__slideshow_handler = gobject.timeout_add(
                                                      self.__slideshow_timeout,
                                                      self.__slideshow_timer)

        else:
            self.__btn_play.set_icon(theme.mb_btn_play_1)


    def __on_btn_previous(self):
        
        self.__image.slide_from_left()
        self.emit_message(msgs.MEDIA_ACT_PREVIOUS)


    def __on_btn_next(self):
        
        self.__image.slide_from_right()
        self.emit_message(msgs.MEDIA_ACT_NEXT)


    def __on_twirl_gesture(self, direction, kscr):
    
        kscr.set_enabled(False)
        if (direction > 0):
            self.__image.zoom_in()
        else:
            self.__image.zoom_out()


    def __on_release(self, px, py, kscr):
    
        kscr.set_enabled(True)

        if (self.__zoom_handler):
            gobject.source_remove(self.__zoom_handler)


    def __on_hold(self, px, py):
    
        if (self.__zoom_handler):
            gobject.source_remove(self.__zoom_handler)
        self.__zoom_handler = gobject.timeout_add(50, self.__on_zoom_gesture, 1)
        
        
    def __on_tap_hold(self, px, py):
        
        if (self.__zoom_handler):
            gobject.source_remove(self.__zoom_handler)
        self.__zoom_handler = gobject.timeout_add(50, self.__on_zoom_gesture, -1)


    def __on_zoom_gesture(self, direction):
    
        if (direction < 0):
            self.__image.zoom_out(False)
        elif (direction > 0):
            self.__image.zoom_in(False)
        return True



    def __on_tap_tap(self, px, py):
    
        self.__toggle_fullscreen()
        
        
    def __on_swipe(self, direction):
    
        if (self.__image.is_image_fitting()):
            if (direction > 0):
                self.__image.slide_from_left()
                self.emit_message(msgs.MEDIA_ACT_PREVIOUS)
            else:
                self.__image.slide_from_right()
                self.emit_message(msgs.MEDIA_ACT_NEXT)

    
        
    def __toggle_fullscreen(self):
    
        self.__is_fullscreen = not self.__is_fullscreen
        
        if (self.__is_fullscreen):
            self.__toolbar.set_visible(False)
            self.__image.set_background(theme.color_image_viewer_background_fullscreen)
        else:
            self.__toolbar.set_visible(True)
            self.__image.set_background(theme.color_image_viewer_background)
        
        self.emit_message(msgs.UI_ACT_FULLSCREEN, self.__is_fullscreen)
        self.__update_layout()
        self.render()


    def render_this(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        #screen.fill_area(x, y, w, h, theme.color_mb_background)
        self.__arr.set_geometry(0, 0, w, h)
        
        
    def get_mime_types(self):
    
        return ["image/*"]

        
    def load(self, f):

        self.__image.load(f)
        self.emit_message(msgs.MEDIA_EV_LOADED, self, f)
        self.render()


    def handle_MEDIA_ACT_PAUSE(self):
    
        if (self.is_player_active()):
            self.__on_btn_play()


    def handle_INPUT_EV_VOLUME_UP(self, pressed):
    
        if (self.is_visible() and self.__image):
            self.__image.zoom_in(False)
        
        
    def handle_INPUT_EV_VOLUME_DOWN(self, pressed):

        if (self.is_visible() and self.__image):
            self.__image.zoom_out(False) 

