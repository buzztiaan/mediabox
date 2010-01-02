from com import Component, msgs
from utils import maemo
from utils import logging

import dbus
import gobject


_HAL_SERVICE = "org.freedesktop.Hal"
_HEADSET_PATH = "/org/freedesktop/Hal/devices/platform_retu_headset_logicaldev_input"
_HAL_DEVICE_IFACE = "org.freedesktop.Hal.Device"

_HEADPHONE_SYS = "/sys/devices/platform/gpio-switch/headphone/state"


class Headset(Component):
    """
    Component for monitoring the headset status.
    """

    def __init__(self):
    
        self.__is_connected = True
        
        self.__click_count = 0
        self.__click_handler = None
        
        Component.__init__(self)
    
        # monitor headset button
        try:
            bus = maemo.get_system_bus()
            obj = bus.get_object(_HAL_SERVICE, _HEADSET_PATH)
            device = dbus.Interface(obj, _HAL_DEVICE_IFACE)
            device.connect_to_signal("Condition", self.__on_hal_condition)
        except:
            logging.warning("unable to monitor headset button")

        # monitor headset status
        try:
            fd = open(_HEADPHONE_SYS, "r")
            self.__on_connect(None, None)            
            self.__watcher = gobject.io_add_watch(fd, gobject.IO_PRI,
                                                  self.__on_connect)
        except:
            logging.warning("unable to monitor headset connection")


        # set up speaker control
        try:
            bus = maemo.get_session_bus()
            obj = bus.get_object("com.nokia.osso_hp_ls_controller",
                                 "/com/nokia/osso_hp_ls_controller")
            self.__speaker = dbus.Interface(obj,
                                  "com.nokia.osso_hp_ls_controller.loudspeaker")
        except:
            logging.warning("cannot force loudspeaker")
            self.__speaker = None



    def __handle_click(self):

        if (self.__click_count == 1):
            self.emit_event(msgs.HWKEY_EV_HEADSET)

        elif (self.__click_count == 2):
            self.emit_event(msgs.HWKEY_EV_HEADSET_DOUBLE)
            
        elif (self.__click_count == 3):
            self.emit_event(msgs.HWKEY_EV_HEADSET_TRIPLE)
            
        self.__click_count = 0
        self.__click_handler = None


    def __on_hal_condition(self, arg1, arg2):

        if ((arg1, arg2) == ("ButtonPressed", "phone")):
            logging.info("headset button pressed")
            self.__click_count += 1

            if (self.__click_handler):
                gobject.source_remove(self.__click_handler)

            self.__click_handler = gobject.timeout_add(700, self.__handle_click)


    def __on_connect(self, src, cond):
        
        if (src): src.read()

        state = open(_HEADPHONE_SYS, "r").read().strip()
        if (state == "disconnected"):
            self.__is_connected = False
            logging.info("headphones disconnected")
            self.emit_event(msgs.SYSTEM_EV_HEADPHONES_REMOVED)

        elif (state == "connected"):
            self.__is_connected = True
            logging.info("headphones connected")
            self.emit_event(msgs.SYSTEM_EV_HEADPHONES_INSERTED)

        return True


    def is_connected(self):
    
        return self.__is_connected


    def __set_force_speaker(self, value):
        
        if (not self.__speaker): return

        # TODO: can this state be monitored?        
        if (value):
            self.__speaker.force_loudspeaker_on()
        else:
            self.__speaker.force_loudspeaker_off()


    def handle_SYSTEM_ACT_FORCE_SPEAKER_ON(self):
    
        self.__set_force_speaker(True)


    def handle_SYSTEM_ACT_FORCE_SPEAKER_OFF(self):            

        self.__set_force_speaker(False)

