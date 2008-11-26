from com import Component, msgs
from utils import maemo

import dbus


class VolumeMount(Component):

    def __init__(self):
    
        Component.__init__(self)
                
        session_bus = maemo.get_session_bus()
        obj = session_bus.get_object("org.gnome.GnomeVFS.Daemon",
                             "/org/gnome/GnomeVFS/Daemon")
        iface = dbus.Interface(obj, 'org.gnome.GnomeVFS.Daemon')
        iface.connect_to_signal("VolumeMountedSignal", self.__on_mount_mmc)
        iface.connect_to_signal("VolumeUnmountedSignal", self.__on_mount_mmc)
        
        
    def __on_mount_mmc(self, arg):
    
        print "MOUNT", arg
        self.emit_event(msgs.SYSTEM_EV_DRIVE_MOUNTED)

