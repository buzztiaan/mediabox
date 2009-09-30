from Item import Item
from theme import theme


class CheckBoxItem(Item):

    EVENT_CHECKED = "event-checked"


    def __init__(self, text, is_checked):
    
        self.__label = text
        self.__is_checked = is_checked
        
        Item.__init__(self)
        
        
    def render_at(self, cnv, x, y):
    
        w, h = self.get_size()
    
        pmap, is_new = self._get_cached_pixmap()
        if (is_new):
            pmap.fill_area(0, 0, w, h, theme.color_mb_background)

            if (self.__is_checked):
                pbuf = theme.mb_checkbox_2
            else:
                pbuf = theme.mb_checkbox_1

            pmap.draw_pixbuf(pbuf, 4, 4)

            pmap.set_clip_rect(5, 5, w - 10, h - 10)
            pmap.draw_text(self.__label, theme.font_mb_tiny,
                           pbuf.get_width() + 10, 10,
                           theme.color_mb_listitem_text)
            pmap.set_clip_rect()
        #end if
        
        # copy to the given canvas
        cnv.copy_buffer(pmap, 0, 0, x, y, w, h)


    def connect_checked(self, cb, *args):
    
        self._connect(self.EVENT_CHECKED, cb, *args)


    def click_at(self, px, py):
    
        self.__is_checked = not self.__is_checked
        self._invalidate_cached_pixmap()

        self.emit_event(self.EVENT_CHECKED, self.__is_checked)

