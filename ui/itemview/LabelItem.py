from Item import Item
from theme import theme


class LabelItem(Item):

    def __init__(self, text):
    
        self.__label = text
        
        Item.__init__(self)
        
        
    def render_at(self, cnv, x, y):
    
        w, h = self.get_size()
    
        pmap, is_new = self._get_cached_pixmap()
        if (is_new):
            pmap.fill_area(0, 0, w, h, theme.color_mb_background)

            pmap.set_clip_rect(0, 0, w, h)
            pmap.draw_text(self.__label, theme.font_mb_tiny,
                           10, 10,
                           theme.color_mb_listitem_text)
            pmap.set_clip_rect()
        #end if
        
        # copy to the given canvas
        cnv.copy_buffer(pmap, 0, 0, x, y, w, h)

