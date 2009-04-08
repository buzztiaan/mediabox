from ui.Widget import Widget
from ui.HBox import HBox
from ui.Pixmap import Pixmap
from theme import theme

import gtk
import pango


class ControlPanel(Widget):

    def __init__(self):
    
        self.__bg_pmap = None
    

        Widget.__init__(self)
        self.__box = HBox()
        self.__box.set_spacing(0)
        self.__box.set_halign(self.__box.HALIGN_RIGHT)
        self.__box.set_valign(self.__box.VALIGN_CENTER)
        self.add(self.__box)        


    def _reload(self):
    
        self.__bg_pmap = None
        w, h = self.get_size()
        self.set_size(w, h)


    def set_size(self, w, h):

        if (not self.__bg_pmap or (w, h) != self.get_size()):
            self.__bg_pmap = Pixmap(None, w, h)
            self.__bg_pmap.fill_area(0, 0, w, h, theme.color_mb_background)
            self.__bg_pmap.draw_frame(theme.mb_panel, 0, 0, w, h, True,
                                      Pixmap.LEFT | Pixmap.TOP | Pixmap.RIGHT)
    
            Widget.set_size(self, w, h)
            self.__box.set_size(w - 20, h)
        

        

    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        if (self.__bg_pmap):
            screen.draw_pixmap(self.__bg_pmap, x, y)
        screen.draw_pixbuf(theme.mb_btn_turn, x + 10, y + 4)
 

    def set_toolbar(self, tbset):
        """
        Sets the given toolbar on this panel.
        """
    
        for c in self.__box.get_children():
            self.__box.remove(c)
        
        for c in tbset:
            self.__box.add(c, False)
            c.set_visible(True)

        self.render()
