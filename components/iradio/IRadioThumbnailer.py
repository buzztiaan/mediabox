from com import Thumbnailer, msgs
from io.Downloader import Downloader
from mediabox import imageloader
from theme import theme

import base64


class IRadioThumbnailer(Thumbnailer):
    """
    Thumbnailer for internet radio stations.
    """

    def __init__(self):
    
        Thumbnailer.__init__(self)
        
        
    def get_mime_types(self):
    
        return []


    def make_quick_thumbnail(self, f):

        f.frame = (theme.iradio_frame, 86, 64, 48, 48)
        return ("", False)


    def make_thumbnail(self, f, cb, *args):
    
        def on_download(d, amount, total, data):
            if (d):
                data[0] += d
            elif (d == None):
                cb("", *args)
            else:
                cb("data://" + base64.b64encode(data[0]), *args)

        fqdn = self.__extract_fqdn(f.thumbnailer_param)
        favicon = fqdn + "/favicon.ico"
        dl = Downloader(favicon, on_download, [""])


    def __extract_fqdn(self, url):
    
        idx1 = url.find("://")
        idx2 = url.find("/", idx1 + 3)
        if (idx2 == -1):
            return url
        else:
            return url[:idx2]

