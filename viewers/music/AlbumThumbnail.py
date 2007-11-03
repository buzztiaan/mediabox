from viewers.Thumbnail import Thumbnail
import theme

import os


class AlbumThumbnail(Thumbnail):

    def __init__(self, thumb, title):
    
        Thumbnail.__init__(self, 160, 120)
        self.fill(0xff, 0xff, 0xff)
        if (os.path.exists(thumb)):
            self.add_image(thumb, 0, 0, 160, 120)
        else:
            self.add_image(theme.viewer_music_unknown, 0, 0, 160, 120)
        self.add_rect(0, 104, 160, 16, 0x44, 0x44, 0xff, 0xa0)
        self.add_text(title, 2, 103, theme.font_tiny, "#ffffff")            
        self.add_image(theme.btn_load, 128, 88)
