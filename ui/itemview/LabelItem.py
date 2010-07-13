from Item import Item
from theme import theme


class LabelItem(Item):

    def __init__(self, text):
    
        self.__icon = None
        self.__label = text
        self.__font = theme.font_mb_plain
        
        Item.__init__(self)
        
        
    def set_icon(self, icon):
    
        self.__icon = icon
        self._invalidate_cached_pixmap()


    def get_icon(self):
    
        return self.__icon

        
    def set_font(self, font):
    
        self.__font = font
        self._invalidate_cached_pixmap()
    
    
    def set_text(self, text):
    
        self.__label = text
        self._invalidate_cached_pixmap()
        
        
    def get_text(self):
    
        return self.__label
        
        
    def render_at(self, cnv, x, y):
    
        w, h = self.get_size()
    
        pmap, is_new = self._get_cached_pixmap()
        if (is_new):
            pmap.fill_area(0, 0, w, h, theme.color_mb_background)

            xpos = 4
            if (self.__icon):
                pmap.draw_pixbuf(self.__icon,
                                 4, (h - self.__icon.get_height()) / 2)
                xpos += self.__icon.get_width() + 16
            #end if

            pmap.set_clip_rect(xpos, 0, w - xpos, h)
            pmap.draw_formatted_text(self.__label, self.__font,
                                     xpos, 4, w - 4 - xpos, h - 8,
                                     theme.color_list_item_text)
            pmap.set_clip_rect()
        #end if
        
        # copy to the given canvas
        cnv.copy_buffer(pmap, 0, 0, x, y, w, h)

