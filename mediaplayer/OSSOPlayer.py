from GenericMediaPlayer import *

try:
    import gobject
    HAVE_GOBJECT = True
except:
    HAVE_GOBJECT = False
    

import dbus
import dbus.glib

import os
import fcntl
import subprocess
import time

import gobject


# connection timeout in seconds
_CONNECTION_TIMEOUT = 30
_LOGGING = False

_SERVICE_NAME = "com.nokia.osso_media_server"
_OBJECT_PATH = "/com/nokia/osso_media_server"
_MUSIC_PLAYER_IFACE = "com.nokia.osso_media_server.music"
_VIDEO_PLAYER_IFACE = "com.nokia.osso_media_server.video"

_FORMATS = (".ram", ".rm", ".rmvb")


class _OSSOPlayer(GenericMediaPlayer):
    """
    Singleton class for controlling and embedding the OSSO media server in
    other applications.
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
        self.__total_length = 0
        self.__time_of_check = 0
        
        self.__timeout_point = 0
        self.__next_time_check = 0

        self.__context_id = 0
        
        self.__bus = dbus.SessionBus(private = True)
        try:
            obj = self.__bus.get_object(_SERVICE_NAME, _OBJECT_PATH)
            self.__mplayer = dbus.Interface(obj, _MUSIC_PLAYER_IFACE)
            self.__mplayer.connect_to_signal("state_changed", self.__on_change_state)
            self.__mplayer.connect_to_signal("end_of_stream", self.__on_eos)
            self.__vplayer = dbus.Interface(obj, _VIDEO_PLAYER_IFACE)
            self.__vplayer.connect_to_signal("state_changed", self.__on_change_state)
            self.__vplayer.connect_to_signal("end_of_stream", self.__on_eos)

            self.__current_player = self.__vplayer
            self.__available = True            
            
        except:
            self.__available = False


    def handles(self, filetype):
    
        return (filetype in _FORMATS)


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
            if (self.__position == 0):
                try:            
                    pos, total = self.get_position()
                    self.__time_of_check = now
                except:
                    pos, total = 0, 0

                self.__position = pos
                self.__total_length = total
                
            else:
                pos = self.__position + now - self.__time_of_check
                total = self.__total_length
                self.__time_of_check = now
                self.__position = pos
            #end if

            self.update_observer(self.OBS_POSITION, self.__context_id,
                                 pos, total)
    
        else:
            self.__idle_counter += 1
            
            # check for connection timeout
            if (self.__timeout_point and not self.__broken and
                time.time() > self.__timeout_point):
                self.__timeout_point = 0
                #self.__broken = True
                self.update_observer(self.OBS_ERROR, self.__context_id,
                                     self.ERR_CONNECTION_TIMEOUT)

        #end if
        
        # close mplayer if we've been idle too long
        if (self.__idle_counter == 500):
            self.__idle_counter = 0
            self.__heartbeat_running = False
            #self.__needs_restart = True
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
    
    
    def __on_eos(self, uri):

        self.__playing = False
        self.__has_video = False
        self.__has_audio = False
        print "REACHED EOF"
        self.update_observer(self.OBS_EOF, self.__context_id)


    def is_available(self):
        """
        Returns whether the player is available on the system.
        """
        
        return self.__available
        

    def set_window(self, xid):
    
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
        self.__uri = uri
        self.__playing = False
        self.__has_video = False
        self.__has_audio = False
        self.__position = 0
        self.__media_length = -1
        self.__current_player.play_media(uri)

        self.__run_heartbeat()
        
        if (ctx_id != -1):
            self.__context_id = ctx_id
        else:
            self.__context_id += 1
        print "CTX", self.__context_id
        return self.__context_id
        


    def set_volume(self, volume):

        self.__current_player.set_volume(volume / 100.0)
        self.__volume = volume


    def play(self):
           
        if (not self.__playing):        
            #self.__playing = True
            self.__position = 0
            self.__position = 0
            self.set_volume(self.__volume)
            self.__current_player.play()
            #self.update_observer(self.OBS_PLAYING, self.__context_id)
        
        
    def pause(self):
          
        #self.__playing = not self.__playing        
        if (self.__playing):
            self.set_volume(self.__volume)
            self.__current_player.pause()
            self.__position = 0
            #self.update_observer(self.OBS_PLAYING, self.__context_id)
        else:
            self.__current_player.pause()
            #self.update_observer(self.OBS_STOPPED, self.__context_id)



    def close(self):
    
        self.stop()



    def stop(self):

        if (self.__playing):
            self.__playing = False
            self.__current_player.stop()
            #self.update_observer(self.OBS_STOPPED, self.__context_id)


    def seek(self, pos):
    
        self.__current_player.seek(1, dbus.Int32(pos * 1000))
        self.play()
        self.__position = 0


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

