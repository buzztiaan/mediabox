from ui.StripItem import StripItem
from mediabox import thumbnail
import theme

import gtk


class ImageThumbnail(StripItem):

    def __init__(self, thumb):
    
        self.__thumb = thumb
        
        StripItem.__init__(self)
        self.set_size(160, 120)
        
        
    def render_this(self, cnv):
    
        cnv.fill_area(0, 0, 160, 120, theme.color_bg)
        thumbnail.draw_decorated(cnv, 0, 0, 160, 120, self.__thumb, "image/*")

        if (self.is_hilighted()):
            cnv.draw_pixbuf(theme.mb_selection_frame, 0, 0)
        
        cnv.draw_pixbuf(theme.btn_load, 128, 88)
