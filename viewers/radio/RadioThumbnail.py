from viewers.Thumbnail import Thumbnail
import theme


class RadioThumbnail(Thumbnail):

    def __init__(self, thumb, title):
    
        self.__thumb = thumb
        self.__title = title
    
        Thumbnail.__init__(self, 160, 120)
        
        
    def _render_thumbnail(self):

        cnv = self.get_canvas()

        cnv.fill_area(0, 0, 160, 120, theme.color_bg)    

        cnv.fit_pixbuf(self.__thumb, 0, 0, 160, 120)

        cnv.draw_pixbuf(theme.caption_bg, 0, 98)
        cnv.draw_text(self.__title, theme.font_tiny, 2, 96,
                       theme.color_fg_thumbnail_label)
        cnv.draw_pixbuf(theme.btn_load, 128, 88)

