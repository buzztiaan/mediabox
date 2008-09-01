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
        self.__emblem = None
        self.__caption = ""
        self.__mimetype = ""
    
        StripItem.__init__(self)
        self.set_size(160, 110)
        self.set_selection_frame(theme.mb_selection_frame)
        
        
    def set_thumbnail(self, path):
    
        self.__thumb = path
        
        
    def set_thumbnail_pbuf(self, pbuf):
    
        self.__thumb_pbuf = pbuf
        
        
    def set_emblem(self, pbuf):
    
        self.__emblem = pbuf
        
        
    def set_caption(self, text):
    
        self.__caption = text
        
        
    def set_mimetype(self, mimetype):
    
        self.__mimetype = mimetype
        
        
    def render_this(self, cnv):

        cnv.fill_area(0, 0, 160, 110, theme.color_bg)

        if (self.__thumb):
            thumbnail.draw_decorated(cnv, 4, 4, 152, 102,
                                     self.__thumb, self.__mimetype)
        elif (self.__thumb_pbuf):
            cnv.fit_pixbuf(self.__thumb_pbuf, 4, 4, 152, 102)

        if (self.__emblem):
            cnv.fit_pixbuf(self.__emblem, 4, 4, 32, 32)

        self.render_selection_frame(cnv)

        if (self.__caption):
            cnv.draw_pixbuf(theme.mb_caption_bg, 0, 88)
            cnv.draw_text(self.__caption, theme.font_tiny, 2, 86,
                          theme.color_fg_thumbnail_label)

        if (not self.is_hilighted()):
            cnv.draw_pixbuf(theme.mb_btn_load, 128, 78)

