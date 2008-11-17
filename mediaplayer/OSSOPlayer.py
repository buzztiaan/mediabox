from GenericMediaPlayer import *
from utils import maemo

try:
    import gobject
    HAVE_GOBJECT = True
except:
    HAVE_GOBJECT = False
    

import dbus

import os
import fcntl
import subprocess
import time

import gobject



# value keys
_NAME = 0
_ARTIST = 1
_GENRE = 2
_WEBSITE = 3

_ICY_INFO = 10

_VIDEO_WIDTH = 20
_VIDEO_HEIGHT = 21
_VIDEO_FPS = 22
_VIDEO_ASPECT = 23
_VIDEO_RESOLUTION = 24

_FILENAME = 30
_POSITION = 31
_PERCENT_POSITION = 32
_LENGTH = 33
_SEEKABLE = 34

_MAX_VALUES = 35       # for the array length


# connection timeout in seconds
_CONNECTION_TIMEOUT = 30
_LOGGING = False

_SERVICE_NAME = "com.nokia.osso_media_server"
_OBJECT_PATH = "/com/nokia/osso_media_server"
_MUSIC_PLAYER_IFACE = "com.nokia.osso_media_server.music"
_MUSIC_PLAYER_ERROR_IFACE = "com.nokia.osso_media_server.music.error"
_VIDEO_PLAYER_IFACE = "com.nokia.osso_media_server.video"
_VIDEO_PLAYER_ERROR_IFACE = "com.nokia.osso_media_server.video.error"


class _OSSOPlayer(GenericMediaPlayer):
    """
    Singleton class for controlling and embedding the OSSO media server in
    other applications.
    
    @todo: replace with gstreamer backend since the osso-media-server D-Bus
           API is private and subject to change
    """

    def __init__(self):
        """
        Creates the OSSOPlayer singleton.
        """

        GenericMediaPlayer.__init__(self)

        self.__heartbeat_running = False
        self.__idle_counter = 0

        self.__has_video = False
        self.__has_audio = False
        self.__playing = False
        
        self.__volume = 50

        self.__uri = ""
        self.__position = 0
        self.__position_valid = False
        self.__total_length = 0
        self.__time_of_check = 0
        
        self.__timeout_point = 0
        self.__next_time_check = 0
        
        self.__is_buffering = True

        self.__context_id = 0

        # table for collecting player values
        self.__player_values = [None] * _MAX_VALUES
        
        bus = maemo.get_session_bus()
        try:
            obj = bus.get_object(_SERVICE_NAME, _OBJECT_PATH)
            self.__mplayer = dbus.Interface(obj, _MUSIC_PLAYER_IFACE)
            self.__mplayer_err = dbus.Interface(obj, _MUSIC_PLAYER_ERROR_IFACE)
            self.__mplayer.connect_to_signal("state_changed", self.__on_change_state)
            self.__mplayer.connect_to_signal("end_of_stream", self.__on_eos)
            self.__mplayer.connect_to_signal("info_buffering", self.__on_buffering)
            self.__mplayer.connect_to_signal("details_received", self.__on_details)
            self.__mplayer_err.connect_to_signal("unsupported_type", self.__on_unsupported)
            self.__mplayer_err.connect_to_signal("type_not_found", self.__on_unsupported)            
            self.__vplayer = dbus.Interface(obj, _VIDEO_PLAYER_IFACE)
            self.__vplayer_err = dbus.Interface(obj, _VIDEO_PLAYER_ERROR_IFACE)
            self.__vplayer.connect_to_signal("state_changed", self.__on_change_state)
            self.__vplayer.connect_to_signal("end_of_stream", self.__on_eos)
            self.__vplayer.connect_to_signal("info_buffering", self.__on_buffering)
            self.__vplayer.connect_to_signal("details_received", self.__on_details)
            self.__vplayer_err.connect_to_signal("unsupported_type", self.__on_unsupported)
            self.__vplayer_err.connect_to_signal("video_codec_not_supported", self.__on_unsupported)

            self.__current_player = self.__vplayer
            self.__available = True            
            
        except:
            self.__available = False



    def handle_expose(self, src, gc, x, y, w, h):
    
        src.draw_rectangle(gc, True, x, y, w, h)


    def __run_heartbeat(self):
        """
        Runs the heartbeat function if GObject is available and it's not
        already running.
        """
    
        if (HAVE_GOBJECT and not self.__heartbeat_running):
            self.__hearbeat_running = True
            self.__heartbeat()
        
                        
            
    def __heartbeat(self):
        """
        Regularly checks the player status and sends events to its listeners.
        """

        if (self.__playing):
            self.__idle_counter = 0            
            now = time.time()

            # don't ask mplayer for the current position every time, because
            # this is highly inefficient with Ogg Vorbis files
            if (not self.__position_valid or now - self.__time_of_check > 1):
                try:
                    pos, total = self.get_position()
                    self.__position_valid = True
                except:
                    import traceback; traceback.print_exc()
                    pos, total = 0, 0

                self.__position = pos
                self.__total_length = total
                self.__time_of_check = now
                
            else:
                pos = self.__position + now - self.__time_of_check
                total = self.__total_length
                #self.__time_of_check = now
                #self.__position = pos
            #end if

            self.update_observer(self.OBS_POSITION, self.__context_id,
                                 pos, total)
    
        else:
            self.__idle_counter += 1
            
            # check for connection timeout
            if (self.__timeout_point and not self.__broken and
                time.time() > self.__timeout_point):
                self.__timeout_point = 0
                self.update_observer(self.OBS_ERROR, self.__context_id,
                                     self.ERR_CONNECTION_TIMEOUT)

        #end if
        
        # close player if we've been idle for too long
        if (self.__idle_counter == 500):
            self.__idle_counter = 0
            self.__heartbeat_running = False
        #    self.close()
            print "player closed due to idle timeout"
            return False
           
        gobject.timeout_add(300, self.__heartbeat)

        
    def __on_change_state(self, state):
    
        if (state == "playing"):
            self.__playing = True
            self.update_observer(self.OBS_PLAYING, self.__context_id)
        elif (state == "paused"):
            self.__playing = False
            self.update_observer(self.OBS_STOPPED, self.__context_id)
        elif (state == "stopped"):
            self.__playing = False
            self.update_observer(self.OBS_STOPPED, self.__context_id)
        elif (state == "connecting"):
            self.__playing = False
            self.update_observer(self.OBS_BUFFERING, self.__context_id)
    
    
    def __on_eos(self, uri):

        self.__playing = False
        self.__has_video = False
        self.__has_audio = False
        print "REACHED EOF"
        self.update_observer(self.OBS_EOF, self.__context_id)


    def __on_buffering(self, value):
    
        if (value < 99.9):
            if (not self.__is_buffering):
                self.__is_buffering = True
                self.update_observer(self.OBS_BUFFERING, self.__context_id)                
        else:
            self.__is_buffering = False
        

    def __on_details(self, details):
    
        self.__has_aspect = 0
        for key, value in details.items():
            print "%s: %s" % (key, value)
            if (key == "has_video"):
                self.__has_video = (value == "1")
            elif (key == "seekable"):
                self.__player_values[_SEEKABLE] = (value == "1")
            elif (key == "width"):
                self.__player_values[_VIDEO_WIDTH] = int(value)
                self.__has_aspect |= 1
            elif (key == "height"):
                self.__player_values[_VIDEO_HEIGHT] = int(value)
                self.__has_aspect |= 2
        #end for
        
        if (self.__has_aspect & 3):
            try:
                video_aspect = self.__player_values[_VIDEO_WIDTH] / \
                               float(self.__player_values[_VIDEO_HEIGHT])
                self.__player_values[_VIDEO_ASPECT] = video_aspect
                self.update_observer(self.OBS_ASPECT, self.__context_id,
                                     video_aspect)
            except:
                import traceback; traceback.print_exc()            
        
        

    def __on_unsupported(self, error):
    
        self.update_observer(self.OBS_ERROR, self.__context_id,
                             self.ERR_NOT_SUPPORTED)
    
    


    def is_available(self):
        """
        Returns whether the player is available on the system.
        """
        
        return self.__available
        

    def set_window(self, xid):
    
        if (xid > 0):
            self.__vplayer.set_video_window(dbus.UInt32(xid))
        
        
    def set_options(self, opts):
    
        pass


    def load_audio(self, uri):
    
        self.__current_player = self.__mplayer
        return self.load(uri)


    def load_video(self, uri):
    
        self.__current_player = self.__vplayer
        return self.load(uri)
        

    def load(self, uri, ctx_id = -1):
       
        if (uri.startswith("/")): uri = "file://" + uri
        uri = uri.replace("\"", "\\\"")

        self.__uri = uri
        self.__playing = False
        self.__has_video = False
        self.__has_audio = True
        self.__position_valid = False
        self.__current_player.play_media(uri)
        self.set_volume(self.__volume)

        self.__run_heartbeat()
        
        if (ctx_id != -1):
            self.__context_id = ctx_id
        else:
            self.__context_id = self._new_context_id()
        print "CTX", self.__context_id
        return self.__context_id
        


    def set_volume(self, volume):

        self.__current_player.set_volume(volume / 100.0)
        self.__volume = volume


    def play(self):
           
        if (not self.__playing):
            self.__run_heartbeat()
            self.__position_valid = False
            self.__current_player.play()
            self.set_volume(self.__volume)            
        
        
    def pause(self):
          
        if (self.__playing):
            self.set_volume(self.__volume)
            self.__current_player.pause()
            self.__position = 0
        else:
            self.__run_heartbeat()
            self.__current_player.pause()



    def close(self):
    
        self.stop()        
        self.__context_id = 0
        #os.system("killall osso-media-server")



    def stop(self):

        if (self.__playing):
            self.__playing = False
            self.__current_player.stop()


    def seek(self, pos):
    
        if (self.__player_values[_SEEKABLE]):
            self.__run_heartbeat()
            self.__current_player.seek(1, dbus.Int32(pos * 10))
            self.play()
            self.__position_valid = False


    def seek_percent(self, pos):
    
        self.seek(pos * self.__total_length)


    def get_position(self):

        try:
            pos, total = self.__current_player.get_position()
        except:
            total = 0.0
            try:
                pos = self.__current_player.get_position()
            except:            
                pos = 0.0
            
        return (pos / 1000.0, total / 1000.0)
        
        
    def show_text(self, text, duration):

        # not available
        pass
        

    def is_playing(self):
        """
        Returns whether MPlayer is currently playing.
        """
    
        return self.__playing
    
    
    
    def has_video(self):
        """
        Returns whether the current media has a video stream.
        """
        
        return self.__has_video


    def has_audio(self):
        """
        Returns whether the current media has an audio stream.
        """
        
        return self.__has_audio               
        


_singleton = _OSSOPlayer()
def OSSOPlayer(): return _singleton

