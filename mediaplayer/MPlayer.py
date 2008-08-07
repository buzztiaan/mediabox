from GenericMediaPlayer import *
from utils import logging

import gobject
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

_MAX_VALUES = 34        # for the array length


# connection timeout in seconds
_CONNECTION_TIMEOUT = 30

# idle timeout in milliseconds
_IDLE_TIMEOUT = 1000 * 60 * 3

_LOGGING = True

# path to the mplayer executable
_MPLAYER = "/usr/bin/mplayer"



class _MPlayer(GenericMediaPlayer):
    """
    Singleton class for controlling and embedding mplayer in other applications.
    """            

    def __init__(self):
        """
        Creates the MPlayer singleton.
        """

        GenericMediaPlayer.__init__(self)

        self.__xid = -1
        self.__opts = ""
        
        self.__stdin = None
        self.__stdout = None
        self.__has_video = False
        self.__has_audio = False
        self.__playing = False
        
        self.__volume = 50
        
        self.__needs_restart = False
        self.__media_length = -1

        self.__video_width = 0
        self.__video_height = 0
        self.__video_aspect = 0
        
        self.__uri = ""
        
        self.__timeout_point = 0
        self.__suspension_point = None
        
        self.__context_id = 0

        self.__collect_handler = None
        self.__position_handler = None
        self.__idle_handler = None
        
        # table for collecting player values
        self.__player_values = [None] * _MAX_VALUES



    def handle_expose(self, src, gc, x, y, w, h):

        w, h = src.get_size()
        src.draw_rectangle(gc, False, w - 1, 0, 1, h)
        src.draw_rectangle(gc, False, 0, h - 1, w, 1)    


    def __on_idle_timeout(self):
        """
        Reacts on idle timeout and suspends mplayer.
        """

        print "IDLE TIMEOUT"
        gobject.source_remove(self.__idle_handler)
        self.__idle_handler = None
        
        pos = float(self.__player_values[_POSITION] or 0)
        self.__suspension_point = (self.__uri, pos)
        self.__stop_mplayer()



    def __on_eof(self):
        """
        Reacts on end-of-file.
        """

        self.__playing = False
        print "REACHED EOF"
        self.__suspension_point = (self.__uri, 0)
        self.update_observer(self.OBS_EOF, self.__context_id)



    def __update_position(self, timestamp, beginpos):
        """
        Keeps the position counter updated without querying mplayer all the
        time. Querying the position is an expensive operation with Ogg-Vorbis
        files.
        """

        if (self.__playing):    
            #pos = float(self.__player_values[_POSITION] or 0)
            total = float(self.__player_values[_LENGTH] or 0)
            pos = beginpos + (time.time() - timestamp)
            self.__player_values[_POSITION] = pos
            
            self.__position_handler = \
                  gobject.timeout_add(500, self.__update_position,
                                      timestamp, beginpos)

            self.update_observer(self.OBS_POSITION, self.__context_id,
                                 pos, total)

            if (total > 0.001 and total - pos < 0.01):
                self.__on_eof()
                
            if (total < 0.001):
                self.__send_cmd("get_time_length")                

        else:
            self.__position_handler = None

        # reset idle timeout
        if (self.__idle_handler):
            gobject.source_remove(self.__idle_handler)
        self.__idle_handler = gobject.timeout_add(_IDLE_TIMEOUT,
                                                  self.__on_idle_timeout)


    def __on_position(self):
        """
        Reacts on reading a position information from mplayer.
        """
    
        if (self.__position_handler):
            gobject.source_remove(self.__position_handler)
            
        pos = float(self.__player_values[_POSITION] or 0)
        self.__position_handler = \
                 gobject.timeout_add(0, self.__update_position,
                                     time.time(), pos)



    def __on_icy_info(self):
        """
        Reacts on reading ICY info (metatags) from mplayer.
        """
    
        title = self.__player_values[_ICY_INFO]
        self.update_observer(self.OBS_NEW_STREAM_TRACK,
                             self.__context_id, title)
        self.__player_values[_ICY_INFO] = None    


    def __wait_for(self, key):
        """
        Waits (with a timeout) until the given key has a value.
        """
    
        cnt  = 0
        while (not self.__player_values[key] and cnt < 500):
            #self.__collect_values()
            time.sleep(0.001)
            cnt += 1
        print cnt
        

    def wait_for_video_aspect(self):
    
        self.__wait_for(_VIDEO_ASPECT)


    def __send_cmd(self, data):
    
        logging.debug("mplayer command:\n%s" % data)
        try:
            self.__stdin.write(data + "\n")
        except:
            self.__needs_restart = True
        
        
    def __read(self):
                
        data = self.__stdout.read(1024)
        logging.debug("mplayer output:\n%s" % data)
        return data        



    def __on_collect_values(self, sock, cond, buf):
        
        if (cond == gobject.IO_HUP):
            self.__collect_handler = None
            return False
            
        else:
            buf[0] += self.__read()
            idx = buf[0].find("\n")
            while (idx >= 0):
                line = buf[0][:idx]
                buf[0] = buf[0][idx + 1:]
                self.__parse_value(line)
                idx = buf[0].find("\n")
            #end while
            
            return True
        #end if
        
                  
        
    def __read_ans(self, data):

        idx = data.find("=")
        value = data[idx + 1:].strip()
        return value
        
        
    def __read_info(self, data):
    
        idx = data.find(":")
        value = data[idx + 1:].strip()
        return value
        
        
    def __parse_value(self, data):
    
        #print "PARSE", data
        if (not data and self.__playing and
            float(self.__player_values[_LENGTH] or 0) < 0.01):
            self.__on_eof()
        elif (data.startswith("ANS_TIME_POSITION")):
            self.__player_values[_POSITION] = self.__read_ans(data)
            self.__on_position()
        elif (data.startswith("ANS_PERCENT_POSITION")):
            self.__player_values[_PERCENT_POSITION] = self.__read_ans(data)
        elif (data.startswith("ANS_LENGTH")):
            self.__player_values[_LENGTH] = self.__read_ans(data)
        elif (data.startswith("ANS_VIDEO_RESOLUTION")):
            self.__player_values[_VIDEO_RESOLUTION] = self.__read_ans(data)
        elif (data.startswith("ANS_filename")):
            self.__player_values[_FILENAME] = self.__read_ans(data)
        elif (data.startswith("ANS_volume")):
            print "VOLUME", self.__read_ans(data)

        elif (data.startswith("AUDIO: ")):
            self.__has_audio = True
        elif (data.startswith("VIDEO: ")):
            self.__has_video = True

        elif (data.startswith("ID_VIDEO_WIDTH")):
            self.__player_values[_VIDEO_WIDTH] = float(self.__read_ans(data))
        elif (data.startswith("ID_VIDEO_HEIGHT")):
            self.__player_values[_VIDEO_HEIGHT] = float(self.__read_ans(data))
            try:
                self.__video_aspect = self.__player_values[_VIDEO_WIDTH] / \
                                      self.__player_values[_VIDEO_HEIGHT]
                self.__player_values[_VIDEO_ASPECT] = self.__video_aspect
                self.__send_cmd("switch_ratio %f" % self.__video_aspect)
                self.update_observer(self.OBS_ASPECT, self.__context_id,
                                     self.__video_aspect)
            except:
                import traceback; traceback.print_exc()

        elif (data.startswith("ID_LENGTH")):
            self.__media_length = float(self.__read_ans(data))

        elif (data.startswith("Name   : ")):
            self.__player_values[_NAME] = self.__read_info(data)
        elif (data.startswith("Genre  : ")):
            self.__player_values[_GENRE] = self.__read_info(data)
        elif (data.startswith("Website: ")):
            self.__player_values[_WEBSITE] = self.__read_info(data)
       
        elif (data.startswith("ICY Info: ")):
            self.__player_values[_ICY_INFO] = \
              self.__parse_icy_info(self.__read_info(data))
            
        elif (data.startswith("Demuxer info Name changed to ")):
            idx = data.find("changed to ")
            name = data[idx + 11:].strip()
            self.__player_values[_NAME] = name
            self.__player_values[_ICY_INFO] = name
            self.__on_icy_info()

        elif (data.startswith("Demuxer info Artist changed to ")):
            idx = data.find("changed to ")
            artist = data[idx + 11:].strip()
            self.__player_values[_ARTIST] = artist
            self.__player_values[_ICY_INFO] = self.__player_values[_NAME] + \
                                              " - " + artist
            self.__on_icy_info()
        
        elif (data.startswith("Starting playback...")):
            self.__playing = True
            self.__timeout_point = 0            
            self.set_volume(self.__volume)
            self.__send_cmd("get_time_pos")
            self.update_observer(self.OBS_PLAYING, self.__context_id)
            
        elif (data.startswith("File not found: ")):
            self.update_observer(self.OBS_ERROR, self.__context_id,
                                 self.ERR_NOT_FOUND)
        elif (data.startswith("[file] No filename")):
            self.update_observer(self.OBS_ERROR, self.__context_id,
                                 self.ERR_NOT_FOUND)
        elif (data.startswith("Cache size set to ")):
            self.update_observer(self.OBS_BUFFERING, self.__context_id)
        elif (data.endswith("No stream found.\n")):
            self.update_observer(self.OBS_ERROR, self.__context_id,
                                 self.ERR_NOT_FOUND)
        elif (" failed to load: " in data):
            self.update_observer(self.OBS_ERROR, self.__context_id,
                                 self.ERR_INVALID)
        elif (data.startswith("Error opening/initializing ")):
            self.update_observer(self.OBS_ERROR, self.__context_id,
                                 self.ERR_INVALID)            



    def __parse_icy_info(self, data):
        
        key = "StreamTitle='"
        idx = data.find(key)
        if (idx != -1):
            idx2 = data.find("';", idx + len(key))
            return data[idx + len(key):idx2]
        return ""
        
        
    def __expect(self, key, must_be_new):
    
        if (must_be_new):
            self.__player_values[key] = None
        cnt = 0
        while (self.__player_values[key] == None and cnt < 50):
            #self.__collect_values()
            time.sleep(0.001)
            cnt += 1
        #end while
            
        return self.__player_values[key]
        

       
    def is_available(self):
        """
        Returns whether mplayer is available on the system.
        """
        
        return os.path.exists(_MPLAYER)
        
        
    def set_window(self, xid):
        """
        Sets the X window to use for rendering content.
        """
    
        if (self.__xid != xid):
            self.__xid = xid
            self.__needs_restart = True
            self.__suspension_point = None


    def set_options(self, opts):
        """
        Sets command line options to use for mplayer.
        """
    
        if (self.__opts != opts):
            self.__opts = opts
            self.__needs_restart = True
            self.__suspension_point = None
        
        
        
    def __stop_mplayer(self):
        """
        Stops the currently running mplayer.
        """
        
        self.__playing = False
        self.__has_video = False
        self.__has_audio = False

        self.update_observer(self.OBS_KILLED)
        
        #if (self.__stdin): self.__stdin.write("quit\n")
        os.system("killall mplayer 2>/dev/null >/dev/null")
        time.sleep(0.25)
        os.system("killall -9 mplayer 2>/dev/null >/dev/null")
        self.__stdin = None
        self.__stdout = None
        
        if (self.__collect_handler):
            gobject.source_remove(self.__collect_handler)
            self.__collect_handler = None
                

            
            
    def __start_mplayer(self, xid, opts):
        """
        Starts a new mplayer process and connects to it.
        """
    
        print "Starting MPlayer"
        self.__playing = False
        
        cmd = "LANG=C %s -quiet -slave " \
              "-noconsolecontrols -nojoystick -nolirc -nomouseinput " \
              "-idle -osdlevel 0 -idx " \
              "-cache 256 -cache-min 50 " \
              "-identify -wid %d %s 2>&1 3>/dev/null" % (_MPLAYER, xid, opts)
        p = subprocess.Popen([cmd],
                             shell=True, cwd="/tmp",
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             close_fds=True)

        time.sleep(0.25)
        if (p.poll()):
            print "Startup failed"
            raise MPlayerNotFoundError()
        else:
            print "running"
        
        self.__stdin = p.stdin
        self.__stdout = p.stdout
        self.__xid = xid
        self.__opts = opts

        # set non-blocking for better performance in an unthreaded environment
        fcntl.fcntl(self.__stdout, fcntl.F_SETFL, os.O_NONBLOCK)
        
        if (not self.__collect_handler):
            self.__collect_handler = gobject.io_add_watch(self.__stdout,
                                                gobject.IO_HUP | gobject.IO_IN,
                                                    self.__on_collect_values,
                                                    [""])

        self.update_observer(self.OBS_STARTED)
        
        
        
    def __ensure_mplayer(self):
        """
        Makes sure that mplayer is running.
        """

        if (self.__needs_restart):        
            self.__stop_mplayer()
            self.__needs_restart = False

        if (not self.__stdin):
            self.__start_mplayer(self.__xid, self.__opts)        

        if (self.__suspension_point):
            uri, pos = self.__suspension_point
            self.load(uri, self.__context_id)
            self.seek(pos)
            #self.__playing = True

        

    
    
    
    def close(self):
        """
        Closes MPlayer. Your program should invoke this method on exit.
        """
    
        self.__stop_mplayer()
        self.__uri = ""


    def load(self, filename, ctx_id = -1):
        """
        Loads and plays the given media file.
        """
    
        self.__uri = ""        
        self.__suspension_point = None
        self.__ensure_mplayer()
        
        filename = filename.replace("\"", "\\\"")
        self.__send_cmd("loadfile \"%s\"" % filename)

        self.__playing = False
        self.__has_video = False
        self.__has_audio = False
        self.__media_length = -1
        self.__uri = filename

        self.__player_values[_FILENAME] = filename
        self.__player_values[_LENGTH] = None

        # reset position bar
        self.update_observer(self.OBS_POSITION, self.__context_id, 0, 0.01)

        self.__timeout_point = time.time() + _CONNECTION_TIMEOUT

        if (ctx_id != -1):
            self.__context_id = ctx_id
        else:
            self.__context_id = self._new_context_id()
        print "CTX", self.__context_id
        return self.__context_id
        
            
    
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
        
        
        
    def set_speed(self, n):
    
        self.__ensure_mplayer()
        
        self.__send_cmd("speed_set %d" % n)
    
    
        
    def play(self):

        self.__ensure_mplayer()
            
        if (not self.__playing):
            self.__playing = True
            self.set_volume(self.__volume)
            self.__send_cmd("play")
            self.update_observer(self.OBS_PLAYING, self.__context_id)
            
        self.__send_cmd("get_time_pos")            
        
        
    def pause(self):

        self.__ensure_mplayer()
            
        self.__playing = not self.__playing        
        if (self.__playing):
            self.set_volume(self.__volume)
            self.__send_cmd("pause")
            self.__send_cmd("get_time_pos")
            self.update_observer(self.OBS_PLAYING, self.__context_id)
        else:
            self.__send_cmd("pause")
            self.update_observer(self.OBS_STOPPED, self.__context_id)
                    
        
    def stop(self):

        self.__ensure_mplayer()
        
        if (self.__playing):
            self.__playing = False
            self.__send_cmd("pause")
            self.update_observer(self.OBS_STOPPED, self.__context_id)


    def seek(self, pos):
    
        self.__ensure_mplayer()
        self.__send_cmd("seek %d 2" % pos)
        self.play()


    def seek_percent(self, pos):

        self.__ensure_mplayer()    
        self.__send_cmd("seek %d 1" % pos)
        self.play()



    def get_position(self):

        self.__ensure_mplayer()
            
        self.__send_cmd("get_percent_pos")
        try:
            pos = float(self.__expect(_PERCENT_POSITION, True)) / 100
        except:
            #import traceback; traceback.print_exc()
            pos = 0.0
        
        if (self.__media_length < 0):
            self.__send_cmd("get_time_length")
            try:
                total = float(self.__expect(_LENGTH, True))
            except:
                total = 0.0
            self.__media_length = total
        else:
            total = self.__media_length

        return (total * pos, total)


    def get_resolution(self):

        self.__ensure_mplayer()
            
        self.__send_cmd("get_video_resolution")
        value = self.__expect(_VIDEO_RESOLUTION, False)[1:-1]
        
        if (value):
            parts = value.split(" x ")
            width = int(parts[0].strip())
            height = int(parts[1].strip())

            return (width, height)
        else:
            return (0, 0)
            
            
    def get_ratio(self):
    
        w, h = self.get_resolution()
        return w / float(h)


    def set_volume(self, volume):

        #self.__ensure_mplayer()
        if (self.__playing):
            self.__send_cmd("volume %f 1" % volume)
        self.__volume = volume



    def show_text(self, text, duration):

        self.__ensure_mplayer()
        self.__send_cmd("osd_show_text \"%s\" %d 0" % (text, duration))


    def screenshot(self):
    
        self.__ensure_mplayer()
        self.__send_cmd("screenshot 0")
        



_singleton = _MPlayer()
def MPlayer(): return _singleton

