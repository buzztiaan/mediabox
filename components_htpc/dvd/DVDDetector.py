from com import Component, msgs
from storage import Device, File
from DVDDevice import DVDDevice
#from VCDDevice import VCDDevice
from utils import maemo
from utils import logging

import time
import os
import commands
import dbus


class DVDDetector(Component):

    def __init__(self):

        self.__device = DVDDevice()

        Component.__init__(self)
        
        
        system_bus = maemo.get_system_bus()
        obj = system_bus.get_object("org.freedesktop.Hal",
                                    "/org/freedesktop/Hal/Manager")
        iface = dbus.Interface(obj, "org.freedesktop.Hal.Manager")
        iface.connect_to_signal("DeviceAdded", self.__on_add_device)


    def __on_add_device(self, ident):
    
        devices = commands.getoutput("/usr/bin/hal-device")
        for device in devices.split("\n\n"):
            print device
            print "\n\n"
           
            if (ident in device):
                if ("volume.disc.type = 'dvd_rom'" in device):
                    pass #self.__load_dvd("DVD", "/dev/cdrom")
                    
                elif ("volume.disc.is_vcd = true" in device):
                    self.__load_vcd("Video CD")
                    
                elif ("volume.disc.is_svcd = true" in device):
                    self.__load_vcd("SVideo CD")
                
                elif ("volume.disc.has_audio = true" in device):
                    pass
                    
                break
            #end if
    
        #end for            
   


    def __is_dvd(self, path):
    
        video_ts = os.path.join(path, "VIDEO_TS")
        return os.path.exists(video_ts)


    def __load_dvd(self, label, path):

        f = File(self.__device)
        f.path = "/"
        f.name = label
        f.mimetype = "video/x-dvd-image"
        f.resource = "dvd://%s" % path        
        self.emit_message(msgs.MEDIA_ACT_LOAD, f)
        self.call_service(msgs.NOTIFY_SVC_SHOW_INFO, u"DVD inserted")
    
    
    def __load_vcd(self, label):

        f = File(self.__device)
        f.path = "/"
        f.name = label
        f.mimetype = "video/x-vcd-image"
        f.resource = "vcd://dev/cdrom@P1"
        self.emit_message(msgs.MEDIA_ACT_LOAD, f)
        self.call_service(msgs.NOTIFY_SVC_SHOW_INFO, u"Video CD inserted")

   

    def handle_SYSTEM_EV_DRIVE_MOUNTED(self, label, path):
    
        if (self.__is_dvd(path)):
            self.__load_dvd(label, path)

    """
    def handle_SYSTEM_EV_DRIVE_UNMOUNTED(self, path):

        for path in self.__devices.keys():
            if (not self.__is_dvd(path) and not self.__is_vcd(path)):
                uuid = self.__devices[path]
                del self.__devices[path]
                self.emit_message(msgs.CORE_EV_DEVICE_REMOVED, uuid)
            #end if
        #end for
    """
    

    def handle_INPUT_EV_EJECT(self):   

        self.emit_message(msgs.MEDIA_ACT_STOP)
        self.emit_message(msgs.UI_ACT_SHOW_MESSAGE,
                        "Ejecting Disc", "",
                        None)
        logging.info("ejecting disc")
        os.system("eject")
        self.emit_message(msgs.UI_ACT_HIDE_MESSAGE)

