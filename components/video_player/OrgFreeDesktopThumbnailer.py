from com import Thumbnailer
import platforms
from ui import pixbuftools
from utils import urlquote
from utils import logging
from theme import theme

import gtk
import dbus
import hashlib
import os


_THUMBNAILER_SERVICE = "org.freedesktop.thumbnailer"
_THUMBNAILER_PATH = "/org/freedesktop/thumbnailer/Generic"
_THUMBNAILER_INTERFACE = "org.freedesktop.thumbnailer.Generic"


class OrgFreeDesktopThumbnailer(Thumbnailer):
    """
    Video thumbnailer that uses the org.freedesktop.thumbnailer service.
    """

    def __init__(self):
    
        # table: handle -> (uri, f, cb, args)
        self.__handles = {}
    
        Thumbnailer.__init__(self)
        
        bus = platforms.get_session_bus()
        obj = bus.get_object(_THUMBNAILER_SERVICE, _THUMBNAILER_PATH)
        self.__thumbnailer = dbus.Interface(obj, _THUMBNAILER_INTERFACE)
        
        self.__thumbnailer.connect_to_signal("Finished", self.__on_finish)
        self.__thumbnailer.connect_to_signal("Error", self.__on_error)
   
    
        
        
    def get_mime_types(self):
    
        return ["video/*"]


    def make_quick_thumbnail(self, f):
    
        thumb = self._get_thumbnail(f)
        if (thumb):
            return (thumb, True)
        else:
            is_final = not f.is_local
            return (theme.mb_frame_video.get_path(), is_final)


    def make_thumbnail(self, f, cb, *args):
    
        uri = "file://" + urlquote.quote(f.resource)
        handle = self.__thumbnailer.Queue([uri], ["video/mp4"], 0)
        self.__handles[handle] = (uri, f, cb, args)
        print "Got Handle", handle, "for", uri


    def __on_finish(self, handle):
    
        print "finished thumbnailing", handle
        try:
            uri, f, cb, args = self.__handles[handle]
            del self.__handles[handle]
            thumbpath = self.__get_osso_thumbnail(uri)
            path = self.__save_thumbnail(f, thumbpath)
            cb(path, *args)
        except:
            print logging.stacktrace()
            pass

        
    def __on_error(self, handle, failed_uris, err, err_msg):
    
        print "Thumbnailing failed for", handle, failed_uris, err_msg
        try:
            uri, f, cb, args = self.__handles[handle]
            del self.__handles[handle]
            cb("", *args)
        except:
            pass


    def __get_osso_thumbnail(self, uri):
    
        name = hashlib.md5(uri).hexdigest()
        thumb_dir = os.path.expanduser("~/.thumbnails/cropped")
        thumb_uri = os.path.join(thumb_dir, name + ".jpeg")

        return thumb_uri


    def __save_thumbnail(self, f, thumbpath):
    
        thumb = theme.mb_frame_video.copy()
        pbuf = gtk.gdk.pixbuf_new_from_file(thumbpath)
        pixbuftools.fit_pbuf(thumb, pbuf, 14, 4, 134, 112)
        
        return self._set_thumbnail(f, thumb)

