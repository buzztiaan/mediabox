from com import Thumbnailer, msgs
from mediabox.OrgFreeDesktopThumbnailer import OrgFreeDesktopThumbnailer
import platforms
#from ui import pixbuftools
from utils import urlquote
from utils import logging
from theme import theme

import gtk



class OrgFreeDesktopVideoThumbnailer(Thumbnailer):
    """
    Video thumbnailer that uses the org.freedesktop.thumbnailer service.
    """

    def __init__(self):

        self.__thumbnailer = OrgFreeDesktopThumbnailer()
    
        Thumbnailer.__init__(self)


    def get_mime_types(self):
    
        return ["video/*"]


    def make_quick_thumbnail(self, f):

        f.frame = (theme.mb_frame_video, 9, 5, 142, 150)
    
        thumb = self._get_thumbnail(f)
        if (thumb):
            return (thumb, True)
        else:
            is_final = not f.is_local
            return (theme.mb_default_video.get_path(), is_final)


    def make_thumbnail(self, f, cb, *args):
    
        self.call_service(msgs.VIDEOPLAYER_SVC_LOCK_DSP)

        uri = "file://" + urlquote.quote(f.resource)
        self.__thumbnailer.queue(uri, ["video/mp4"], self.__on_finish,
                                 f, cb, args)


    def __on_finish(self, thumbpath, f, cb, args):
    
        self.call_service(msgs.VIDEOPLAYER_SVC_RELEASE_DSP)

        try:
            path = self.__save_thumbnail(f, thumbpath)
        except:
            #print logging.stacktrace()
            path = ""

        cb(path, *args)


    def __save_thumbnail(self, f, thumbpath):
    
        #thumb = theme.mb_frame_video.copy()
        pbuf = gtk.gdk.pixbuf_new_from_file(thumbpath)
        #pixbuftools.fit_pbuf(thumb, pbuf, 14, 4, 134, 112)
        
        return self._set_thumbnail(f, pbuf)

