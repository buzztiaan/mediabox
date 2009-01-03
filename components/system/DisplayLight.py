from com import Component, msgs
from utils import maemo
import config

import gobject


class DisplayLight(Component):

    def __init__(self):
    
        Component.__init__(self)
        self.__devstate = maemo.get_device_state()
        
        self.__timeout_handler = None


    def handle_message(self, msg, *args):
    
        if (msg == msgs.UI_EV_VIEWER_CHANGED):
            idx = args[0]            
            if (idx != -1):
                # viewer; may keep display on
                lit = config.get_display_lit()
                if (not self.__timeout_handler and lit == "yes"):
                    self.__timeout_handler = gobject.timeout_add(29000,
                                                        self.__keep_display_on)
            else:
                # main menu; may not keep display on
                if (self.__timeout_handler):
                    gobject.source_remove(self.__timeout_handler)
                    self.__timeout_handler = None



    def __keep_display_on(self):
    
        self.__devstate.display_blanking_pause()
        return True

