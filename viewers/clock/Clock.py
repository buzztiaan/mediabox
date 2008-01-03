from viewers.Viewer import Viewer
from SunClock import SunClock
import theme

import gtk
import gobject
import os



class Clock(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_clock
    ICON_ACTIVE = theme.viewer_clock_active
    PRIORITY = 100
   

    def __init__(self, esens):
    
        self.__is_ticking = False
    
        Viewer.__init__(self, esens)
                
        self.__sunclock = SunClock(esens)
        self.add(self.__sunclock)
              
        
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
                   
        self.__tick()
        if (not self.__is_ticking):
            gobject.timeout_add(10000, self.__tick)
            self.__is_ticking = True

