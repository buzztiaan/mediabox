from AbstractBackend import AbstractBackend
from utils import maemo

import dbus
import gobject


_SERVICE_NAME = "de.pycage.Xine"
_OBJECT_PATH = "/de/pycage/Xine"
_PLAYER_IFACE = "de.pycage.Xine"


class XineBackend(AbstractBackend):
    """
    Backend implementation for controlling Xine via my D-Bus Xine wrapper.
    """

    def __init__(self):
    
        self.__current_pos = 0
        self.__window_id = 0
        self.__player = None
    
        AbstractBackend.__init__(self)


    def _get_icon(self):
    
        from theme import theme
        return theme.mb_backend_xine
                    
            
    def __start_xine(self):
    
        bus = maemo.get_session_bus()
        try:
            obj = bus.get_object(_SERVICE_NAME, _OBJECT_PATH)
            self.__player = dbus.Interface(obj, _PLAYER_IFACE)
            self.__player.connect_to_signal("aspect_changed", self.__on_aspect_changed)
        except:
            pass


    def __on_aspect_changed(self, a):
    
        if (a == 0):
            ratio = 4/3.0      # auto
        elif (a == 1):
            ratio = 1.0        # square
        elif (a == 2):
            ratio = 4/3.0      # 4:3
        elif (a == 3):
            ratio = 16/9.0     # 16:9
        elif (a == 4):
            ratio = 2.11/1.0   # DVB
        else:
            ratio = 16/9.0
                      
        print "RATIO", ratio
        self._report_aspect_ratio(ratio)

        
    def _ensure_backend(self):
    
        if (not self.__player):
            self.__start_xine()


    def _set_window(self, xid):
    
        if (xid != self.__window_id):
            self.__window_id = xid
        
        
    def _is_eof(self):
    
        return False
        
        
    def _close(self):
    
        self.__player.quit()
        self.__player = None

        
    def _load(self, uri):
    
        if (uri.endswith(".dvd") or uri.endswith(".iso")):
            uri = "dvd://" + uri
        self.__current_pos = 0
    
        if (self._get_mode() == self.MODE_VIDEO):
            if (self.__window_id != 0):
                self.__player.set_window(self.__window_id)
                self.__window_id = 0

        self.__player.open(uri)



    def _send_key(self, key):
    
        self.__player.send_key(key)
        
        return True
        
        
    def _play(self):

        self.__player.play()
        
        
    def _stop(self):
    
        self.__player.stop()
        
        
    def _seek(self, pos):

        self.__player.seek(pos)    
        
        
    def _set_volume(self, vol):

        self.__player.set_volume(vol)    

        
    def _get_position(self):

        pos, total = self.__player.get_position()    
        return (pos, total)

