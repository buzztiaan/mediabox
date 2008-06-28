from ui.StripItem import StripItem
from ui.Pixmap import Pixmap
import theme

import os
import gtk


class AlbumThumbnail(StripItem):

    def __init__(self, thumb, title):

        self.__thumb = thumb
        self.__title = title        
               
        StripItem.__init__(self)
        self.set_size(160, 120)
        
        
    def render_this(self, cnv):

        cnv.fill_area(0, 0, 160, 120, theme.color_bg)

        if (os.path.exists(self.__thumb)):
            cnv.draw_pixbuf(theme.viewer_music_frame, 20, 0)
            try:
                cnv.fit_pixbuf(gtk.gdk.pixbuf_new_from_file(self.__thumb),
                               23, 3, 109, 109)
            except:
                pass

        else:
            cnv.fit_pixbuf(theme.viewer_music_unknown, 0, 0, 160, 120)

        if (self.is_hilighted()):
            cnv.draw_pixbuf(theme.selection_frame, 0, 0)

        cnv.draw_pixbuf(theme.caption_bg, 0, 98)
        cnv.draw_text(self.__title, theme.font_tiny, 2, 96,
                       theme.color_fg_thumbnail_label)
        cnv.draw_pixbuf(theme.btn_load, 128, 88)
