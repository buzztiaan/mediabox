from Item import Item
from theme import theme


class LabelItem(Item):

    def __init__(self, text):
    
        self.__label = text
        self.__font = theme.font_mb_plain
        
        Item.__init__(self)
        
        
    def set_font(self, font):
    
        self.__font = font
        self._invalidate_cached_pixmap()
    
    
    def set_text(self, text):
    
        self.__label = text
        self._invalidate_cached_pixmap()
        
        
    def render_at(self, cnv, x, y):
    
        w, h = self.get_size()
    
        pmap, is_new = self._get_cached_pixmap()
        if (is_new):
            pmap.fill_area(0, 0, w, h, theme.color_mb_background)

            pmap.set_clip_rect(0, 0, w, h)
            pmap.draw_formatted_text(self.__label, self.__font,
                                     4, 4, w - 8, h - 8,
                                     theme.color_list_item_text)
            pmap.set_clip_rect()
        #end if
        
        # copy to the given canvas
        cnv.copy_buffer(pmap, 0, 0, x, y, w, h)

