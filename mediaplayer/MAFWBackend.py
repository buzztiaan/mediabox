from AbstractBackend import AbstractBackend
from utils import c_gobject

import gobject
import ctypes


class MAFWBackend(AbstractBackend):
    """
    Class for a MAFW backend for Maemo5.
    """            

    def __init__(self):

        self.__mafw = ctypes.CDLL("libmafw.so.0")
        self.__mafw_shared = ctypes.CDLL("libmafw-shared.so.0")

        AbstractBackend.__init__(self)

        registry_p = self.__mafw.mafw_registry_get_instance()
        
        err = ctypes.c_void_p()
        self.__mafw_shared.mafw_shared_init(self.__registry, ctypes.byref(err))

        self.__registry = c_gobject.wrap(registry_p)
        self.__registry.connect("renderer_added", self.__on_renderer_added)

        ext_list = self.__mafw_registry.mafw_registry_get_renderers(registry_p)


    def __on_renderer_added(self, *args):
    
        print "new renderer", args

    def _ensure_backend(self):
    
        pass
        

    def _set_window(self, xid):
    
        pass
              

    def _load(self, uri):

        def f():
            self._report_error(self.ERR_NOT_SUPPORTED, "")

        gobject.idle_add(f)
        

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

