from com import Thumbnailer
from theme import theme

from threading import Thread
import os
import gtk
import gobject


class VideoThumbnailer(Thumbnailer):
    """
    Thumbnailer for creating video thumbnails.
    """

    def __init__(self):
    
        Thumbnailer.__init__(self)
        
        
    def get_mime_types(self):
    
        return ["video/*"]


    def make_quick_thumbnail(self, f):

        thumb = self._get_thumbnail(f)
        if (thumb):
            return (thumb, True)
        else:
            is_final = not f.is_local
            return ("", is_final)


    def make_thumbnail(self, f, cb, *args):

        t = Thread(target = self.__thumbnailer, args = (f, cb, args))
        t.start()


    def __thumbnailer(self, f, cb, args):

        os.system("totem-video-thumbnailer -j \"%s\" /tmp/videotn" \
                  % f.resource)
        gobject.timeout_add(0, self.__process_thumbnail, f, cb, args)


    def __process_thumbnail(self, f, cb, args):

        try:
            pbuf = gtk.gdk.pixbuf_new_from_file("/tmp/videotn")
            os.system("rm -f /tmp/videotn")
            cb(self._set_thumbnail(f, pbuf), *args)
            del pbuf
        except:
            cb("", *args)

