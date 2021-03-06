from com import Thumbnailer, msgs
from io.Downloader import Downloader
from mediabox import imageloader
from theme import theme

import base64


class YouTubeThumbnailer(Thumbnailer):
    """
    Thumbnailer for YouTube videos.
    """

    def __init__(self):
    
        Thumbnailer.__init__(self)
        
        
    def get_mime_types(self):
    
        return ["video/x-youtube-video"]


    def make_quick_thumbnail(self, f):
    
        f.frame = (theme.mb_frame_video, 9, 5, 142, 150)
        return (theme.mb_default_video.get_path(), False)


    def make_thumbnail(self, f, cb, *args):
    
        def on_download(d, amount, total, data):
            if (d):
                data[0] += d
            else:
                cb("data://" + base64.b64encode(data[0]))

    
        dl = Downloader(f.thumbnailer_param, on_download, [""])

