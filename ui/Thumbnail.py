from StripItem import StripItem
from mediabox import thumbnail
import theme


class Thumbnail(StripItem):
    """
    Base class for thumbnail items.
    """
    
    def __init__(self):
    
        self.__thumb = ""
        self.__thumb_pbuf = None
        self.__caption = ""
        self.__mimetype = ""
    
        StripItem.__init__(self)
        self.set_selection_frame(theme.mb_selection_frame)
        
        
    def set_thumbnail(self, path):
    
        self.__thumb = path
        
        
    def set_thumbnail_pbuf(self, pbuf):
    
        self.__thumb_pbuf = pbuf
        
        
    def set_caption(self, text):
    
        self.__caption = text
        
        
    def set_mimetype(self, mimetype):
    
        self.__mimetype = mimetype
        
        
    def render_this(self, cnv):

        cnv.fill_area(0, 0, 160, 120, theme.color_bg)

        if (self.__thumb):
            thumbnail.draw_decorated(cnv, 4, 4, 152, 112,
                                     self.__thumb, self.__mimetype)
        elif (self.__thumb_pbuf):
            cnv.fit_pixbuf(self.__thumb_pbuf, 4, 4, 152, 112)


        self.render_selection_frame(cnv)

        if (self.__caption):
            cnv.draw_pixbuf(theme.mb_caption_bg, 0, 98)
            cnv.draw_text(self.__caption, theme.font_tiny, 2, 96,
                          theme.color_fg_thumbnail_label)

        if (not self.is_hilighted()):
            cnv.draw_pixbuf(theme.btn_load, 128, 88)

