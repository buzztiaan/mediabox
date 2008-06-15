from StripItem import StripItem
from Pixmap import Pixmap, TEMPORARY_PIXMAP
import theme


class Item(StripItem):

    def __init__(self):

        self.__normal_bg = None
        self.__hilighted_bg = None
        
        StripItem.__init__(self)
        

    def set_graphics(self, normal, hilighted):
    
        self.__normal_bg = normal
        self.__hilighted_bg = hilighted
       
        
    def render_this(self, cnv):

        w, h = self.get_size()    
        cnv.fill_area(0, 0, w, h, theme.color_bg)        

        background = self.is_hilighted() and self.__hilighted_bg \
                                         or self.__normal_bg

        if (background):
            cnv.draw_frame(background, 0, 0, w, h, True)

