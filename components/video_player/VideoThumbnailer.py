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
    
        return (theme.mb_file_video.get_path(), True)

