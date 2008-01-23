from viewers.Thumbnail import Thumbnail
import theme


class ImageThumbnail(Thumbnail):

    def __init__(self, thumb):
    
        Thumbnail.__init__(self, 160, 120)
        self.fill_color(theme.color_bg)
        self.add_image(theme.viewer_image_frame, 0, 0)
        #self.add_image(thumb, 3, 3, 154, 114)
        self.add_image(thumb, 7, 7, 142, 102)
        self.add_image(theme.btn_load, 128, 48)
