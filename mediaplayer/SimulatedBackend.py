from AbstractBackend import AbstractBackend

import random
import gobject


class SimulatedBackend(AbstractBackend):
    """
    Backend implementation simulating a media backend.
    """

    def __init__(self):

        self.__position = 0
        self.__total = 0
        self.__is_playing = False
        self.__is_eof = False
        self.__volume = 100
        self.__play_handler = None

        AbstractBackend.__init__(self)


    def __player(self):
    
        if (self.__is_playing):
            if (self.__position >= self.__total):
                self.__is_eof = True
            else:
                self.__position += 1
            
        return True


    def _get_icon(self):
    
        from theme import theme
        return theme.mb_backend_oms


    def _ensure_backend(self):
    
        if (not self.__play_handler):
            self.__play_handler = gobject.timeout_add(1000, self.__player)


    def _is_eof(self):
    
        return self.__is_eof
        

    def _set_window(self, xid):
    
        pass
        
        
    def _load(self, uri):
    
        self.__is_eof = False
        self.__total = random.randint(30, 500)
        self.__position = 0
        self._report_volume(self.__volume)


    def _set_volume(self, volume):

        self.__volume = volume


    def _play(self):
         
        self.__is_eof = False
        self.__is_playing = True
        
        
    def _stop(self):

        self.__is_playing = False


    def _close(self):

        if (self.__play_handler):
            gobject.source_remove(self.__play_handler)
            self.__play_handler = None    


    def _seek(self, pos):

        self.__position = max(0, min(pos, self.__total))


    def _get_position(self):

        return (self.__position, self.__total)

