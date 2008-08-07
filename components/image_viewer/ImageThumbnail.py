from ui.Thumbnail import Thumbnail
from mediabox import thumbnail
import theme

import gtk


class ImageThumbnail(Thumbnail):

    def __init__(self, thumb):
    
        Thumbnail.__init__(self)
        self.set_thumbnail(thumb)
        self.set_mimetype("image/*")

