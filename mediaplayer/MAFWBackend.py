from AbstractBackend import AbstractBackend
import gobject


class MAFWBackend(AbstractBackend):
    """
    Class for a MAFW backend for Maemo5.
    """            

    def __init__(self):

        AbstractBackend.__init__(self)


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

