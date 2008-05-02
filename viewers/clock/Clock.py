from viewers.Viewer import Viewer
from ui.KineticScroller import KineticScroller
from SunClock import SunClock
import theme

import gtk
import gobject
import os
import time



class Clock(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_clock
    ICON_ACTIVE = theme.viewer_clock_active
    PRIORITY = 100
   

    def __init__(self, esens):
    
        self.__is_ticking = False
    
        Viewer.__init__(self, esens)

        self.__sunclock = SunClock(esens)
        self.__sunclock.set_pos(0, 10)
        self.add(self.__sunclock)

        # kinetic panning of the earth background is not optimized for speed
        # yet
        #kscr = KineticScroller(self.__sunclock)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, "#000000")
              
        
    def __tick(self):
    
        if (self.may_render()):
            today = time.strftime("%A - %x", time.localtime())
            self.update_observer(self.OBS_TITLE, today)
            self.update_observer(self.OBS_RENDER)
            return True
        else:
            self.__is_ticking = False
            return False
        
        
    def show(self):
    
        Viewer.show(self)
        self.update_observer(self.OBS_HIDE_COLLECTION)
                   
        self.__tick()
        if (not self.__is_ticking):
            today = time.strftime("%A - %x", time.localtime())
            self.update_observer(self.OBS_TITLE, today)

            gobject.timeout_add(10000, self.__tick)
            self.__is_ticking = True

