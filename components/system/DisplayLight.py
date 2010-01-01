from com import Component, msgs
import platforms
import config

import gobject


class DisplayLight(Component):

    def __init__(self):

        Component.__init__(self)
        
        self.__timeout_handler = None


    def handle_MEDIA_EV_PLAY(self):
    
        lit = config.get_display_lit()
        if (lit == "playing"):
            self.__enable_light()


    def handle_MEDIA_EV_PAUSE(self):

        lit = config.get_display_lit()
        if (lit == "playing"):
            self.__disable_light()
    
    
    def handle_MEDIA_EV_EOF(self):        

        lit = config.get_display_lit()
        if (lit == "playing"):
            self.__disable_light()


    def __enable_light(self):

        print "enabling light"
        if (not self.__timeout_handler):
            self.__timeout_handler = gobject.timeout_add(23000,
                                                         self.__keep_display_on)
                                                         
                                                         
    def __disable_light(self):

        print "disabling light"
        if (self.__timeout_handler):
            gobject.source_remove(self.__timeout_handler)
            self.__timeout_handler = None


    def __keep_display_on(self):
    
        print "inhibiting screen blanking"
        platforms.inhibit_screen_blanking()
        return True

