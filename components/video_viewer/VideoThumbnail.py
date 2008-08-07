from ui.Thumbnail import Thumbnail
from mediabox import thumbnail
import theme

import os
import gtk

_PATH = os.path.dirname(__file__)



class VideoThumbnail(Thumbnail):

    def __init__(self, thumb, title):

        Thumbnail.__init__(self)
        self.set_thumbnail(thumb)
        self.set_caption(title)
        self.set_mimetype("video/*")
