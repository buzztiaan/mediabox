from com import Thumbnailer, msgs
from mediabox.OrgFreeDesktopThumbnailer import OrgFreeDesktopThumbnailer
import platforms
from utils import urlquote
from utils import logging
from theme import theme

import gtk


class OrgFreeDesktopImageThumbnailer(Thumbnailer):
    """
    Image thumbnailer that uses the org.freedesktop.thumbnailer service.
    """

    def __init__(self):

        self.__thumbnailer = OrgFreeDesktopThumbnailer()
    
        Thumbnailer.__init__(self)


    def get_mime_types(self):
    
        return ["image/*",
                "application/x-image-folder"]


    def make_quick_thumbnail(self, f):

        if (f.mimetype == "application/x-image-folder"):
            f.frame = (theme.mb_frame_image_album, 13, 12, 148, 143)
        else:
            f.frame = (theme.mb_frame_image, 5, 5, 150, 150)
    
        thumb = self._get_thumbnail(f)
        if (thumb):
            return (thumb, True)
        else:
            is_final = not f.is_local
            return ("", is_final)


    def make_thumbnail(self, f, cb, *args):
    
        if (f.mimetype == "application/x-image-folder"):
            c = f.get_children()[0]
            res = c.resource
            mimetype = c.mimetype
        else:
            res = f.resource
            mimetype = f.mimetype
            
        uri = "file://" + urlquote.quote(res)
        print "thumbnailing image", f, mimetype
        self.__thumbnailer.queue(uri, [mimetype], self.__on_finish,
                                 f, cb, args)


    def __on_finish(self, thumbpath, f, cb, args):
    
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

