from ui.Thumbnail import Thumbnail
from ui.Pixmap import Pixmap
from mediabox import thumbnail
import theme

import os
import gtk


class AlbumThumbnail(Thumbnail):

    def __init__(self, thumb, title):

        Thumbnail.__init__(self)
        self.set_thumbnail(thumb)
        self.set_caption(title)
        self.set_size(160, 120)
        self.set_mimetype("audio/x-music-folder")
