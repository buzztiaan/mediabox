from viewers.Viewer import Viewer
from SunClock import SunClock
import theme

import gtk
import gobject
import os



class Clock(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_clock
    PRIORITY = 100
    BORDER_WIDTH = 0
    IS_EXPERIMENTAL = False
    

    def __init__(self):
    
        self.__is_ticking = False
    
        Viewer.__init__(self)
                
        self.__sunclock = SunClock()
        self.set_widget(self.__sunclock)
        
        #gobject.timeout_add(10000, self.__tick)
        
        
    def __tick(self):
    
        self.__sunclock.update()
        if (self.is_active()):
            return True
        else:
            self.__is_ticking = False
            return False
        
        
    def show(self):
    
        Viewer.show(self)
        self.update_observer(self.OBS_HIDE_COLLECTION)
        gobject.idle_add(self.__sunclock.update)
        
        self.__tick()
        if (not self.__is_ticking):
            gobject.timeout_add(10000, self.__tick)
            self.__is_ticking = True

