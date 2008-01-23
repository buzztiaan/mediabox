from viewers.Thumbnail import Thumbnail
import theme

import os


class AlbumThumbnail(Thumbnail):

    def __init__(self, thumb, title):
    
        Thumbnail.__init__(self, 160, 120)
        self.fill_color(theme.color_bg)

        if (os.path.exists(thumb)):
            self.add_image(theme.viewer_music_frame, 20, 0)
            self.add_image(thumb, 23, 3, 109, 109)

        else:
            self.add_image(theme.viewer_music_unknown, 0, 0, 160, 120)

        self.add_rect(0, 98, 160, 22, theme.color_bg_thumbnail_label, 0xa0)
        self.add_text(title, 2, 96, theme.font_tiny,
                      theme.color_fg_thumbnail_label)            
        self.add_image(theme.btn_load, 128, 88)
