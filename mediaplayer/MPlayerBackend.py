from AbstractBackend import AbstractBackend
from utils import maemo
from utils import logging

import os
import fcntl
import subprocess
import gobject
import gtk
import time


_MPLAYER = "/usr/bin/mplayer"


class MPlayerBackend(AbstractBackend):
    """
    Backend implementation for controlling MPlayer.
    """

    def __init__(self):
    
        self.__current_pos = 0
        self.__window_id = 0
        self.__current_mode = AbstractBackend.MODE_AUDIO
        
        self.__stdin = None
        self.__stdout = None
        self.__collect_handler = None
    
        self.__media_length = 0
        self.__media_position = 0
        
        self.__video_width = 0
        self.__video_height = 0

        # counter for determining likeliness of EOF
        self.__maybe_eof = 0
    
        AbstractBackend.__init__(self)


    def _get_icon(self):
    
        from theme import theme
        return theme.mb_backend_mplayer


    def __start_mplayer(self):
    
        if (self._get_mode() == self.MODE_AUDIO):
            cmd = "LANG=C %s -quiet -slave " \
                  "-noconsolecontrols -nojoystick -nolirc -nomouseinput " \
                  "-idle -osdlevel 0 -idx " \
                  "-cache 256 -cache-min 50 " \
                  "-identify -novideo 2>&1 3>/dev/null" \
                  % _MPLAYER
        else:
            product = maemo.get_product_code()
            if (product == "?"):
                logging.debug("mplayer backend detected non-maemo device")
                vo_opts = "-vo xv"
            elif (product == "SU-18"):
                logging.debug("mplayer backend detected Nokia 770")
                vo_opts = "-vo nokia770"
                                          #"fb_overlay_only:" \
                                          #"x=174:y=60:w=600:h=360")
            else:
                logging.debug("mplayer backend detected Nokia maemo-device")
                vo_opts = "-vo xv:ck-method=auto "\
                          "-noslices -hardframedrop " \
                          "-lavdopts fast:lowres=1,400"
        
            cmd = "LANG=C %s -quiet -slave " \
                  "-noconsolecontrols -nojoystick -nolirc -nomouseinput " \
                  "-dr -nomenu -idle -osdlevel 0 -idx " \
                  "-cache 256 -cache-min 50 " \
                  "-identify -wid %d %s 2>&1 3>/dev/null" \
                  % (_MPLAYER, self.__window_id, vo_opts)
        
        
        
        p = subprocess.Popen([cmd],
                             shell=True, cwd="/tmp",
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             close_fds=True)

        time.sleep(0.25)
        if (p.poll()):
            print "Startup failed"
            self._report_error(self.ERR_INVALID, "Could not start mplayer")
            return
        else:
            print "running"
   
        self.__stdin = p.stdin
        self.__stdout = p.stdout
        
        # set non-blocking for better performance in an unthreaded environment
        fcntl.fcntl(self.__stdout, fcntl.F_SETFL, os.O_NONBLOCK)

        self.__collect_handler = gobject.io_add_watch(self.__stdout,
                                                      gobject.IO_HUP |
                                                      gobject.IO_IN,
                                                      self.__on_collect_values,
                                                      [""])



    def __stop_mplayer(self):
        """
        Stops the currently running mplayer.
        """
        
        os.system("killall mplayer 2>/dev/null >/dev/null")
        time.sleep(0.25)
        os.system("killall -9 mplayer 2>/dev/null >/dev/null")
        self.__stdin = None
        self.__stdout = None
        
        if (self.__collect_handler):
            gobject.source_remove(self.__collect_handler)
            self.__collect_handler = None



    def _ensure_backend(self):
    
        if (self._get_mode() != self.__current_mode):
            self.__stop_mplayer()
            self.__current_mode = self._get_mode()
        
        if (not self.__stdout):
            self.__start_mplayer()



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
            buf[0] = buf[0].replace("\r", "\n")
            idx = buf[0].find("\n")

            while (idx >= 0):
                line = buf[0][:idx]
                buf[0] = buf[0][idx + 1:]
                try:
                    self.__parse_value(line)
                except:
                    logging.error("error parsing mplayer output: %s\n%s",
                                  line, logging.stacktrace())

                idx = buf[0].find("\n")
            #end while
            
            return True
        #end if

       
        
    def _set_window(self, xid):
    
        if (xid != self.__window_id):
            self.__window_id = xid
        
        
    def _is_eof(self):
    
        if (self.__maybe_eof == 0):
            return False
    
        elif (self.__maybe_eof == 1):
            # provoke an answer from mplayer; if it fails, we have reached EOF
            #self.__send_cmd("get_time_pos")
            #self.__maybe_eof = 2
            return True
            
        #elif (self.__maybe_eof == 2):
        #    return True
        
        
    def _load(self, uri):
    
        self.__media_length = 0
        self.__media_position = 0
        self.__video_width = 0
        self.__video_height = 0
        self.__maybe_eof = 0
        self.__filename = uri
        
        uri = uri.replace("\"", "\\\"")
        self.__send_cmd("loadfile \"%s\"" % uri)
        self.__send_cmd("get_time_length")
        self.__send_cmd("get_time_pos")
        
        
    def _play(self):
    
        self.__send_cmd("play")

        
    def _stop(self):
    
        self.__send_cmd("pause")
        
        
    def _close(self):
    
        self.__stop_mplayer()
        
        
    def _seek(self, pos):
    
        self.__send_cmd("seek %d 2" % pos)
        
        
    def _set_volume(self, vol):
    
        self.__send_cmd("volume %f 1" % vol)

        
    def _get_position(self):
    
        if (self.__maybe_eof > 0):
            return (0, 0)
    
        if (self.__media_length == 0):
            self.__send_cmd("get_time_length")
            self.__media_length = -1
            timeout = time.time() + 1.0
            while (self.__media_length == -1 and time.time() < timeout):
                gtk.main_iteration(False)
            if (time.time() >= timeout):
                logging.warning("timeout reached for mplayer.get_time_length")
        #end if

        self.__media_position = -1
        self.__send_cmd("get_time_pos")
        timeout = time.time() + 1.0
        while (self.__media_position == -1 and time.time() < timeout):
            gtk.main_iteration(False)
        if (time.time() >= timeout):
            logging.warning("timeout reached for mplayer.get_time_pos")

        return (self.__media_position, self.__media_length)



    
    def __try_report_aspect_ratio(self):
    
        if (self.__video_width > 0 and self.__video_height > 0):
            ratio = self.__video_width / float(self.__video_height)
            self._report_aspect_ratio(ratio)
            self.__send_cmd("switch_ratio %f" % ratio)
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

        if (not data):
            # an empty line may indicate EOF, but not every empty line is an EOF
            self.__maybe_eof = 1
        else:
            self.__maybe_eof = 0
            
        if (data.startswith("ANS_TIME_POSITION")):
            self.__media_position = float(self.__read_ans(data))

        elif (data.startswith("ANS_PERCENT_POSITION")):
            print "PERCENT POSITION", self.__read_ans(data)
            self.__media_position = float(self.__read_ans(data))  / 100.0 * \
                                    self.__media_length

        elif (data.startswith("ANS_LENGTH")):
            self.__media_length = float(self.__read_ans(data))

        elif (data.startswith("ANS_VIDEO_RESOLUTION")):
            res = self.__read_ans(data)
            
        elif (data.startswith("ANS_filename")):
            filename = self.__read_ans(data)
            
        elif (data.startswith("ANS_volume")):
            print "VOLUME", self.__read_ans(data)

        elif (data.startswith("AUDIO: ")):
            #print "HAS AUDIO"
            pass
            
        elif (data.startswith("VIDEO: ")):
            #print "HAS VIDEO"
            pass

        elif (data.startswith("ID_VIDEO_WIDTH")):
            self.__video_width = float(self.__read_ans(data))
            #print "VIDEO WIDTH", self.__video_width
            self.__try_report_aspect_ratio()
            
        elif (data.startswith("ID_VIDEO_HEIGHT")):
            self.__video_height = float(self.__read_ans(data))
            #print "VIDEO HEIGHT", self.__video_height
            self.__try_report_aspect_ratio()

        elif (data.startswith("ID_LENGTH")):
            # ID_LENGTH has precedence over reported length, if available,
            # because mplayer is buggy reporting length of FLAC files
            self.__media_length = float(self.__read_ans(data))
            #print "MEDIA LENGTH", self.__media_length

        elif (data.startswith("Name   : ")):
            print "NAME", self.__read_info(data)
            
        elif (data.startswith("Genre  : ")):
            print "GENRE", self.__read_info(data)
            
        elif (data.startswith("Website: ")):
            print "WEBSITE", self.__read_info(data)
       
        elif (data.startswith("ICY Info: ")):
            title = self.__parse_icy_info(self.__read_info(data))
            print "ICY INFO", title
            self._report_tag("TITLE", title)
            
        elif (data.startswith("Demuxer info Name changed to ")):
            idx = data.find("changed to ")
            name = data[idx + 11:].strip()
            print "NAME CHANGED", name
            #self._report_tag("TITLE", name)

        elif (data.startswith("Demuxer info Artist changed to ")):
            idx = data.find("changed to ")
            artist = data[idx + 11:].strip()
            print "ARTIST CHANGED", artist
            #self._report_tag("ARTIST", artist)
        
        elif (data.startswith("Starting playback...")):
            #print "STARTING PLAYBACK"
            pass
            
        elif (data.startswith("GNOME screensaver enabled")):
            #print "DETECTED EOF"
            self.__maybe_eof = 1
            
        elif (data.startswith("File not found: ")):
            #print "FILE NOT FOUND"
            self._report_error(self.ERR_NOT_FOUND, "")

        elif (data.startswith("[file] No filename")):
            #print "NO FILENAME"
            self._report_error(self.ERR_NOT_FOUND, "")

        elif (data.startswith("Connecting to server")):
            self._report_connecting()

        elif (data.startswith("Cache size set to ")):
            #print "CACHE SIZE SET TO"
            self._report_buffering(0)

        elif (data.startswith("Cache fill:")):
            idx1 = data.find(":")
            idx2 = data.find("%")
            value = int(float(data[idx1 + 1:idx2].strip()))
            self._report_buffering(value)

        elif (data.endswith("No stream found.\n")):
            #print "NO STREAM FOUND"
            self._report_error(self.ERR_NOT_FOUND, "")

        elif (data.startswith("Error opening/initializing ")):
            #print "ERROR OPENING"
            self._report_error(self.ERR_INVALID, "")

        elif (data.startswith("Server returned 400:Server Full")):
            #print "ERROR 400:Server Full"
            self._report_error(self.ERR_SERVER_FULL, "")

        elif (data.startswith("Server returned 404")):
            self._report_error(self.ERR_NOT_FOUND, "")

        elif (data.startswith("Server returned 503")):
            self._report_error(self.ERR_NOT_FOUND, "")


    def __parse_icy_info(self, data):
        
        key = "StreamTitle='"
        idx = data.find(key)
        if (idx != -1):
            idx2 = data.find("';", idx + len(key))
            return data[idx + len(key):idx2]
        return ""

