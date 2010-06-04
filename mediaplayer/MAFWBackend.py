from AbstractBackend import AbstractBackend
from utils import c_gobject

import gobject
import ctypes


class _GError(ctypes.Structure): pass
_GError._fields_ = [
    ("domain", ctypes.c_uint32),
    ("code", ctypes.c_int),
    ("message", ctypes.c_char_p)
]

class _GList(ctypes.Structure): pass
_GList._fields_ = [
    ("data", ctypes.c_void_p),
    ("next", ctypes.POINTER(_GList)),
    ("prev", ctypes.POINTER(_GList))
]


class MAFWBackend(AbstractBackend):
    """
    Class for a MAFW backend for Maemo5.
    """            

    def __init__(self):

        self.__renderer = None

        self.__mafw = ctypes.CDLL("libmafw.so.0")
        self.__mafw_shared = ctypes.CDLL("libmafw-shared.so.0")

        AbstractBackend.__init__(self)

        registry_p = self.__mafw.mafw_registry_get_instance()
        print "REGISTRY", registry_p
        
        err_p = ctypes.c_void_p(0)
        self.__mafw_shared.mafw_shared_init(registry_p,
                                            ctypes.byref(err_p))

        self.__registry = c_gobject.wrap(registry_p)
        self.__registry.connect("renderer_added", self.__on_renderer_added)

        list_p = self.__mafw.mafw_registry_get_renderers(registry_p)
        print "ext list p", list_p
        while (list_p):
	    item = _GList(list_p[0])
            print item.data
            list_p = item.next
        #end while


    def __on_renderer_added(self, *args):
    
        print "new renderer", args
        renderer_p = args[0]
        name = self.__mafw.mafw_extension_get_name(renderer_p)
        if (name == "Mafw-Gst-Renderer"):
            self.__renderer = c_gobject.wrap(renderer_p)
            self.__renderer.connect("state-changed", self.__on_change_state)
        #end if
        
        
    def __on_change_state(self, *args):
    
        pass


    def _ensure_backend(self):
    
        pass
        

    def _set_window(self, xid):
    
        pass
              

    def _load(self, uri):

        if (self.__renderer):
            self.__mafw.mafw_renderer_play_uri(hash(self.__renderer), uri,
                                               self.__on_loaded, None)
        else:            
            self._report_error(self.ERR_NOT_SUPPORTED, "")
        

    def _set_volume(self, volume):

        pass


    def _is_eof(self):
    
        return False


    def _play(self):

        pass           

        
    def _stop(self):

        pass          


    def _close(self):
    
        pass


    def _seek(self, pos):

        pass    


    def _get_position(self):
         
        return (0, 0)


if __name__ == "__main__":
    import gtk
    mafw = MAFWBackend()
    gtk.main()

