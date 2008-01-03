from viewers.Thumbnail import Thumbnail
import theme

import os

_PATH = os.path.dirname(__file__)



class VideoThumbnail(Thumbnail):
    
    def __init__(self, thumb, title):
    
        Thumbnail.__init__(self, 160, 120)
        self.add_image(theme.viewer_video_film)
        self.add_image(thumb, 13, 4, 134, 112)
        self.add_rect(0, 98, 160, 22, theme.color_bg_thumbnail_label, 0xa0)
        self.add_text(title, 2, 96, theme.font_tiny,
                      theme.color_fg_thumbnail_label)
        self.add_image(theme.btn_load, 128, 88)
