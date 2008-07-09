from com import Component, msgs
from utils import maemo
from Headset import Headset

import dbus


class System(Component):

    def __init__(self):
    
        Component.__init__(self)
                
        session_bus = maemo.get_session_bus()
        obj = session_bus.get_object("org.gnome.GnomeVFS.Daemon",
                             "/org/gnome/GnomeVFS/Daemon")
        iface = dbus.Interface(obj, 'org.gnome.GnomeVFS.Daemon')
        iface.connect_to_signal("VolumeMountedSignal", self.__on_mount_mmc)
        
        
        self.__headset = Headset()
        self.__headset.add_observer(self.__on_observe_headset)
        
        
    def __on_mount_mmc(self, arg):
    
        print "MOUNT", arg
        self.emit_event(msgs.SYSTEM_EV_DRIVE_MOUNTED)



    def __on_observe_headset(self, src, cmd, *args):
    
        if (cmd == src.OBS_BUTTON_PRESSED):
            self.emit_event(msgs.HWKEY_EV_HEADSET)
            
            
            
    def handle_event(self, event, *args):
    
        if (event == msgs.SYSTEM_ACT_FORCE_SPEAKER_ON):
            self.__headset.set_force_speaker(True)
            
        elif (event == msgs.SYSTEM_ACT_FORCE_SPEAKER_OFF):
            self.__headset.set_force_speaker(False)

