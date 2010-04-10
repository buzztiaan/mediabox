from com import Thumbnailer, msgs
from io.Downloader import Downloader
from utils import imageloader
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
    
        #thumb = self._get_thumbnail(f)
        #if (thumb):
        #    return (thumb, True)
        #else:
        f.frame = (theme.mb_frame_video, 14, 4, 134, 112)
        return ("", False)


    def make_thumbnail(self, f, cb, *args):
    
        def on_download(d, amount, total, data):
            if (d):
                data[0] += d
            else:
                cb("data://" + base64.b64encode(data[0]))
                #imageloader.load_data(data[0], on_image)
    
        #def on_image(pbuf):
        #    if (pbuf):
        #        path = self._set_thumbnail(f, pbuf)
        #    else:
        #        path = ""
        #    cb(path, *args)

    
        dl = Downloader(f.thumbnailer_param, on_download, [""])
        
