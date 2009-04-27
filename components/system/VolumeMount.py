from com import Component, msgs
from utils import maemo
from utils import logging

import dbus


class VolumeMount(Component):

    def __init__(self):
    
        # table: ident -> (device, path)
        self.__mounts = {}
        
        Component.__init__(self)
                
        session_bus = maemo.get_session_bus()
        obj = session_bus.get_object("org.gnome.GnomeVFS.Daemon",
                             "/org/gnome/GnomeVFS/Daemon")
        iface = dbus.Interface(obj, 'org.gnome.GnomeVFS.Daemon')
        iface.connect_to_signal("VolumeMountedSignal", self.__on_mount_volume)
        iface.connect_to_signal("VolumeUnmountedSignal", self.__on_unmount_volume)
        
        
    def __on_mount_volume(self, arg):
    
        ident = arg[0]
        path = arg[4][7:]
        label = arg[6]
        device = arg[11]
        self.__mounts[ident] = (device, path)
        logging.info("device mounted: %s at %s", label, path)
        self.emit_message(msgs.SYSTEM_EV_DRIVE_MOUNTED, label, path)



    def __on_unmount_volume(self, ident):
    
        dev, path = self.__mounts.get(ident, (None, None))
        if (dev and path):
            logging.info("device unmounted: %s", dev)
            self.emit_message(msgs.SYSTEM_EV_DRIVE_UNMOUNTED, path)
        else:
            logging.info("unspecified device unmounted: %s", ident)
            self.emit_message(msgs.SYSTEM_EV_DRIVE_UNMOUNTED, path)
