from AbstractBackend import AbstractBackend
import platforms
from utils import logging

import gobject
import pygst; pygst.require("0.10")
import gst
import dbus
import os
import time


class GstBackend(AbstractBackend):
    """
    Backend implementation for GStreamer.
    """

    def __init__(self):
        """
        Creates the GstBackend.
        """
        
        self.__is_eof = False
        self.__player = None
        self.__window_id = 0
        
        self.__to_seek = 0
        
        # time when MediaBox has last changed the sound volume
        self.__last_volume_change_time = 0
        
        self.__volume = 50
        
        # set up device volume listener on the N900
        if (platforms.MAEMO5):
            bus = platforms.get_session_bus()
            bus.add_signal_receiver(self.__on_change_volume,
                                    signal_name = "property_changed",
                                    dbus_interface = "com.nokia.mafw.extension",
                                    path = "/com/nokia/mafw/renderer/gstrenderer")

            # retrieve initial volume
            self.__volume = self.__get_current_volume()

        AbstractBackend.__init__(self)


    def _get_icon(self):
    
        from theme import theme
        return theme.mb_backend_gstreamer


    def __get_current_volume(self):
    
        if (platforms.MAEMO5):
            bus = platforms.get_session_bus()
            obj = bus.get_object("com.nokia.mafw.renderer.Mafw-Gst-Renderer-Plugin.gstrenderer",
                                 "/com/nokia/mafw/renderer/gstrenderer")
            mafw = dbus.Interface(obj, "com.nokia.mafw.extension")
            volume = int(mafw.get_extension_property("volume")[1])
        else:
            if (self.__player):
                volume = self.__player.get_property("volume") * 100
            else:
                volume = self.__volume
        
        return volume        


    def __start_gst(self):

        if (platforms.MAEMO5):
            # normal playbin is broken on Maemo5
            self.__player = gst.element_factory_make("playbin2", "player")
        else:
            # playbin2 is considered experimental elsewhere
            self.__player = gst.element_factory_make("playbin", "player")
            
        bus = self.__player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.__on_message)
        bus.connect("sync-message::element", self.__on_sync_message)
        self.__bus = bus
        
        
    def _ensure_backend(self):
    
        if (not self.__player):
            self.__start_gst()
        
        
    def __on_message(self, bus, message):
    
        t = message.type
        #print "Message Type", t
        if (t == gst.MESSAGE_STATE_CHANGED):
            prev, new, pend = message.parse_state_changed()
            if (new == gst.STATE_PLAYING and self.__to_seek):
                self._seek(self.__to_seek)
                self.__to_seek = 0
        
        elif (t == gst.MESSAGE_EOS):        
            self.__player.set_state(gst.STATE_NULL)
            self.__is_eof = True

        elif (t == gst.MESSAGE_ELEMENT):
            s = message.structure
            if (s.has_name("redirect")):     
                url = s["new-location"]
                logging.debug("GStreamer got redirect: %s", url)
                self.__player.set_state(gst.STATE_NULL)
                self.__player.set_property("uri", url)
                self.__player.set_state(gst.STATE_PLAYING)

        elif (t == gst.MESSAGE_BUFFERING):
            self._report_buffering(0)
            #query = gst.query_new_buffering(gst.FORMAT_PERCENT)
            #if (self.__player.query(query)):
            #    fmt, start, stop, total = query.parse_buffering_range()
            #    print fmt, start, stop, total

        elif (t == gst.MESSAGE_ERROR):
            self.__player.set_state(gst.STATE_READY)
            err, debug = message.parse_error()
            logging.error("GStreamer Error:\n%s\n%s", err, debug)
            self._report_error(self.ERR_INVALID, "")

        elif (t == gst.MESSAGE_TAG):
            tags = message.parse_tag()
            for key in tags.keys():
                #print key #, tags[key]
                if (key == "title"):
                    self._report_tag("TITLE", tags[key])
                elif (key == "artist"):
                    self._report_tag("ARTIST", tags[key])
                elif (key == "album"):
                    self._report_tag("ALBUM", tags[key])
                elif (key == "bitrate"):
                    print "Bitrate: %0.1f kbps" % (tags[key] / 1000.0)
                elif (key == "image"):
                    if (type(tags[key]) == list):
                        self._report_tag("PICTURE", tags[key][0].data)
                    else:
                        self._report_tag("PICTURE", tags[key].data)
                    print "Found cover image"
            #end for
    

    def __on_sync_message(self, bus, message):
    
        if (message.structure == None): return
        
        name = message.structure.get_name()
        if (name == "prepare-xwindow-id" and self.__window_id != -1):
            imgsink = message.src
            imgsink.set_property("force-aspect-ratio", True)
            imgsink.set_xwindow_id(self.__window_id)


    def __on_change_volume(self, key, value):
        """
        Reacts on changing the system volume on the N900.
        """
    
        # only accept system volume change notifications if the last app
        # volume change has been some time ago
        if (key == "volume" and time.time() > self.__last_volume_change_time + 1):
            self.__volume = value
            self._report_volume(value)


    def _set_window(self, xid):
    
        self.__window_id = xid
        

    def _load(self, uri):

        if (uri.startswith("/")): uri = "file://" + uri
        uri = uri.replace("\"", "\\\"")
        
        self.__player.set_state(gst.STATE_NULL)
        self.__start_gst()

        self.__player.set_property("uri", uri)
        self.__player.set_state(gst.STATE_PLAYING)
        self.__player.seek_simple(gst.Format(gst.FORMAT_TIME),
                                  gst.SEEK_FLAG_FLUSH,
                                  0)
        self._report_aspect_ratio(16/9.0)
        if (not platforms.MAEMO5):
            self._set_volume(self.__volume)
        self._report_volume(self.__volume)
        


    def _set_volume(self, volume):

        if (volume == self.__volume): return

        if (platforms.MAEMO5):
            # ugly as hell... but does its job
            print "SET SYSTEM VOLUME", volume
            os.system("dbus-send --session --print-reply " \
                      "--dest=com.nokia.mafw.renderer.Mafw-Gst-Renderer-Plugin.gstrenderer " \
                      "/com/nokia/mafw/renderer/gstrenderer " \
                      "com.nokia.mafw.extension.set_extension_property " \
                      "string:'volume' variant:uint32:%d 2>/dev/null &" \
                      % volume)
        else:
            if (self.__player):
                self.__player.set_property("volume", volume / 100.0)

        self._report_volume(volume)
        self.__last_volume_change_time = time.time()
        self.__volume = volume

    
    def _is_eof(self):
    
        return self.__is_eof


    def _play(self):
           
        self.__is_eof = False
        self.__player.set_state(gst.STATE_PLAYING)


    def _stop(self):

        self.__player.set_state(gst.STATE_PAUSED)


    def _close(self):
    
        if (self.__player):
            self.__player.set_state(gst.STATE_NULL)
            self.__player = None


    def _seek(self, pos):
    
        if (self.__player):
            self.__pos_time = (0, 0, 0)
            state = self.__player.get_state()[1]
            if (state == gst.STATE_PLAYING):
                self.__player.seek_simple(gst.Format(gst.FORMAT_TIME),
                                          gst.SEEK_FLAG_FLUSH,
                                          pos * 1000000000)
            else:
                self.__player.set_state(gst.STATE_PLAYING)
                self.__to_seek = pos
        #end if
        

    def _get_position(self):

        try:
            pos, format = self.__player.query_position(gst.FORMAT_TIME)
            total, format = self.__player.query_duration(gst.FORMAT_TIME)
            
            # gstreamer time is in nano seconds... weird! :o
            pos /= 1000000000
            total /= 1000000000
            
        except:
            # the query may fail
            pos, total = (-1, -1)
        
        return (pos, total)

