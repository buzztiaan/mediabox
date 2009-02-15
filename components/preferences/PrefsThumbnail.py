from ui.Thumbnail import Thumbnail


class PrefsThumbnail(Thumbnail):

    def __init__(self, thumb, title):

        Thumbnail.__init__(self)
        self.set_thumbnail_pbuf(thumb)
        self.set_caption(title)

