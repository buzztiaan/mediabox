from ui.itemview.Item import Item
from theme import theme


class PrefsItem(Item):

    EVENT_CLICKED = "event-clicked"
    

    def __init__(self, configurator):
    
        self.__configurator = configurator
    
        Item.__init__(self)
        self.set_size(120, 120)


    def render_at(self, cnv, x, y):

        w, h = self.get_size()

        pmap, is_new = self._get_cached_pixmap()
        if (is_new):
            pmap.fill_area(0, 0, w, h, theme.color_mb_background)
            pmap.fit_pixbuf(self.__configurator.ICON, 10, 10, w - 20, h - 30)
            pmap.draw_centered_text(self.__configurator.TITLE,
                                    theme.font_mb_listitem,
                                    10, h - 26, w - 20, 20,
                                    theme.color_mb_listitem_text)
        #end if

        # copy to the given canvas
        cnv.copy_buffer(pmap, 0, 0, x, y, w, h)


    def connect_clicked(self, cb, *args):
    
        self._connect(self.EVENT_CLICKED, cb, *args)
        
        
    def click_at(self, px, py):
    
        self.emit_event(self.EVENT_CLICKED)

