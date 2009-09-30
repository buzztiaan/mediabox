from ui.itemview import Item
from theme import theme


class ThemeListItem(Item):
    """
    List item for themes.
    """

    EVENT_CLICKED = "event-clicked"


    def __init__(self, preview, name, info, author):

        self.__preview = preview
        self.__label = name #self.escape_xml(name)
        self.__info = info #self.escape_xml(info)
        self.__author = author #self.escape_xml(author)

        Item.__init__(self)


    def get_preview(self):
    
        return self.__preview


    def render_at(self, cnv, x, y):
    
        w, h = self.get_size()
        
        pmap, is_new = self._get_cached_pixmap()
        if (is_new):        
            pmap.fill_area(0, 0, w, h, theme.color_mb_background)

            icon_y = (h - self.__preview.get_height()) / 2
            pmap.draw_pixbuf(self.__preview, 8, icon_y)

            info = self.__info
            if (self.__author):
                info += "\nby " + self.__author

            pmap.set_clip_rect(0, 0, w, h)
            pmap.draw_text(self.__label, theme.font_mb_listitem,
                            128, 10, theme.color_mb_listitem_text)
            pmap.draw_text(info, theme.font_mb_listitem,
                            128, 30, theme.color_mb_listitem_subtext)
            pmap.set_clip_rect()
        #end if

        # copy to the given canvas
        cnv.copy_buffer(pmap, 0, 0, x, y, w, h)


    def connect_clicked(self, cb, *args):
    
        self._connect(self.EVENT_CLICKED, cb, *args)
        
        
        
    def click_at(self, px, py):
    
        w, h = self.get_size()
        if (px >= w - 80):
            print "CLICK"
            self.emit_event(self.EVENT_CLICKED)
        
