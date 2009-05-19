from AbstractBackend import AbstractBackend
from utils import maemo

import dbus


_SERVICE_NAME = "com.nokia.osso_media_server"
_OBJECT_PATH = "/com/nokia/osso_media_server"
_MUSIC_PLAYER_IFACE = "com.nokia.osso_media_server.music"
_MUSIC_PLAYER_ERROR_IFACE = "com.nokia.osso_media_server.music.error"
_VIDEO_PLAYER_IFACE = "com.nokia.osso_media_server.video"
_VIDEO_PLAYER_ERROR_IFACE = "com.nokia.osso_media_server.video.error"


class OSSOBackend(AbstractBackend):
    """
    Backend implementation for controlling the osso-media-server.
    """

    def __init__(self):
        """
        Creates the OSSOBackend.
        """

        self.__current_player = None
        self.__mplayer = None
        self.__vplayer = None
        
        self.__width = 0
        self.__height = 0
        
        self.__is_seekable = False
        self.__is_eof = False

        AbstractBackend.__init__(self)


    def _get_icon(self):
    
        from theme import theme
        return theme.mb_backend_oms


    def __start_oms(self):
        
        bus = maemo.get_session_bus()
        try:
            obj = bus.get_object(_SERVICE_NAME, _OBJECT_PATH)
            self.__mplayer = dbus.Interface(obj, _MUSIC_PLAYER_IFACE)
            mplayer_err = dbus.Interface(obj, _MUSIC_PLAYER_ERROR_IFACE)
            self.__mplayer.connect_to_signal("state_changed", self.__on_change_state)
            self.__mplayer.connect_to_signal("end_of_stream", self.__on_eos)
            self.__mplayer.connect_to_signal("info_buffering", self.__on_buffering)
            self.__mplayer.connect_to_signal("details_received", self.__on_details)
            mplayer_err.connect_to_signal("unsupported_type", self.__on_unsupported)
            mplayer_err.connect_to_signal("type_not_found", self.__on_unsupported)            
            self.__vplayer = dbus.Interface(obj, _VIDEO_PLAYER_IFACE)
            vplayer_err = dbus.Interface(obj, _VIDEO_PLAYER_ERROR_IFACE)
            self.__vplayer.connect_to_signal("state_changed", self.__on_change_state)
            self.__vplayer.connect_to_signal("end_of_stream", self.__on_eos)
            self.__vplayer.connect_to_signal("info_buffering", self.__on_buffering)
            self.__vplayer.connect_to_signal("details_received", self.__on_details)
            vplayer_err.connect_to_signal("unsupported_type", self.__on_unsupported)
            vplayer_err.connect_to_signal("video_codec_not_supported", self.__on_unsupported)

            self.__current_player = self.__vplayer

        except:
            pass


    def _ensure_backend(self):
    
        if (not self.__current_player):
            self.__start_oms()


        
    def __on_change_state(self, state):
    
        if (state == "playing"):
            pass
        elif (state == "paused"):
            pass
        elif (state == "stopped"):
            pass
        elif (state == "connecting"):
            self._report_connecting()
    
    
    def __on_eos(self, uri):

        self.__is_eof = True


    def _is_eof(self):
    
        return self.__is_eof


    def __on_buffering(self, value):
    
        print "buffering", value
        if (value < 99.9):
            self._report_buffering(int(value))
        

    def __on_details(self, details):
    
        for key, value in details.items():
            print "%s: %s" % (key, value)
            if (key == "has_video"):
                pass
            elif (key == "seekable"):
                self.__is_seekable = (value == "1")
            elif (key == "width"):
                self.__width = int(value)
            elif (key == "height"):
                self.__height = int(value)
            elif (key == "title"):
                self._report_tag("TITLE", value)
            elif (key == "artist"):
                self._report_tag("ARTIST", value)
            elif (key == "album"):
                self._report_tag("ALBUM", value)
        #end for

        if (self.__width > 0 and self.__height > 0):
            self._report_aspect_ratio(self.__width / float(self.__height))
        
        

    def __on_unsupported(self, error):
    
        self._report_error(self.ERR_NOT_SUPPORTED, "")
        

    def _set_window(self, xid):
    
        self._ensure_backend()
        if (xid > 0):
            self.__vplayer.set_video_window(dbus.UInt32(xid))
        
        
    def _load(self, uri):
    
        if (self._get_mode() == self.MODE_AUDIO):
            self.__current_player = self.__mplayer
        else:
            self.__current_player = self.__vplayer
            
        if (uri.startswith("/")): uri = "file://" + uri
        uri = uri.replace("\"", "\\\"")

        self.__is_seekable = False
        self.__is_eof = False
        self.__width = 0
        self.__height = 0
        self.__current_player.play_media(uri)
        


    def _set_volume(self, volume):

        if (self.__current_player):
            self.__current_player.set_volume(volume / 100.0)


    def _play(self):
         
        self.__is_eof = False
        self.__current_player.play()
        
        
    def _stop(self):

        self.__current_player.pause()


    def _close(self):
    
        self.__current_player.stop()
        self.__current_player = None
        self.__mplayer = None
        self.__vplayer = None
        #os.system("killall osso-media-server")


    def _seek(self, pos):
    
        if (self.__is_seekable):
            self.__current_player.seek(1, dbus.Int32(pos * 1000))
            self._play()


    def _get_position(self):

        try:
            pos, total = self.__current_player.get_position()
        except:
            total = 0.0
            try:
                pos = self.__current_player.get_position()
            except:            
                pos = 0.0
            
        return (pos / 1000.0, total / 1000.0)

