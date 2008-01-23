#! /usr/bin/env python

try:
    from utils.Observable import Observable
except:
    class Observable(object):
        def update_observer(*args): pass
        def add_observer(*args): pass
        def remove_observer(*args): pass

try:
    import gobject
    HAVE_GOBJECT = True
except:
    HAVE_GOBJECT = False
    

import os
import fcntl
import subprocess
import time

import gobject


class MPlayerError(StandardError): pass
class MPlayerNotFoundError(MPlayerError): pass
class MPlayerDiedError(MPlayerError): pass
class FileNotFoundError(MPlayerError): pass
class InvalidFileError(MPlayerError): pass


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
_LENGTH = 32

_MAX_VALUES = 33


# connection timeout in seconds
_CONNECTION_TIMEOUT = 30
_LOGGING = False

# path to the mplayer executable
_MPLAYER = "/usr/bin/mplayer"


class _MPlayer(Observable):
    """
    Singleton class for controlling and embedding mplayer in other applications.
    """
    
    OBS_STARTED = 0
    OBS_KILLED = 1
    OBS_ERROR = 2
        
    OBS_PLAYING = 3
    OBS_STOPPED = 4
    OBS_NEW_STREAM_TRACK = 5
    OBS_EOF = 6
    
    OBS_POSITION = 7
    
    OBS_ASPECT = 8
    
    OBS_BUFFERING = 9
    
    # error codes
    ERR_INVALID = 0
    ERR_NOT_FOUND = 1
    ERR_CONNECTION_TIMEOUT = 2
    
            

    def __init__(self):
        """
        Creates the MPlayer singleton.
        """

        self.__heartbeat_running = False
    
        self.__xid = -1
        self.__opts = ""
        
        self.__stdin = None
        self.__stdout = None
        self.__has_video = False
        self.__has_audio = False
        self.__playing = False
        self.__broken = False
        
        self.__volume = 50
        
        self.__needs_restart = False
        self.__media_length = -1
        self.__idle_counter = 0
        
        self.__video_width = 0
        self.__video_height = 0
        self.__video_aspect = 0
        
        self.__uri = ""
        self.__position = 0
        self.__total_length = 0
        self.__time_of_check = 0
        
        self.__timeout_point = 0
        self.__next_time_check = 0
                
        self.__context_id = 0
        
        # table for collecting player values
        self.__player_values = [None] * _MAX_VALUES
        

    def __on_eof(self):
        """
        Reacts on end-of-file.
        """

        self.stop()
        self.__playing = False
        self.__has_video = False
        self.__has_audio = False
        print "REACHED EOF"
        self.update_observer(self.OBS_EOF, self.__context_id)


    def __run_heartbeat(self):
        """
        Runs the heartbeat function if GObject is available and it's not
        already running.
        """
    
        if (HAVE_GOBJECT and not self.__heartbeat_running):
            self.__hearbeat_running = True
            self.__player_values[_FILENAME] = "..."
            self.__heartbeat()
        
                        
            
    def __heartbeat(self):
        """
        Regularly checks the player status and sends events to its listeners.
        """

        self.__collect_values()

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

            # check for new track in stream
            if (self.__player_values[_ICY_INFO]):
                title = self.__player_values[_ICY_INFO]
                self.update_observer(self.OBS_NEW_STREAM_TRACK,
                                     self.__context_id, title)
                self.__player_values[_ICY_INFO] = None
            
            # check for end of file
            if (self.__player_values[_FILENAME]):
                self.__next_time_check = now + 1
            elif (now > self.__next_time_check):            
                self.__on_eof()
                self.__next_time_check = now + 1

            self.__player_values[_FILENAME] = None
            self.__send_cmd("get_property filename")

            self.update_observer(self.OBS_POSITION, self.__context_id,
                                 pos, total)
    
        else:
            self.__idle_counter += 1
            
            # check for connection timeout
            if (self.__timeout_point and not self.__broken and
                time.time() > self.__timeout_point):
                self.__timeout_point = 0
                self.__broken = True
                self.update_observer(self.OBS_ERROR, self.__context_id,
                                     self.ERR_CONNECTION_TIMEOUT)

        #end if
        
        # close mplayer if we've been idle too long
        if (self.__idle_counter == 500):
            self.__idle_counter = 0
            self.__stdin.close()
            self.__stdout.close()
            self.__stop_mplayer()
            self.__heartbeat_running = False
            self.__needs_restart = True
            print "mplayer closed due to idle timeout"            
            return False
           
        gobject.timeout_add(300, self.__heartbeat)        


    def __wait_for(self, key):
        """
        Waits (with a timeout) until the given key has a value.
        """
    
        cnt  = 0
        while (not self.__player_values[key] and cnt < 500):
            self.__collect_values()
            time.sleep(0.001)
            cnt += 1
        print cnt
        

    def wait_for_video_aspect(self):
    
        self.__wait_for(_VIDEO_ASPECT)


    def __send_cmd(self, data):
    
        if (_LOGGING): print "--> " + data
        try:
            self.__stdin.write(data + "\n")
        except IOError:
            # broken pipe
            self.__stop_mplayer()
        
        
    def __read(self):
                
        data = self.__stdout.readline()
        if (_LOGGING): print "    " + data[:-1]
        return data        



    def __collect_values(self):        
        
        if (not self.__stdout): return
        
        # get all new data
        for i in range(10):  # not more than ten in a row
            try:
                data = self.__read()
            except IOError, err:
                # no data left
                break
                
            self.__parse_value(data)
        #end for
        
        
    def __read_ans(self, data):

        idx = data.find("=")
        value = data[idx + 1:].strip()
        return value
        
        
    def __read_info(self, data):
    
        idx = data.find(":")
        value = data[idx + 1:].strip()
        return value
        
        
    def __parse_value(self, data):
    
        if (data.startswith("ANS_TIME_POSITION")):
            self.__player_values[_POSITION] = self.__read_ans(data)
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

        elif (data.startswith("Demuxer info Artist changed to ")):
            idx = data.find("changed to ")
            artist = data[idx + 11:].strip()
            self.__player_values[_ARTIST] = artist
            self.__player_values[_ICY_INFO] = self.__player_values[_NAME] + \
                                              " - " + artist
        
        elif (data.startswith("Starting playback...")):
            self.__playing = True
            self.__timeout_point = 0
            self.__media_length = -1
            self.set_volume(self.__volume)
            self.update_observer(self.OBS_PLAYING, self.__context_id)
            
        elif (data.startswith("File not found: ")):
            self.__broken = True
            self.update_observer(self.OBS_ERROR, self.__context_id,
                                 self.ERR_NOT_FOUND)
        elif (data.startswith("[file] No filename")):
            self.__broken = True
            self.update_observer(self.OBS_ERROR, self.__context_id,
                                 self.ERR_NOT_FOUND)
        elif (data.startswith("Cache size set to ")):
            self.update_observer(self.OBS_BUFFERING, self.__context_id)
        elif (data.endswith("No stream found.\n")):
            self.__broken = True
            self.update_observer(self.OBS_ERROR, self.__context_id,
                                 self.ERR_NOT_FOUND)
        elif (" failed to load: " in data):
            self.__broken = True
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
            self.__collect_values()
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


    def set_options(self, opts):
        """
        Sets command line options to use for mplayer.
        """
    
        if (self.__opts != opts):
            self.__opts = opts
            self.__needs_restart = True
        
        
        
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
                

            
            
    def __start_mplayer(self, xid, opts):
        """
        Starts a new mplayer process and connects to it.
        """
    
        print "Starting MPlayer"
        self.__playing = False
        
        cmd = "LANG=C %s -quiet -slave -idle -osdlevel 0 " \
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
                
        self.__run_heartbeat()
        self.update_observer(self.OBS_STARTED)
        
        
        
    def __ensure_mplayer(self):
        """
        Makes sure that mplayer is running.
        """

        if (self.__needs_restart):        
            self.__stop_mplayer()
            self.__needs_restart = False
            if (self.__uri):
                self.load(self.__uri, self.__context_id)
                self.__playing = False
        
        if (not self.__stdin):
            self.__start_mplayer(self.__xid, self.__opts)        

        

    
    
    
    def close(self):
        """
        Closes MPlayer. Your program should invoke this method on exit.
        """
    
        self.__stop_mplayer()


    def load(self, filename, ctx_id = -1):
        """
        Loads and plays the given media file.
        """
    
        self.__uri = ""
        self.__ensure_mplayer()
        
        self.__send_cmd("loadfile \"%s\"" % filename)

        self.__playing = False
        self.__broken = False
        self.__has_video = False
        self.__has_audio = False
        self.__position = 0
        self.__uri = filename

        self.__player_values[_FILENAME] = filename

        #cnt = 0
        #while (not self.__playing and not self.__broken):
        #    self.__collect_values()
        #    time.sleep(0.01)
        #    #print "CNT", cnt
        #    if (cnt == 5000):
        #        self.__broken = True
        #        break
        #        
        #    cnt += 1
        #end while
        
        self.__timeout_point = time.time() + _CONNECTION_TIMEOUT

        if (ctx_id != -1):
            self.__context_id = ctx_id
        else:
            self.__context_id +=1
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
            self.__position = 0
            self.__position = 0
            self.set_volume(self.__volume)
            self.__send_cmd("play")            
            self.update_observer(self.OBS_PLAYING, self.__context_id)
        
        
    def pause(self):

        self.__ensure_mplayer()
            
        self.__playing = not self.__playing        
        if (self.__playing):
            self.set_volume(self.__volume)
            self.__send_cmd("pause")
            self.__position = 0
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
        self.__position = 0
                

        
        
    def seek_percent(self, pos):

        self.__ensure_mplayer()    
        self.__send_cmd("seek %d 1" % pos)
        self.play()
        self.__position = 0



    def get_position(self):

        self.__ensure_mplayer()
            
        self.__send_cmd("get_time_pos")
        try:
            pos = float(self.__expect(_POSITION, True))
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

        return (pos, total)


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

