from ui.StripItem import StripItem
import theme

import gtk


class ImageThumbnail(StripItem):

    def __init__(self, thumb):
    
        self.__thumb = thumb
        
        StripItem.__init__(self)
        self.set_size(160, 120)
        
        
    def render_this(self, cnv):
    
        cnv.fill_area(0, 0, 160, 120, theme.color_bg)

        cnv.draw_pixbuf(theme.viewer_image_frame, 0, 0)
        try:
            cnv.fit_pixbuf(gtk.gdk.pixbuf_new_from_file(self.__thumb),
                           7, 7, 142, 102)
        except:
            pass

        if (self.is_hilighted()):
            cnv.draw_pixbuf(theme.selection_frame, 0, 0)
        
        cnv.draw_pixbuf(theme.btn_load, 128, 88)
