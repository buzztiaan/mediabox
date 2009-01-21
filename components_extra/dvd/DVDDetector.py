from com import Component, msgs
from DVDDevice import DVDDevice
from VCDDevice import VCDDevice
from utils import logging

import time
import os


class DVDDetector(Component):

    def __init__(self):
    
        # table: path -> uuid
        self.__devices = {}
        
        Component.__init__(self)


    def __is_dvd(self, path):
    
        video_ts = os.path.join(path, "VIDEO_TS")
        return os.path.exists(video_ts)       


    def __is_vcd(self, path):
    
        vcd = os.path.join(path, "vcd")
        return os.path.exists(vcd)       

        

    def handle_message(self, msg, *args):
    
        if (msg == msgs.SYSTEM_EV_DRIVE_MOUNTED):
            path = args[0]
            if (self.__is_dvd(path)):
                uuid = "dvd:%s" % `time.time()`
                device = DVDDevice(path)
                self.__devices[path] = uuid
                
                self.emit_event(msgs.CORE_EV_DEVICE_ADDED, uuid, device)
                self.call_service(msgs.NOTIFY_SVC_SHOW_INFO, u"DVD inserted")
                self.emit_event(msgs.UI_ACT_SELECT_VIEWER, "VideoViewer")
                self.emit_event(msgs.UI_ACT_SELECT_DEVICE, uuid)

            elif (self.__is_vcd(path)):
                uuid = "vcd:%s" % `time.time()`
                device = VCDDevice(path)
                self.__devices[path] = uuid

                self.emit_event(msgs.CORE_EV_DEVICE_ADDED, uuid, device)
                self.call_service(msgs.NOTIFY_SVC_SHOW_INFO, u"VCD inserted")
                self.emit_event(msgs.UI_ACT_SELECT_VIEWER, "VideoViewer")
                self.emit_event(msgs.UI_ACT_SELECT_DEVICE, uuid)


        elif (msg == msgs.SYSTEM_EV_DRIVE_UNMOUNTED):
            path = args[0]
            
            if (path in self.__devices):
                uuid = self.__devices[path]
                del self.__devices[path]
                self.emit_event(msgs.CORE_EV_DEVICE_REMOVED, uuid)

   
        elif (msg == msgs.INPUT_EV_EJECT):
            if (self.__devices):
                dev = self.__devices.keys()[0]
                self.emit_event(msgs.UI_ACT_SHOW_MESSAGE,
                                "Ejecting Disc", "",
                                None)
                logging.info("ejecting media %s", dev)
                os.system("eject %s" % dev)
                self.emit_event(msgs.UI_ACT_HIDE_MESSAGE)

