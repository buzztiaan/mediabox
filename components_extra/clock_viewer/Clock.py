from com import Viewer, msgs
from ui.KineticScroller import KineticScroller
from SunClock import SunClock
from mediabox import viewmodes
from theme import theme

import gtk
import gobject
import os
import time



class Clock(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.mb_viewer_clock
    PRIORITY = 100
   

    def __init__(self):
    
        self.__is_ticking = False
    
        Viewer.__init__(self)

        self.__sunclock = SunClock()
        self.__sunclock.set_pos(0, 0)
        self.add(self.__sunclock)

        # kinetic panning of the earth background is not optimized for speed
        # yet
        #kscr = KineticScroller(self.__sunclock)

             
        
    def __tick(self):
    
        if (self.may_render()):
            today = time.strftime("%A - %x", time.localtime())
            self.set_title(today)
            self.emit_event(msgs.UI_ACT_RENDER)
            return True
        else:
            self.__is_ticking = False
            return False
        
        
    def show(self):
    
        Viewer.show(self)
        self.emit_event(msgs.UI_ACT_VIEW_MODE, viewmodes.NORMAL)        
                   
        self.__tick()
        if (not self.__is_ticking):
            today = time.strftime("%A - %x", time.localtime())
            self.set_title(today)

            gobject.timeout_add(10000, self.__tick)
            self.__is_ticking = True

