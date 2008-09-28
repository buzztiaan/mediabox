from ui.Widget import Widget
from ui.HBox import HBox
from utils.Observable import Observable

import theme

import gtk
import pango


class ControlPanel(Widget, Observable):   

    def __init__(self):

        Widget.__init__(self)
        self.__box = HBox()
        self.__box.set_spacing(0)
        self.__box.set_alignment(self.__box.ALIGN_RIGHT)
        self.add(self.__box)        


    def set_size(self, w, h):
    
        Widget.set_size(self, w, h)
        self.__box.set_size(w - 20, h)
        

    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        screen.draw_frame(theme.mb_panel, x, y, w, h, True,
                          screen.TOP | screen.RIGHT)

 

    def set_toolbar(self, tbset):
        """
        Sets the given toolbar on this panel.
        """
    
        for c in self.__box.get_children():
            self.__box.remove(c)
        
        for c in tbset:
            self.__box.add(c)
            c.set_visible(True)

