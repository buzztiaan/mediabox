from ui.StripItem import StripItem
from mediabox import thumbnail
import theme

import os
import gtk

_PATH = os.path.dirname(__file__)



class VideoThumbnail(StripItem):

    def __init__(self, thumb, title):

        self.__thumb = thumb
        self.__title = title
        StripItem.__init__(self)
        self.set_size(160, 120)
        
        
    def render_this(self, cnv):

        cnv.fill_area(0, 0, 160, 120, theme.color_bg)
        thumbnail.draw_decorated(cnv, 0, 0, 160, 120, self.__thumb, "video/*")

        if (self.is_hilighted()):
            cnv.draw_pixbuf(theme.mb_selection_frame, 0, 0)

        cnv.draw_pixbuf(theme.mb_caption_bg, 0, 98)
        cnv.draw_text(self.__title, theme.font_tiny, 2, 96,
                       theme.color_fg_thumbnail_label)
        cnv.draw_pixbuf(theme.btn_load, 128, 88)

