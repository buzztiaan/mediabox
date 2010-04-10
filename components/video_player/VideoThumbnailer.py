from com import Thumbnailer
from theme import theme


class VideoThumbnailer(Thumbnailer):
    """
    Thumbnailer for creating video thumbnails.
    """

    def __init__(self):
    
        Thumbnailer.__init__(self)
        
        
    def get_mime_types(self):
    
        return ["video/*"]


    def make_quick_thumbnail(self, f):

        f.frame = (theme.mb_frame_video, 14, 4, 134, 112)
        return ("", True)

