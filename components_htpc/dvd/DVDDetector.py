from com import Component, msgs
from DVDDevice import DVDDevice
from VCDDevice import VCDDevice
from utils import logging

import time
import os
import commands


class DVDDetector(Component):

    def __init__(self):
    
        # table: path -> uuid
        self.__devices = {}
        
        Component.__init__(self)


    def __find_dvd(self):
    
        for line in open("/etc/mtab", "r").readlines():
            parts = line.split()
            device = parts[0]
            mountpoint = parts[1]
            filesystem = parts[2]
            
            if (filesystem == "udf" and self.__is_dvd(mountpoint)):
                label = commands.getoutput("volname %s" % device)
                return label, mountpoint
        #end for
        
        return ""
        


    def __is_dvd(self, path):
    
        video_ts = os.path.join(path, "VIDEO_TS")
        return os.path.exists(video_ts)       


    def __is_vcd(self, path):
    
        vcd = os.path.join(path, "vcd")
        return os.path.exists(vcd)       


    def __load_dvd(self, label, path):

        uuid = "dvd:%s" % `time.time()`
        device = DVDDevice(label, path)
        self.__devices[path] = uuid
        
        self.emit_message(msgs.CORE_EV_DEVICE_ADDED, uuid, device)
        self.call_service(msgs.NOTIFY_SVC_SHOW_INFO, u"DVD inserted")
        #self.emit_message(msgs.UI_ACT_SELECT_VIEWER, "VideoViewer")
        #self.emit_message(msgs.UI_ACT_SELECT_DEVICE, uuid)
    
    
    def __load_vcd(self, label, path):

        uuid = "vcd:%s" % `time.time()`
        device = VCDDevice(label, path)
        self.__devices[path] = uuid

        self.emit_message(msgs.CORE_EV_DEVICE_ADDED, uuid, device)
        self.call_service(msgs.NOTIFY_SVC_SHOW_INFO, u"VCD inserted")
        #self.emit_message(msgs.UI_ACT_SELECT_VIEWER, "VideoViewer")
        #self.emit_message(msgs.UI_ACT_SELECT_DEVICE, uuid)

    
    
        

    def handle_message(self, msg, *args):
    
        if (msg == msgs.CORE_EV_APP_STARTED):
            label, path = self.__find_dvd()
            if (self.__is_dvd(path)):
                self.__load_dvd(label, path)

            elif (self.__is_vcd(path)):
                self.__load_vcd(label, path)
    
        elif (msg == msgs.SYSTEM_EV_DRIVE_MOUNTED):
            label, path = args
            if (self.__is_dvd(path)):
                self.__load_dvd(label, path)

            elif (self.__is_vcd(path)):
                self.__load_vcd(label, path)

        elif (msg == msgs.SYSTEM_EV_DRIVE_UNMOUNTED):
            for path in self.__devices.keys():
                if (not self.__is_dvd(path) and not self.__is_vcd(path)):
                    print "REMOVED", path
                    uuid = self.__devices[path]
                    del self.__devices[path]
                    self.emit_message(msgs.CORE_EV_DEVICE_REMOVED, uuid)
                #end if
            #end for
   
        elif (msg == msgs.INPUT_EV_EJECT):
            if (self.__devices):
                dev = self.__devices.keys()[0]
                self.emit_message(msgs.MEDIA_ACT_STOP)
                self.emit_message(msgs.UI_ACT_SHOW_MESSAGE,
                                "Ejecting Disc", "",
                                None)
                logging.info("ejecting media %s", dev)
                os.system("eject %s" % dev)
                self.emit_message(msgs.UI_ACT_HIDE_MESSAGE)

