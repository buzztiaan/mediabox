from com import Component, msgs

import dbus
import dbus.service


class DBusInterface(Component, dbus.service.Object):
    """
    Component for controlling the application with a D-Bus interface.
    """

    def __init__(self):
    
        self.__need_report_position = True
        self.__volume = 0
    
        Component.__init__(self)
        dbus.service.Object.__init__(self,
                                     dbus.service.BusName("de.pycage.mediabox",
                                                          dbus.SessionBus()),
                                     "/de/pycage/mediabox/control")


    @dbus.service.method("de.pycage.mediabox.control")
    def play(self):
    
        self.emit_message(msgs.MEDIA_ACT_PAUSE)


    @dbus.service.method("de.pycage.mediabox.control")
    def pause(self):
    
        self.emit_message(msgs.MEDIA_ACT_PAUSE)


    @dbus.service.method("de.pycage.mediabox.control")
    def stop(self):
    
        self.emit_message(msgs.MEDIA_ACT_STOP)


    @dbus.service.method("de.pycage.mediabox.control")
    def previous(self):
    
        self.emit_message(msgs.MEDIA_ACT_PREVIOUS)


    @dbus.service.method("de.pycage.mediabox.control")
    def next(self):
    
        self.emit_message(msgs.MEDIA_ACT_NEXT)


    @dbus.service.method("de.pycage.mediabox.control", in_signature = "u")
    def seek(self, pos):
    
        self.emit_message(msgs.MEDIA_ACT_SEEK, pos / 1000.0)


    @dbus.service.method("de.pycage.mediabox.control", out_signature = "u")
    def get_volume(self):
    
        return self.__volume


    """
    Not implemented yet...
    @dbus.service.method("de.pycage.mediabox.control", in_signature = "u")
    def set_volume(self, volume):
    
        self.emit_message(msgs.MEDIA_ACT_SET_VOLUME, volume)
    """
    
        
    @dbus.service.signal("de.pycage.mediabox.control", "s")
    def state_signal(self, state): pass


    @dbus.service.signal("de.pycage.mediabox.control", "uu")
    def seek_signal(self, pos, total): pass


    @dbus.service.signal("de.pycage.mediabox.control", "ssss")
    def load_signal(self, name, info, resource, mimetype): pass


    @dbus.service.signal("de.pycage.mediabox.control", "ss")
    def tag_signal(self, key, value): pass
    
    
    def handle_MEDIA_EV_LOADED(self, player, f):
    
        self.load_signal(f.name, f.info, f.resource, f.mimetype)
        self.__need_report_position = True
    
    
    def handle_MEDIA_EV_TAG(self, key, value):
    
        self.tag_signal(key, value)
    
    
    def handle_MEDIA_EV_PLAY(self):
    
        self.state_signal("playing")
        self.__need_report_position = True


    def handle_MEDIA_EV_PAUSE(self):
    
        self.state_signal("paused")
        self.__need_report_position = True
        

    def handle_MEDIA_EV_EOF(self):
    
        self.state_signal("eof")
        self.__need_report_position = True


    def handle_MEDIA_EV_POSITION(self, pos, total):
    
        if (self.__need_report_position):
            self.__need_report_position = False
            self.seek_signal(int(pos * 1000), int(total * 1000))


    def handle_MEDIA_EV_VOLUME_CHANGED(self, vol):
    
        self.__volume = vol

