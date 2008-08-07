from ui.Thumbnail import Thumbnail


class FileThumbnail(Thumbnail):

    def __init__(self, thumb, f):

        Thumbnail.__init__(self)
        self.set_thumbnail(thumb)
        self.set_caption(f.name)
        self.set_mimetype(f.mimetype)
