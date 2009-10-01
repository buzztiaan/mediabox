from com import Thumbnailer
from theme import theme


class AudioThumbnailer(Thumbnailer):

    def __init__(self):
    
        Thumbnailer.__init__(self)
        
        
    def get_mime_types(self):
    
        return ["audio/*",
                "application/ogg",
                "application/x-music-folder"]


    def make_quick_thumbnail(self, f):
    
        return (theme.mb_filetype_audio.get_path(), True)

