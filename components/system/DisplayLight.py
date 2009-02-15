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
    
        if (msg == msgs.MEDIA_EV_PLAY):
            lit = config.get_display_lit()
            if (lit == "playing"):
                self.__enable_light()

        
        elif (msg in (msgs.MEDIA_EV_PAUSE, msgs.MEDIA_EV_EOF)):
            lit = config.get_display_lit()
            if (lit == "playing"):
                self.__disable_light()

    
        elif (msg == msgs.UI_EV_VIEWER_CHANGED):
            idx = args[0]
            lit = config.get_display_lit()
            if (lit == "yes"):
                if (idx != -1):
                    # viewer; may keep display on
                    self.__enable_light()
                else:
                    # main menu; may not keep display on
                    self.__disable_light()
                    
            elif (lit == "no"):
                self.__disable_light()
      


    def __enable_light(self):

        if (not self.__timeout_handler):
            self.__timeout_handler = gobject.timeout_add(29000,
                                                         self.__keep_display_on)
                                                         
                                                         
    def __disable_light(self):

        if (self.__timeout_handler):
            gobject.source_remove(self.__timeout_handler)
            self.__timeout_handler = None


    def __keep_display_on(self):
    
        self.__devstate.display_blanking_pause()
        return True

