from viewers.Thumbnail import Thumbnail
import theme

import os
import gtk

_PATH = os.path.dirname(__file__)


class VideoThumbnail(Thumbnail):
    
    def __init__(self, thumb, title):
    
        self.__thumb = thumb
        self.__title = title
        Thumbnail.__init__(self, 160, 120)
        
        
    def _render_thumbnail(self):
    
        cnv = self.get_canvas()
    
        cnv.draw_pixbuf(theme.viewer_video_film, 0, 0)
        try:
            cnv.fit_pixbuf(gtk.gdk.pixbuf_new_from_file(self.__thumb), 13, 4, 134, 112)
        except:
            pass

        cnv.draw_pixbuf(theme.caption_bg, 0, 98)
        cnv.draw_text(self.__title, theme.font_tiny, 2, 96,
                       theme.color_fg_thumbnail_label)
        cnv.draw_pixbuf(theme.btn_load, 128, 88)

        #self.add_image(theme.viewer_video_film)
        #self.add_image(thumb, 13, 4, 134, 112)
        #self.add_rect(0, 98, 160, 22, theme.color_bg_thumbnail_label, 0xa0)
        #self.add_text(title, 2, 96, theme.font_tiny,
        #              theme.color_fg_thumbnail_label)
        #self.add_image(theme.btn_load, 128, 88)

