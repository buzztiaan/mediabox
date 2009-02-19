from ui.Widget import Widget
from ui.HBox import HBox
from ui import pixbuftools
from theme import theme

import gtk
import pango


class ControlPanel(Widget):

    def __init__(self):
    
        self.__bg_pbuf = None
    

        Widget.__init__(self)
        self.__box = HBox()
        self.__box.set_spacing(0)
        self.__box.set_halign(self.__box.HALIGN_RIGHT)
        self.__box.set_valign(self.__box.VALIGN_CENTER)
        self.add(self.__box)        


    def _reload(self):
    
        self.__bg_pbuf = None
        w, h = self.get_size()
        self.set_size(w, h)


    def set_size(self, w, h):

        if (not self.__bg_pbuf or (w, h) != self.get_size()):
            self.__bg_pbuf = pixbuftools.make_frame(theme.mb_panel, w, h, True,
                                           pixbuftools.TOP | pixbuftools.RIGHT)
    
        Widget.set_size(self, w, h)
        self.__box.set_size(w - 20, h)
        

        

    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        if (self.__bg_pbuf):
            screen.draw_pixbuf(self.__bg_pbuf, x, y)
 

    def set_toolbar(self, tbset):
        """
        Sets the given toolbar on this panel.
        """
    
        for c in self.__box.get_children():
            self.__box.remove(c)
        
        for c in tbset:
            self.__box.add(c)
            c.set_visible(True)

