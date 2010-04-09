from com import Component, msgs
from utils import logging
import platforms

import dbus


_STATE_NONE = 0
_STATE_INCOMING = 1


class PhoneMonitor(Component):
    """
    Component for monitoring the phone state.
    """

    def __init__(self):

        self.__state = _STATE_NONE

        Component.__init__(self)

        bus = platforms.get_system_bus()
        obj = bus.get_object("com.nokia.mce", "/com/nokia/mce/signal")
        
        obj.connect_to_signal("sig_call_state_ind",
                              self.__on_state_signal)

        obj.connect_to_signal("sig_device_mode_ind",
                              self.__on_mode_signal)

       
        
    def __on_state_signal(self, call_state, emergency_state):
    
        if (call_state == "ringing"):
            self.__state = _STATE_INCOMING
            self.emit_message(msgs.SYSTEM_EV_PHONE_RINGING)
            
        elif (call_state == "active"):
            if (self.__state == _STATE_INCOMING):
                self.emit_message(msgs.SYSTEM_EV_PHONE_ANSWERING)
            else:
                self.emit_message(msgs.SYSTEM_EV_PHONE_DIALING)
                
        elif (call_state == "none"):
            self.emit_message(msgs.SYSTEM_EV_PHONE_HANGUP)
            self.__state = _STATE_NONE


    def __on_mode_signal(self, mode):
    
        if (mode == "normal"):
            self.emit_message(msgs.SYSTEM_EV_NORMAL_MODE)

        elif (mode == "flight"):
            self.emit_message(msgs.SYSTEM_EV_OFFLINE_MODE)

        elif (mode == "offline"):
            self.emit_message(msgs.SYSTEM_EV_OFFLINE_MODE)

