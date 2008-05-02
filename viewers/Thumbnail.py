from ui.SharedPixmap import SharedPixmap
import theme


class Thumbnail(object):
    """
    Base class for thumbnail images. Viewers subclass this class for their
    thumbnails.
    """

    __canvas = SharedPixmap(160, 120)

    def __init__(self, width = 160, height = 120):

        self.__hilighted = False

        self.__canvas.set_renderer(self, lambda x:self.render())
        #SharedPixmap.__init__(self, width, height)
        #self.set_renderer(self, lambda x:self._render_thumbnail())
        #self._render_thumbnail()


    def get_canvas(self):
    
        return self.__canvas
        
        
    def get_size(self):
    
        return self.__canvas.get_size()        


    def get_pixmap(self):
    
        self.__canvas.prepare(self)
        return self.__canvas


    def _render_thumbnail(self):
    
        raise NotImplementedError


    def render(self):

        self.__canvas.invalidate_cache(self)
        self._render_thumbnail()

        if (self.__hilighted):            
            self.__canvas.draw_pixbuf(theme.selection_frame, 0, 0)

    def set_hilighted(self, value):
    
        if (value != self.__hilighted):
            self.__hilighted = value
            self.render() #_render_thumbnail()


