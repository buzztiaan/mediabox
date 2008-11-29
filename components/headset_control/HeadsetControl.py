from com import Component, msgs

import gobject


class HeadsetControl(Component):
    """
    Component for recognizing headset button "gestures".
    """

    def __init__(self):
    
        self.__click_count = 0
        self.__click_handler = None
    
        Component.__init__(self)
        
        
        
    def __handle_click(self):

        if (self.__click_count == 1):
            self.emit_event(msgs.MEDIA_ACT_PAUSE)
            print "PAUSE"

        elif (self.__click_count == 2):
            #self.emit_event(msgs.MEDIA_ACT_PREVIOUS)
            print "PREVIOUS"
            
        elif (self.__click_count == 3):
            #self.emit_event(msgs.MEDIA_ACT_NEXT)
            print "NEXT"
            
        self.__click_count = 0
        self.__click_handler = None
        
        
    def handle_event(self, msg, *args):
    
        if (msg == msgs.HWKEY_EV_HEADSET):
            self.__click_count += 1
            if (self.__click_handler):
                gobject.source_remove(self.__click_handler)
            self.__click_handler = gobject.timeout_add(500, self.__handle_click)
            
            self.emit_event(msgs.MEDIA_ACT_PAUSE)

