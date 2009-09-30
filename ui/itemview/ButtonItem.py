from Item import Item
from theme import theme


class ButtonItem(Item):

    EVENT_CLICKED = "event-clicked"


    def __init__(self, text):
    
        self.__label = text
        
        Item.__init__(self)
        
        
    def render_at(self, cnv, x, y):
    
        w, h = self.get_size()
    
        pmap, is_new = self._get_cached_pixmap()
        if (is_new):
            pmap.fill_area(0, 0, w, h, theme.color_mb_background)

            pmap.draw_frame(theme.mb_button_1, 4, 4, w - 8, h - 8,
                            pmap.TOP | pmap.BOTTOM |
                            pmap.LEFT | pmap.RIGHT)

            pmap.set_clip_rect(5, 5, w - 10, h - 10)
            pmap.draw_centered_text(self.__label, theme.font_mb_tiny,
                                    0, 0, w, h,
                                    theme.color_mb_listitem_text)
            pmap.set_clip_rect()
        #end if
        
        # copy to the given canvas
        cnv.copy_buffer(pmap, 0, 0, x, y, w, h)


    def connect_clicked(self, cb, *args):
    
        self._connect(self.EVENT_CLICKED, cb, *args)


    def click_at(self, px, py):
    
        self.emit_event(self.EVENT_CLICKED)

