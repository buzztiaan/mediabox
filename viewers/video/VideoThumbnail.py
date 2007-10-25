from viewers.Thumbnail import Thumbnail
import theme

import os

_PATH = os.path.dirname(__file__)



class VideoThumbnail(Thumbnail):

    def __init__(self, thumb, title):
    
        Thumbnail.__init__(self, 160, 120)
        self.add_image(os.path.join(_PATH, "film.png"))
        self.add_image(thumb, 13, 4, 134, 112)
        self.add_text(title, 3, 111, theme.font_tiny, "#000000")
        self.add_text(title, 2, 110, theme.font_tiny, "#ffffff")
        self.add_image(theme.btn_load, 136, 48)
