from ui.itemview import Item
from theme import theme


_READABLE_NAMES = {
    "xine": "Xine (experimental)",
    "gst": "GStreamer",
    "mafw": "MAFW",
    "oms": "OSSO Media Server",
    "mplayer": "MPlayer",
    "simulated": "Simulator (just for testing)"
}


class BackendListItem(Item):
    """
    List item for player backends.
    """

    def __init__(self, mediatype, backend):

        self.__icon = None
        self.__mediatype = mediatype
        self.__backend = backend        
        
        Item.__init__(self)


    def set_backend_icon(self, icon):
    
        self.__icon = icon
        self._invalidate_cached_pixmap()


    def get_media_type(self):
    
        return self.__mediatype


    def get_backend(self):
    
        return self.__backend
        
        
    def set_backend(self, backend):
    
        self.__backend = backend
        self._invalidate_cached_pixmap()


    def render_at(self, cnv, x, y):
    
        w, h = self.get_size()
        
        pmap, is_new = self._get_cached_pixmap()
        if (is_new):
            pmap.fill_area(0, 0, w, h, theme.color_mb_background)

            if (self.__icon):
                icon_y = (h - self.__icon.get_height()) / 2
                pmap.draw_pixbuf(self.__icon, 24, icon_y)

            name = _READABLE_NAMES.get(self.__backend, self.__backend)
            pmap.set_clip_rect(0, 0, w, h)
            pmap.draw_text(self.__mediatype, theme.font_mb_plain,
                           128, 2, theme.color_list_item_text)
            pmap.draw_text("played with " + name, theme.font_mb_tiny,
                            128, 30, theme.color_list_item_subtext)
            pmap.set_clip_rect()
        #end if

        # copy to the given canvas
        cnv.copy_buffer(pmap, 0, 0, x, y, w, h)

