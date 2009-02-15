from ui.Thumbnail import Thumbnail
from ui.Pixmap import Pixmap
from theme import theme

import os
import gtk
import urllib


class DeviceThumbnail(Thumbnail):

    def __init__(self, dev):

        title = dev.get_name()
        try:
            thumb = dev.get_icon() or theme.mb_device_unknown
        except:
            thumb = theme.mb_device_unknown
            
        Thumbnail.__init__(self)
        self.set_thumbnail_pbuf(thumb)
        self.set_caption(title)

