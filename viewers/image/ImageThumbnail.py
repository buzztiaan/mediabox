from viewers.Thumbnail import Thumbnail
import theme


class ImageThumbnail(Thumbnail):

    def __init__(self, thumb):
    
        Thumbnail.__init__(self, 160, 120)
        self.fill(0xff, 0xff, 0xff)
        self.add_image(thumb, 3, 3, 154, 114)
        self.add_image(theme.btn_load, 128, 48)
        
