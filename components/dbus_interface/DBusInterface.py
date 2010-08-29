from com import Component, msgs
from storage import File
from mediabox import values
from utils import mimetypes

import dbus
import dbus.service
import os

# location of exported picture (cover art, etc.)
_PICTURE_LOCATION = os.path.join(values.USER_DIR, "picture.jpg")


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


    @dbus.service.method("de.pycage.mediabox.control", in_signature = "ss")
    def load(self, uri, mimetype):
    
        if (not mimetype):
            ext = os.path.splitext(uri)[1]
            mimetype = mimetypes.ext_to_mimetype(ext)
    
        print uri, mimetype
        f = self.call_service(msgs.CORE_SVC_GET_FILE,
                              "adhoc://" + File.pack_path("/", uri, mimetype))
        print "Loading by D-Bus request:", f
        if (f):
            self.emit_message(msgs.MEDIA_ACT_LOAD, f)


    @dbus.service.method("de.pycage.mediabox.control")
    def play(self):
    
        self.emit_message(msgs.MEDIA_ACT_PLAY)


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
    
        print key, value, type(key), type(value)
        
        if (key == "PICTURE" and value):
            try:
                pbuf = value
                pbuf.save(_PICTURE_LOCATION, "jpeg")
                value = _PICTURE_LOCATION
            except:
                value = ""
        
        self.tag_signal(key, value or "")
    
    
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
            if (total == -1):
                total = 0
            self.seek_signal(int(pos * 1000), int(total * 1000))


    def handle_MEDIA_EV_VOLUME_CHANGED(self, vol):
    
        self.__volume = vol

