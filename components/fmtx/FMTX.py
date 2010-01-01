from com import Component, msgs
from mediabox import tagreader
import platforms

import dbus

#dbus-send --system --print-reply --dest=com.nokia.FMTx /com/nokia/fmtx/default org.freedesktop.DBus.Properties.Get string:'com.nokia.FMTx.Device' string:'rds_ps'

class FMTX(Component):

    def __init__(self):
    
        self.__fmtx = None
        self.__is_playing = False
        self.__title = ""
    
        Component.__init__(self)
        

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
            # doesn't work
            #self.__fmtx.Set("com.nokia.FMTx.Device", "rds_text",
            #                dbus.Array([dbus.String(self.__title[:64])]))

            # works, but is ugly
            import os
            os.system("/usr/bin/dbus-send --system --dest=com.nokia.FMTx " \
                      "/com/nokia/fmtx/default " \
                      "org.freedesktop.DBus.Properties.Set " \
                      "string:'com.nokia.FMTx.Device' string:'rds_text' " \
                      "variant:string:'%s'" % self.__title[:64])

            os.system("/usr/bin/dbus-send --system --dest=com.nokia.FMTx " \
                      "/com/nokia/fmtx/default " \
                      "org.freedesktop.DBus.Properties.Set " \
                      "string:'com.nokia.FMTx.Device' string:'rds_ps' " \
                      "variant:string:'MediaBox'")


        #end if

        
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

