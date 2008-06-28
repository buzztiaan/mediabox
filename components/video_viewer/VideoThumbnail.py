from ui.StripItem import StripItem
import theme

import os
import gtk

_PATH = os.path.dirname(__file__)



class VideoThumbnail(StripItem):

    def __init__(self, thumb, title):

        self.__thumb = thumb
        self.__title = title
        StripItem.__init__(self)
        self.set_size(160, 120)
        
        
    def render_this(self, cnv):

        cnv.draw_pixbuf(theme.viewer_video_film, 0, 0)
        try:
            cnv.fit_pixbuf(gtk.gdk.pixbuf_new_from_file(self.__thumb), 13, 4, 134, 112)
        except:
            pass

        if (self.is_hilighted()):
            cnv.draw_pixbuf(theme.selection_frame, 0, 0)

        cnv.draw_pixbuf(theme.caption_bg, 0, 98)
        cnv.draw_text(self.__title, theme.font_tiny, 2, 96,
                       theme.color_fg_thumbnail_label)
        cnv.draw_pixbuf(theme.btn_load, 128, 88)
