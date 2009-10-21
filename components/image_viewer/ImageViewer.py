from com import Player, msgs
from Image import Image
from ui.decorators import Gestures
from ui.KineticScroller import KineticScroller
from ui.Toolbar import Toolbar
from ui.ImageButton import ImageButton
from theme import theme
from utils import logging

import gobject


class ImageViewer(Player):

    def __init__(self):      

        self.__is_fullscreen = False
        self.__zoom_handler = None

        Player.__init__(self)
        
        self.__image = Image()
        self.add(self.__image)
        
        kscr = KineticScroller(self.__image)
        
        gestures = Gestures(self.__image)
        gestures.connect_twirl(self.__on_twirl_gesture, kscr)
        gestures.connect_release(self.__on_release, kscr)
        gestures.connect_hold(self.__on_hold)
        gestures.connect_tap_hold(self.__on_tap_hold)
        gestures.connect_tap_tap(self.__on_tap_tap)
        gestures.connect_swipe(self.__on_swipe)
        
        
        # toolbar elements
        self.__btn_play = ImageButton(theme.mb_btn_play_1,
                                      theme.mb_btn_play_2)
        self.__btn_play.connect_clicked(self.__on_btn_play)
        
        # toolbar
        self.__toolbar = Toolbar()
        self.add(self.__toolbar)

        btn_previous = ImageButton(theme.mb_btn_previous_1,
                                   theme.mb_btn_previous_2)
        btn_previous.connect_clicked(self.__on_btn_previous)

        btn_next = ImageButton(theme.mb_btn_next_1,
                               theme.mb_btn_next_2)
        btn_next.connect_clicked(self.__on_btn_next)

        self.__toolbar.set_toolbar(btn_previous,
                                   self.__btn_play,
                                   btn_next)


    def __on_btn_play(self):
    
        if (self.__player):
            self.__player.pause()


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
        else:
            self.__toolbar.set_visible(True)
        
        self.emit_message(msgs.UI_ACT_FULLSCREEN, self.__is_fullscreen)
        self.render()


    def render_this(self):
    
        w, h = self.get_size()
        if (self.__is_fullscreen):
            # fullscreen mode
            self.__image.set_geometry(0, 0, w, h)
        
        elif (w < h):
            # portrait mode
            self.__image.set_geometry(0, 0, w, h - 70)
            self.__toolbar.set_geometry(0, h - 70, w, 70)

        else:
            # landscape mode
            self.__image.set_geometry(0, 0, w - 70, h)
            self.__toolbar.set_geometry(w - 70, 0, 70, h)        
        
        
    def get_mime_types(self):
    
        return ["image/*"]        

        
    def load(self, f):

        self.__image.load(f)
        self.emit_message(msgs.MEDIA_EV_LOADED, self, f)
        self.render()

