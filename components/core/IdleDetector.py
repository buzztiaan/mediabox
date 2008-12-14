from com import Component, msgs
from utils import logging

import time
import gobject


_IDLE_TIMEOUT = 60000


class IdleDetector(Component):
    """
    Component responsible for putting the application into idle mode for saving
    battery.
    
    @todo: don't go idle when on AC
    """

    def __init__(self):
    
        self.__idle_timer = None
        self.__is_idle = False
        
        Component.__init__(self)
        
        
    def __go_idle(self):
    
        self.__is_idle = True
        self.__idle_timer = None
        logging.info("no activity: going idle")
        self.emit_event(msgs.CORE_EV_APP_IDLE_BEGIN)
        
        
        
    def handle_event(self, ev, *args):
    
        if (self.__is_idle):
            self.__is_idle = False
            logging.info("activity: waking up")
            self.emit_event(msgs.CORE_EV_APP_IDLE_END)
    
        if (self.__idle_timer):
            gobject.source_remove(self.__idle_timer)
        self.__idle_timer = gobject.timeout_add(_IDLE_TIMEOUT, self.__go_idle)

