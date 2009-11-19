from AbstractBackend import AbstractBackend
    
import pygst; pygst.require("0.10")
import gst


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
        
        
        AbstractBackend.__init__(self)


    def _get_icon(self):
    
        from theme import theme
        return theme.mb_backend_gstreamer
        

    def __start_gst(self):

        self.__player = gst.element_factory_make("playbin2", "player")
        bus = self.__player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.__on_message)
        bus.connect("sync-message::element", self.__on_sync_message) 
        
        
    def _ensure_backend(self):
    
        if (not self.__player):
            self.__start_gst()
        
        
    def __on_message(self, bus, message):
    
        t = message.type
        #print "Message Type", t
        if (t == gst.MESSAGE_EOS):        
            self.__player.set_state(gst.STATE_NULL)
            self.__is_eof = True

        elif (t == gst.MESSAGE_ERROR):
            self.__player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            self._report_error(self.ERR_INVALID, "")

        elif (t == gst.MESSAGE_TAG):
            #print message
            pass


    def __on_sync_message(self, bus, message):
    
        if (message.structure == None): return
        
        name = message.structure.get_name()

        if (name == "prepare-xwindow-id" and self.__window_id != -1):
            imgsink = message.src
            imgsink.set_property("force-aspect-ratio", True)
            imgsink.set_xwindow_id(self.__window_id)


    def _set_window(self, xid):
    
        self.__window_id = xid
        

    def _load(self, uri):
       
        if (uri.startswith("/")): uri = "file://" + uri
        uri = uri.replace("\"", "\\\"")

        self.__player.set_state(gst.STATE_NULL)
        self.__player.set_property("uri", uri)
        self.__player.seek_simple(gst.Format(gst.FORMAT_TIME),
                                  gst.SEEK_FLAG_FLUSH,
                                  0)
        self._report_aspect_ratio(16/9.0)
        


    def _set_volume(self, volume):

        self.__player.set_property("volume", volume / 1000.0)

    
    def _is_eof(self):
    
        return self.__is_eof


    def _play(self):
           
        self.__is_eof = False
        self.__player.set_state(gst.STATE_PLAYING)


    def _stop(self):

        self.__player.set_state(gst.STATE_PAUSED)


    def _close(self):
    
        self._stop()


    def _seek(self, pos):
    
        self.__pos_time = (0, 0, 0)
        self.__player.seek_simple(gst.Format(gst.FORMAT_TIME),
                                  gst.SEEK_FLAG_FLUSH,
                                  pos * 1000000000)


    def _get_position(self):

        try:
            pos, format = self.__player.query_position(gst.FORMAT_TIME)
            total, format = self.__player.query_duration(gst.FORMAT_TIME)
            
            # gstreamer time is in nano seconds... weird! :o
            pos /= 1000000000
            total /= 1000000000
            
        except:
            pos, total = (0, 0)
        
        return (pos, total)

