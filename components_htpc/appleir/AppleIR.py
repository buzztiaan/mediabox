from com import Component, msgs
from utils import logging

import commands
import gobject
import time


# these are the codes that my AppleRemote produces; YMMV
_KEYCODES = {

  # product 0x8240
  (0x87, 0xee, 0xfa, 0x0b): msgs.HWKEY_EV_UP,
  (0x87, 0xee, 0xfa, 0x0d): msgs.HWKEY_EV_DOWN,
  (0x87, 0xee, 0xfa, 0x08): msgs.HWKEY_EV_LEFT,
  (0x87, 0xee, 0xfa, 0x07): msgs.HWKEY_EV_RIGHT,
  (0x87, 0xee, 0xfa, 0x04): msgs.HWKEY_EV_ENTER,
  (0x87, 0xee, 0xfa, 0x02): msgs.HWKEY_EV_MENU,

}

_KEY_REPEAT = ()
_FLAT_BATTERY = (0x25, 0x87, 0xe0, 0xca, 0x06)



class AppleIR(Component):
    """
    Component for controlling MediaBox with the AppleRemote infrared remote
    control that comes included with most Macs nowadays.
    
    The AppleRemote appears as USB-device once the "appleir" kernel module is
    loaded.
    """

    def __init__(self):
    
        self.__last_keycode = None
        self.__warned_about_battery = False
        
        self.__accept_repeat_time = 0
        
        Component.__init__(self)
    
        usbdev = self.__find_device()
        if (usbdev):
            try:
                fd = open(usbdev, "r")
            except:
                logging.error("cannot read from AppleRemote %s- " \
                              "permission denied?" % usbdev)
            else:
                gobject.io_add_watch(fd, gobject.IO_IN, self.__on_receive_input)

        
    
    def __find_device(self):
        """
        Returns the device for reading input.
        """
        
        current_dev = ""
        current_product = ""
        
        hal_data = commands.getoutput("/usr/bin/hal-device")
        for line in hal_data.splitlines():
            if (not line.strip()):
                # empty line
                if ("Apple" in current_product and "IR" in current_product):
                    logging.info("found AppleRemote @ %s", current_dev)
                    return current_dev
                continue
                
            elif (line[0].isdigit()):
                # new device
                pass
                
            else:
                # entry
                parts = line.split(" = ")
                key = parts[0].strip()
                value = parts[1].strip()

                if (key == "info.product"):
                    current_product = value
                    #print key, current_product
                elif (key == "linux.device_file"):
                    current_dev = value[1:value.rfind("'")]
                    #print key, current_dev
        #end for
        
        logging.info("no AppleRemote found")
        return None


    def __on_receive_input(self, fd, cond):
    
        data = fd.read(32)
        code = tuple([ ord(c) for c in data if 0x0 < ord(c) < 0xff ])
        print code

        if (code == _KEY_REPEAT):
            if (self.__accept_repeat_time + 1.0 > time.time() > self.__accept_repeat_time):
                keycode = self.__last_keycode
            else:
                return True
            
        elif (code == _FLAT_BATTERY and not self.__warned_about_battery):
            self.call_service(msgs.NOTIFY_SVC_SHOW_MESSAGE,
                              "AppleRemote has weak battery")
            logging.warning("AppleRemote has weak battery")
            self.__warned_about_battery = True
            return True
            
        else:
            keycode = _KEYCODES.get(code)
            self.__accept_repeat_time = time.time() + 0.5
            
        if (keycode):
            self.emit_message(keycode)
            self.__last_keycode = keycode
        else:
            logging.warning("AppleRemote sent unknown code: %s", `code`)

        return True

