from ui.Thumbnail import Thumbnail


class ItemThumbnail(Thumbnail):

    def __init__(self, thumb, f):

        Thumbnail.__init__(self)
        if (thumb):
            self.set_thumbnail(thumb)
        if (f):
            self.set_caption(f.name)
            self.set_mimetype(f.mimetype)

