from OSDComponent import OSDComponent
from com import msgs
from ui import pixbuftools
from theme import theme
from mediabox import thumbnail

import gtk
import gobject
import pango


class OSDVolume(OSDComponent):

    def __init__(self):
    
        # volume within range [0.0, 1.0]
        self.__volume = 0.0
        
        self.__timeout_handler = None
        
    
        OSDComponent.__init__(self)

        w = gtk.gdk.screen_width() * 0.8
        h = 32
        self.set_size(w, h)
        
        self.set_pos((gtk.gdk.screen_width() - w) / 2,
                     gtk.gdk.screen_height() * 0.90)


    def render_this(self):
    
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.clear_translucent()
        screen.fill_area(0, 0, w, h, "#00000080")
        w -= 4
        if (w * self.__volume > 0):
            screen.fill_area(2, 2, int(w * self.__volume), h - 4, "#ffffff80")
        


    def __hide(self):
    
        self.__timeout_handler = None
        self.set_visible(False)


    def handle_message(self, msg, *args):
    
        if (msg == msgs.MEDIA_EV_VOLUME_CHANGED):
            vol = args[0]
            self.__volume = vol / 100.0

            if (not self.__timeout_handler):
                self.set_visible(True)
            else:
                gobject.source_remove(self.__timeout_handler)
            
            self.__timeout_handler = gobject.timeout_add(2000, self.__hide)
            self.render()

