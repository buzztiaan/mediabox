from ui.ButtonListItem import ButtonListItem
from theme import theme


_READABLE_NAMES = {
    "xine": "Xine (experimental)",
    "gst": "GStreamer (experimental)",
    "oms": "OSSO Media Server",
    "mplayer": "MPlayer"
}


class BackendListItem(ButtonListItem):
    """
    List item for player backends.
    """

    BUTTON_PLAY = "play"


    def __init__(self, mediatype, backend):

        self.__icon = None
        self.__mediatype = mediatype
        self.__backend = backend        
        
        ButtonListItem.__init__(self)
        self.set_colors(theme.color_mb_listitem_text, theme.color_mb_listitem_subtext)
        self.set_font(theme.font_mb_tiny)

        self.set_buttons((self.BUTTON_PLAY, theme.mb_item_btn_play))


    def set_backend_icon(self, icon):
    
        self.__icon = icon


    def get_media_type(self):
    
        return self.__mediatype


    def get_backend(self):
    
        return self.__backend
        
        
    def set_backend(self, backend):
    
        self.__backend = backend


    def render_this(self, cnv):
    
        self.render_bg(cnv)

        w, h = self.get_size()
        if (self.__icon):
            icon_y = (h - self.__icon.get_height()) / 2
            cnv.draw_pixbuf(self.__icon, 24, icon_y)

        name = _READABLE_NAMES.get(self.__backend, self.__backend)
        self.render_label(cnv, 112, self.__mediatype,
                          "played with " + name)
        self.render_buttons(cnv)

