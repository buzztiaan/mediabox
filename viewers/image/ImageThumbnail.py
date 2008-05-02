from viewers.Thumbnail import Thumbnail
import theme

import gtk


class ImageThumbnail(Thumbnail):

    def __init__(self, thumb):
    
        self.__thumb = thumb
        
        Thumbnail.__init__(self, 160, 120)
        
        
    def _render_thumbnail(self):
    
        cnv = self.get_canvas()
        
        cnv.fill_area(0, 0, 160, 120, theme.color_bg)

        cnv.draw_pixbuf(theme.viewer_image_frame, 0, 0)
        try:
            cnv.fit_pixbuf(gtk.gdk.pixbuf_new_from_file(self.__thumb),
                           7, 7, 142, 102)
        except:
            pass
        
        cnv.draw_pixbuf(theme.btn_load, 128, 88)
