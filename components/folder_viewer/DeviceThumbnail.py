from ui.StripItem import StripItem
from ui.Pixmap import Pixmap
import theme

import os
import gtk
import urllib


class DeviceThumbnail(StripItem):

    def __init__(self, dev):

        self.__title = dev.get_name()
        self.__icon = dev.get_icon() or theme.viewer_upnp_device
        
        StripItem.__init__(self)
        self.set_size(160, 120)
        
        
    def render_this(self, cnv):

        cnv.fill_area(0, 0, 160, 120, theme.color_bg)

        if (self.__icon):
            cnv.fit_pixbuf(self.__icon, 0, 0, 160, 120)

        if (self.is_hilighted()):
            cnv.draw_pixbuf(theme.selection_frame, 0, 0)

        cnv.draw_pixbuf(theme.caption_bg, 0, 98)
        cnv.draw_text(self.__title, theme.font_tiny, 2, 96,
                       theme.color_fg_thumbnail_label)
        cnv.draw_pixbuf(theme.btn_load, 128, 88)

