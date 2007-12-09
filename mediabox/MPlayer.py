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




class _MPlayer(Observable):
    """
    Singleton class for controlling and embedding mplayer in other applications.
    """
    
    OBS_STARTED = 0
    OBS_KILLED = 1
    
    OBS_PLAYING = 2
    OBS_STOPPED = 3
    OBS_EOF = 4
    
    OBS_POSITION = 5
    
    OBS_ASPECT = 6
    
    
            

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
        
        self.__next_time_check = 0
        
        self.__context_id = 0
        

    def __on_eof(self, is_eof):
        """
        Reacts on end-of-file.
        """

        if (is_eof):
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
            self.__heartbeat()
        
                        
            
    def __heartbeat(self):
        """
        Regularly checks the player status and sends events to its listeners.
        """
                                
        if (self.__playing):
            self.__idle_counter = 0
            
            now = time.time()

            # check if player is still playing a file
            self.__check_for_eof(self.__on_eof)
        
            # don't ask mplayer for the current position every time, because
            # this is highly inefficient with Ogg Vorbis files
            t = time.time()
            if (self.__position == 0): # or t > self.__next_time_check):
                try:            
                    pos, total = self.get_position()
                    self.__time_of_check = now
                except:
                    pos, total = 0, 0

                self.__position = pos
                self.__total_length = total
                self.__next_time_check = t + 10
                
            else:
                pos = self.__position + t - self.__time_of_check
                total = self.__total_length
                self.__time_of_check = t
                self.__position = pos
            #end if
             
            self.update_observer(self.OBS_POSITION, self.__context_id,
                                 pos, total)
    
        else:
            self.__idle_counter += 1
        #end if
        
        # close mplayer if we've been idle too long
        if (self.__idle_counter == 500):
            self.__idle_counter = 0
            self.__stop_mplayer()
            self.__heartbeat_running = False
            self.__needs_restart = True
            print "mplayer closed due to idle timeout"            
            return False
                
        gobject.timeout_add(500, self.__heartbeat)        

       
    def is_available(self):
        """
        Returns whether mplayer is available on the system.
        """
        
        return os.path.exists("/usr/bin/mplayer")
        
        
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
        
        cmd = "LANG=C /usr/bin/mplayer -quiet -slave -idle -osdlevel 0 " \
              "-identify -wid %d %s 3>/dev/null" % (xid, opts)
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
                self.load(self.__uri)
        
        if (not self.__stdin):
            self.__start_mplayer(self.__xid, self.__opts)        

        

    
    
    
    def close(self):
        """
        Closes MPlayer. Your program should invoke this method on exit.
        """
    
        self.__stop_mplayer()

    
    
    def load(self, filename):
        """
        Loads and plays the given media file.
        """

        print "LOAD", filename
        self.__uri = ""
        self.__ensure_mplayer()

        NONE = 0
        LOADING = 1
        LOADING_OK = 2
        PLAYING = 3 
        
        self.__stdin.write("loadfile \"%s\"\n" % filename)
        self.__playing = False
        
        self.__has_video = False
        self.__has_audio = False
        
        self.__position = 0

        state = NONE                    
        while (True):
            try:
                out = self.__stdout.readline()
            except IOError, err:
                errno = err.errno
                #print errno
                time.sleep(0.01)
                continue
                
            #print ">>> " + out
            if (not out):
                self.__start_mplayer()
                raise MPlayerDiedError()

            #if (out.strip()): print ">>> " + out.strip()
            if (state == NONE):
                if (out.startswith("Playing ")):
                    state = LOADING
                    
            elif (state == LOADING):
                if (out.startswith("Failed to open ")):
                    raise FileNotFoundError()
                elif (out.endswith(" failed\n")):
                    raise InvalidFileError()
                elif (out.endswith("No stream found.\n")):
                    raise InvalidFileError()
                elif (out.startswith("\n")):                
                    pass
                    #raise InvalidFileError()                    
                elif (out.startswith("AUDIO: ")):
                    self.__has_audio = True
                elif (out.startswith("VIDEO: ")):
                    self.__has_video = True
                    
                elif (out.startswith("ID_VIDEO_WIDTH=")):
                    value = float(out.split("=")[1])
                    self.__video_width = value
                elif (out.startswith("ID_VIDEO_HEIGHT=")):
                    value = float(out.split("=")[1])
                    self.__video_height = value
                    self.__video_aspect = self.__video_width / self.__video_height
                    self.update_observer(self.OBS_ASPECT, self.__video_aspect)
                elif (out.startswith("ID_VIDEO_ASPECT=")):
                    value = float(out.split("=")[1])
                    self.__video_aspect = value
                    
                elif (out.startswith("Starting playback...")):
                    self.__uri = filename
                    self.__playing = True
                    print self.__has_video, self.__has_audio
                    self.__media_length = -1
                    self.update_observer(self.OBS_PLAYING)
                    break
        #end while
                
        self.__context_id +=1
        print "CTX", self.__context_id
        return self.__context_id
        

    def __expect(self, key, cb = None):
        """
        Waits for the given key and returns its value. If a callback handler
        is given, this method returns immediately and calls the handler when
        the value is available.
        """

        if (HAVE_GOBJECT and cb):
            gobject.io_add_watch(self.__stdout, gobject.IO_IN, cb)
            return
            
        elif (cb):
            return
                
        #print "expect", key
        i = 0    
        while (i < 100):
            i += 1
            try:
                out = self.__stdout.readline()
            except IOError, err:
                time.sleep(0.01)
                continue
            #print ">>> " + out
                                      
            if (out.startswith(key)):
                try:
                    value = out.split("=")[1]
                except:
                    return ""
                else:
                    return value.strip()
        #end while

        return ""
    
    
    def __check_for_eof(self, cb):

        def f(fd, cond):
            try:
                out = fd.readline()
            except IOError:
                return False

            cb(out.strip() == "")
            return False

        # ask for the filename. if there's no answer (MPlayerError), we know
        # that mplayer isn't playing a file
        self.__stdin.write("get_property filename\n")
        self.__expect("ANS_filename", f)
    
    
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
        
        self.__stdin.write("speed_set %d\n" % n)
    
    
        
    def play(self):

        self.__ensure_mplayer()
            
        if (not self.__playing):
            self.__playing = True
            self.__position = 0
            self.__position = 0
            self.__stdin.write("play\n")
            self.update_observer(self.OBS_PLAYING)
        
        
    def pause(self):

        if (not self.__stdin): return
            
        self.__playing = not self.__playing        
        if (self.__playing):
            self.__stdin.write("pause\n")
            self.__position = 0
            self.update_observer(self.OBS_PLAYING)
        else:
            self.__stdin.write("pause\n")
            self.update_observer(self.OBS_STOPPED)
        
        
    def stop(self):

        self.__ensure_mplayer()
        
        if (self.__playing):
            self.__playing = False
            self.__stdin.write("pause\n")
            self.update_observer(self.OBS_STOPPED)


    def seek(self, pos):
    
        self.__ensure_mplayer()
        self.__stdin.write("seek %d 2\n" % pos)
        self.play()
        self.__position = 0
                

        
        
    def seek_percent(self, pos):

        self.__ensure_mplayer()    
        self.__stdin.write("seek %d 1\n" % pos)
        self.play()
        self.__position = 0



    def get_position(self):

        self.__ensure_mplayer()
            
        self.__stdin.write("get_time_pos\n")
        try:
            pos = float(self.__expect("ANS_TIME_POSITION"))
        except:
            pos = 0.0            
        
        if (self.__media_length < 0):
            self.__stdin.write("get_time_length\n")
            try:
                total = float(self.__expect("ANS_LENGTH"))
            except:
                total = 0.0
            self.__media_length = total
        else:
            total = self.__media_length

        return (pos, total)


    def get_resolution(self):

        self.__ensure_mplayer()
            
        self.__stdin.write("get_video_resolution\n")
        value = self.__expect("ANS_VIDEO_RESOLUTION")[1:-1]
        
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

        self.__ensure_mplayer()
        print "Volume", volume
        self.__stdin.write("volume %f 1\n" % volume)



    def show_text(self, text, duration):

        self.__ensure_mplayer()
            
        self.__stdin.write("osd_show_text \"%s\" %d 0\n" % (text, duration))


    def screenshot(self):
    
        self.__ensure_mplayer()
        self.__stdin.write("screenshot 0\n")
        



_singleton = _MPlayer()
def MPlayer(): return _singleton

