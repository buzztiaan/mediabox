from ui.Widget import Widget
from ui.layout import Box
from ui.Pixmap import Pixmap
from theme import theme

import gtk


class Toolbar(Widget):

    def __init__(self):
    
        # offscreen buffer
        self.__buffer = None
    
        self.__bg_pmap = None
    
        self.__current_set = []
    

        Widget.__init__(self)
        self.__box = Box()
        self.__box.set_spacing(2)
        self.__box.set_halign(self.__box.HALIGN_CENTER)
        self.__box.set_valign(self.__box.VALIGN_CENTER)
        self.add(self.__box)        


    def _reload(self):
    
        self.__bg_pmap = None
        w, h = self.get_size()
        if (w and h):
            self.set_size(w, h)


    def set_size(self, w, h):

        if (w < h):
            edges = Pixmap.LEFT
        else:
            edges = Pixmap.TOP

        if (not self.__bg_pmap or (w, h) != self.get_size()):
            self.__buffer = None
            self.__bg_pmap = Pixmap(None, w, h)
            self.__bg_pmap.fill_area(0, 0, w, h, theme.color_mb_background)
            self.__bg_pmap.draw_frame(theme.mb_panel, 0, 0, w, h, True,
                                      edges)
    
            self.__box.set_size(w, h)

        Widget.set_size(self, w, h)
        

        

    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        if (w < h):
            self.__box.set_orientation(Box.VERTICAL)
        else:
            self.__box.set_orientation(Box.HORIZONTAL)

        if (self.__bg_pmap):
            screen.draw_pixmap(self.__bg_pmap, x, y)


    def set_toolbar(self, *tbset):
        """
        Sets the given toolbar on this panel.
        """
    
        if (tuple(tbset) == tuple(self.__current_set)):
            return
        
        self.__current_set = tbset
    
        for c in self.__box.get_children():
            self.__box.remove(c)
        
        for c in tbset:
            self.__box.add(c, True)
            c.set_visible(True)

        if (not self.__buffer):
            w, h = self.get_size()
            if (w > 0 and h > 0):
                self.__buffer = Pixmap(None, w, h)    

        if (self.__buffer):
            self.render_buffered(self.__buffer)

