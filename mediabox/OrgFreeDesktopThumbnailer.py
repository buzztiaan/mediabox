import platforms

import gobject
import dbus
import hashlib
import os


_THUMBNAILER_SERVICE = "org.freedesktop.thumbnailer"
_THUMBNAILER_PATH = "/org/freedesktop/thumbnailer/Generic"
_THUMBNAILER_INTERFACE = "org.freedesktop.thumbnailer.Generic"

# thumbnailer timeout in milliseconds
_TIMEOUT = 5 * 1000


class _OrgFreeDesktopThumbnailer(object):
    """
    Proxy for using the org.freedesktop.thumbnailer service.
    """

    def __init__(self):

        # table: handle -> (uri, cb, args)
        self.__handles = {}
    
        bus = platforms.get_session_bus()
        obj = bus.get_object(_THUMBNAILER_SERVICE, _THUMBNAILER_PATH)
        self.__thumbnailer = dbus.Interface(obj, _THUMBNAILER_INTERFACE)
        
        self.__thumbnailer.connect_to_signal("Finished", self.__on_finish)
        self.__thumbnailer.connect_to_signal("Error", self.__on_error)


    def is_busy(self):
    
        return self.__handles


    def queue(self, uri, mimetypes, cb, *args):
    
        handle = self.__thumbnailer.Queue([uri], mimetypes, 0)
        timeout = gobject.timeout_add(_TIMEOUT, self.__on_check_for_timeout,
                                      handle)
        self.__handles[int(handle)] = (timeout, uri, cb, args)
        print "Got Handle", handle, "for", uri
        
        
        
        
    def __on_check_for_timeout(self, handle):
    
        if (handle in self.__handles):
            timeout, uri, cb, args = self.__handles[handle]
            del self.__handles[handle]
            print "timeout reached for thumbnailing handle", handle
            
            try:
                cb("", *args)
            except:
                pass


    def __on_finish(self, handle):
    
        handle = int(handle)
        print "finished thumbnailing", handle

        if (handle in self.__handles):
            timeout, uri, cb, args = self.__handles[handle]
            gobject.source_remove(timeout)
            del self.__handles[handle]
        
            thumbpath = self.__get_osso_thumbnail(uri)
            try:
                cb(thumbpath, *args)
            except:
                pass
        #end if
            
        return True


    def __on_error(self, handle, failed_uris, err, err_msg):
    
        print "Thumbnailing failed for", handle, failed_uris, err_msg
                

    def __get_osso_thumbnail(self, uri):
    
        name = hashlib.md5(uri).hexdigest()
        thumb_dir = os.path.expanduser("~/.thumbnails/cropped")
        thumb_uri = os.path.join(thumb_dir, name + ".jpeg")

        return thumb_uri

        
_singleton = _OrgFreeDesktopThumbnailer()
def OrgFreeDesktopThumbnailer(): return _singleton

