from com import Component, msgs
from mediabox import tagreader
import platforms

import dbus
import os


#dbus-send --system --print-reply --dest=com.nokia.FMTx /com/nokia/fmtx/default org.freedesktop.DBus.Properties.Get string:'com.nokia.FMTx.Device' string:'rds_ps'

class FMTX(Component):
    """
    Component for sending RDS song information over the FM transmitter.
    """

    def __init__(self):
    
        self.__fmtx = None
        self.__is_playing = False
        self.__title = ""
    
        Component.__init__(self)

        # add support for calling fm-boost automatically, if available        
        if (os.path.exists("/sbin/fm-boost")):
            bus = platforms.get_system_bus()
            bus.add_signal_receiver(self.__on_change_fmtx,
                                    signal_name="Changed",
                                    dbus_interface="com.nokia.FMTx.Device",
                                    path="/com/nokia/fmtx/default")
        #end if    
        

    def __prepare_dbus(self):
        """
        Lazy preparation of D-Bus connection to not have an impact on startup
        speed.
        """
        
        if (not self.__fmtx):
            bus = platforms.get_system_bus()
            obj = bus.get_object("com.nokia.FMTx",
                                 "/com/nokia/fmtx/default",
                                 False, True)
            self.__fmtx = dbus.Interface(obj, "org.freedesktop.DBus.Properties")
        #end if


    def __send_rds(self):
    
        self.__prepare_dbus()
        if (self.__fmtx.Get("com.nokia.FMTx.Device", "state") == "enabled"):
            # thanks to Marcel J.E. Mol for this solution!
            self.__fmtx.Set("com.nokia.FMTx.Device", "rds_text",
                     dbus.String(u"%s" % self.__title[:64], variant_level = 1))
            self.__fmtx.Set("com.nokia.FMTx.Device", "rds_ps",
                     dbus.String(u"MediaBox", variant_level = 1))
        #end if


    def __on_change_fmtx(self, *args):
    
        print "FMTX CHANGED", args
        self.__prepare_dbus()
        if (self.__fmtx.Get("com.nokia.FMTx.Device", "state") == "enabled"):
            os.system("sudo /sbin/fm-boost &")
            self.emit_message(msgs.UI_ACT_SHOW_INFO,
                            "calling fm-boost to improve FM transmitter signal")

        
    def handle_MEDIA_EV_LOADED(self, nil, f):
    
        tags = tagreader.get_tags(f)
        self.__title = tags.get("TITLE")
        self.__send_rds()
        
        
    def handle_MEDIA_EV_PLAY(self):
    
        self.__is_playing = True
        
        
    def handle_MEDIA_EV_PAUSE(self):
    
        self.__is_playing = False

        
    def handle_MEDIA_EV_EOF(self):

        self.__is_playing = False

