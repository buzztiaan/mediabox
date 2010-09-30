from StreamAnalyzer import StreamAnalyzer
from utils.EventEmitter import EventEmitter
from utils.StateMachine import StateMachine, State
from utils import logging

import gobject
import time
import urllib




# idle timeout in milliseconds
_IDLE_TIMEOUT = 1000 * 5 #1000 * 60 * 3

_INPUT_LOAD = 0
_INPUT_PLAY = 1
_INPUT_SEEK = 2
_INPUT_PAUSE = 3
_INPUT_STOP = 4
_INPUT_EOF = 5
_INPUT_IDLE = 6
_INPUT_RESUME = 7




class AbstractBackend(EventEmitter):
    """
    Abstract base class for media player backend implementations.
    Backends deriving from this class only have to implement a minimal set of
    simple methods, while all the logic is contained in this base class.
    This way, backend implementation becomes easy and straight-forward.
    """

    # player states
    STATUS_CONNECTING = 0
    STATUS_BUFFERING = 1
    STATUS_PLAYING = 2
    STATUS_STOPPED = 3
    STATUS_EOF = 4

    # error codes
    NO_ERROR = 0
    ERR_INVALID = 1
    ERR_NOT_FOUND = 2
    ERR_CONNECTION_TIMEOUT = 3
    ERR_NOT_SUPPORTED = 4
    ERR_SERVER_FULL = 5
    
    EVENT_STARTED = "event-started"
    EVENT_KILLED = "event-killed"
    EVENT_SUSPENDED = "event-suspended"
    EVENT_ERROR = "event-error"
    
    EVENT_STATUS_CHANGED = "event-status-changed"
    EVENT_VOLUME_CHANGED = "event-volume-changed"
    
    EVENT_POSITION_CHANGED = "event-position-changed"
    EVENT_ASPECT_CHANGED = "event-aspect-changed"
    EVENT_TAG_DISCOVERED = "event-tag-discovered"
   
   
    # remote control keys that can be sent to backends (for DVD navigation etc.)
    KEY_UP = 0
    KEY_DOWN = 1
    KEY_LEFT = 2
    KEY_RIGHT = 3
    KEY_SELECT = 10
    KEY_MENU1 = 11
    KEY_MENU2 = 12
    KEY_MENU3 = 13

    # playback modes so that the backends can behave accordingly
    MODE_AUDIO = 0
    MODE_VIDEO = 1

    __context_id_cnt = [0]
    
    
    def __init__(self):
        """
        Constructor to be invoked by subclasses. Do not instantiate this class
        directly.
        """
        
        # mode: MODE_AUDIO or MODE_VIDEO
        self.__mode = self.MODE_AUDIO
        
        # handler for watching the current position
        self.__position_handler = None
        
        # handler for detecting idle timeout
        self.__idle_handler = None
        
        # analyzer for streams to check them before loading
        self.__stream_analyzer = StreamAnalyzer()
        
        
        # build state machine
        self.__STATE_UNLOADED = State("unloaded",
                                      self.__on_enter_unloaded,
                                      self.__on_leave_unloaded)
        self.__STATE_LOADED =   State("loaded",
                                      self.__on_enter_loaded)
        self.__STATE_PLAYING =  State("playing",
                                      self.__on_enter_playing,
                                      self.__on_leave_playing)
        self.__STATE_PAUSED =   State("paused",
                                      self.__on_enter_paused,
                                      self.__on_leave_paused)
        self.__STATE_EOF =      State("eof",
                                      self.__on_enter_eof,
                                      self.__on_leave_eof)
        self.__STATE_IDLE =     State("idle",
                                      self.__on_enter_idle)
        self.__STATE_ERROR =    State("error",
                                      self.__on_enter_error)

        no_error = lambda sm: sm.get_property("error") == self.NO_ERROR
        with_error = lambda sm: sm.get_property("error") != self.NO_ERROR

        self.__state_machine = StateMachine(self.__STATE_UNLOADED, [
        
            (self.__STATE_UNLOADED,        _INPUT_LOAD,
             no_error,                     self.__STATE_LOADED),

            (self.__STATE_UNLOADED,        _INPUT_PLAY,
             no_error,                     self.__STATE_LOADED),

            (self.__STATE_UNLOADED,        _INPUT_SEEK,
             no_error,                     self.__STATE_LOADED),

            (self.__STATE_UNLOADED,        _INPUT_PAUSE,
             no_error,                     self.__STATE_LOADED),

            (self.__STATE_UNLOADED,        None,
             with_error,                   self.__STATE_ERROR),
             
            (self.__STATE_LOADED,          None,
             no_error,                     self.__STATE_PLAYING),
            
            (self.__STATE_LOADED,          None,
             with_error,                   self.__STATE_ERROR),
            
            (self.__STATE_PLAYING,         _INPUT_PAUSE,
             no_error,                     self.__STATE_PAUSED),

            (self.__STATE_PLAYING,         _INPUT_STOP,
             no_error,                     self.__STATE_PAUSED),

            (self.__STATE_PLAYING,         _INPUT_SEEK,
             no_error,                     self.__STATE_PLAYING),

            (self.__STATE_PLAYING,         _INPUT_LOAD,
             no_error,                     self.__STATE_LOADED),
             
            (self.__STATE_PLAYING,         _INPUT_EOF,
             no_error,                     self.__STATE_EOF),

            (self.__STATE_PLAYING,         None,
             with_error,                   self.__STATE_ERROR),
             
            (self.__STATE_PAUSED,          _INPUT_PAUSE,
             no_error,                     self.__STATE_PLAYING),

            (self.__STATE_PAUSED,          _INPUT_PLAY,
             no_error,                     self.__STATE_PLAYING),

            (self.__STATE_PAUSED,          _INPUT_SEEK,
             no_error,                     self.__STATE_PLAYING),

            (self.__STATE_PAUSED,          _INPUT_LOAD,
             no_error,                     self.__STATE_LOADED),
             
            (self.__STATE_PAUSED,          _INPUT_IDLE,
             no_error,                     self.__STATE_IDLE),
             
            (self.__STATE_IDLE,            None,
             no_error,                     self.__STATE_UNLOADED),

            #(self.__STATE_EOF,             _INPUT_LOAD,
            # no_error,                     self.__STATE_LOADED),

            (self.__STATE_EOF,             None,
             no_error,                     self.__STATE_UNLOADED),

            (self.__STATE_ERROR,           None,
             no_error,                     self.__STATE_UNLOADED),
            
        ])
        
        # current position in seconds (-1 means unknown)
        self.__state_machine.set_property("position", 0)

        # current length in seconds (-1 means unknown)
        self.__state_machine.set_property("length", -1)
        
        # tags collected by the backend
        self.__state_machine.set_property("tags", {})
        
        # the URI of the current file
        self.__state_machine.set_property("uri", "")
        
        # the current context ID
        self.__state_machine.set_property("context id", 0)

        # point to resume from: (uri, seconds)
        self.__state_machine.set_property("suspension point", None)
        
        # error code
        self.__state_machine.set_property("error", self.NO_ERROR)
        
        EventEmitter.__init__(self)
        
        
    def __guard_error(self, sm):
    
        return sm.get_property("error", False)
        
        
    def __on_enter_unloaded(self, sm):
    
        # make sure the backend is unloaded
        self._close()
        
        
    def __on_leave_unloaded(self, sm):
    
        # load backend
        self._ensure_backend()
        
        
    def __on_enter_loaded(self, sm):
    
        # clear tags
        sm.get_property("tags").clear()
                
        # resume from suspension point
        susp = sm.get_property("suspension point")
        if (susp):
            uri, pos = susp
        else:
            uri = sm.get_property("uri")

        # load file
        self._load(uri)
        
        
    def __on_enter_playing(self, sm):
    
        # resume from suspension point and invalidate it
        susp = sm.get_property("suspension point")
        if (susp):
            uri, pos = susp
            sm.set_property("suspension point", None)
            print "seek from", pos
            self._seek(pos)
        else:
            self._play()
    
        sm.set_property("position", -1)
    
        # start playloop
        if (not self.__position_handler):
            self.__position_handler = \
                  gobject.timeout_add(0, self.__update_position, 0, time.time())

        # notify
        gobject.timeout_add(0, self.emit_event, self.EVENT_STATUS_CHANGED,
                        sm.get_property("context id"), self.STATUS_PLAYING)


        
    def __on_leave_playing(self, sm):
    
        # stop playloop
        if (self.__position_handler):
            gobject.source_remove(self.__position_handler)
        self.__position_handler = None


    def __on_enter_eof(self, sm):

        # start idle timeout
        if (self.__idle_handler):
            gobject.source_remove(self.__idle_handler)
        self.__idle_handler = gobject.timeout_add(_IDLE_TIMEOUT,
                                                  self.__on_idle_timeout)
    
        # notify
        logging.info("reached end-of-file")
        self.emit_event(self.EVENT_STATUS_CHANGED,
                        sm.get_property("context id"), self.STATUS_EOF)


    def __on_leave_eof(self, sm):
    
        # stop idle timeout
        if (self.__idle_handler):
            gobject.source_remove(self.__idle_handler)


    def __on_enter_paused(self, sm):
    
        self._stop()
    
        # start idle timeout
        if (self.__idle_handler):
            gobject.source_remove(self.__idle_handler)
        self.__idle_handler = gobject.timeout_add(_IDLE_TIMEOUT,
                                                  self.__on_idle_timeout)
        
        # notify
        self.emit_event(self.EVENT_STATUS_CHANGED,
                        sm.get_property("context id"), self.STATUS_STOPPED)


    def __on_leave_paused(self, sm):
    
        # stop idle timeout
        if (self.__idle_handler):
            gobject.source_remove(self.__idle_handler)
        
        
    def __on_enter_idle(self, sm):
    
        # set suspension point
        pos = sm.get_property("position")
        total = sm.get_property("length")
        uri = self.__state_machine.get_property("uri")
        sm.set_property("suspension point", (uri, pos))
        
   
    def __on_enter_error(self, sm):
    
        ctx_id = sm.get_property("context id")
        err = sm.get_property("error")
        sm.set_property("error", self.NO_ERROR)
        self.emit_event(self.EVENT_ERROR, ctx_id, err)
        
        
    def connect_started(self, cb, *args):
    
        self._connect(self.EVENT_STARTED, cb, *args)
        
        
    def connect_killed(self, cb, *args):
    
        self._connect(self.EVENT_KILLED, cb, *args)


    def connect_suspended(self, cb, *args):
    
        self._connect(self.EVENT_SUSPENDED, cb, *args)


    def connect_error(self, cb, *args):
    
        self._connect(self.EVENT_ERROR, cb, *args)
        
        
    def connect_status_changed(self, cb, *args):
    
        self._connect(self.EVENT_STATUS_CHANGED, cb, *args)


    def connect_volume_changed(self, cb, *args):
    
        self._connect(self.EVENT_VOLUME_CHANGED, cb, *args)


    def connect_position_changed(self, cb, *args):
    
        self._connect(self.EVENT_POSITION_CHANGED, cb, *args)
        
        
    def connect_aspect_changed(self, cb, *args):
    
        self._connect(self.EVENT_ASPECT_CHANGED, cb, *args)


    def connect_tag_discovered(self, cb, *args):
    
        self._connect(self.EVENT_TAG_DISCOVERED, cb, *args)


    def __repr__(self):
        """
        Returns a readable string representation of this player object.
        """
    
        return self.__class__.__name__


    def _new_context_id(self):
        """
        Generates and returns a new context ID.
        
        @return: a new context ID
        """
    
        self.__context_id_cnt[0] += 1
        ctx_id = self.__context_id_cnt[0]
        return ctx_id


    def get_icon(self):
        """
        Returns the icon representing the backend, or None
        
        @return: icon pixbuf or None
        """
    
        return self._get_icon()


    def _get_mode(self):
        """
        Returns the current mode. Either MODE_AUDIO or MODE_VIDEO.
        
        @return: mode
        """
    
        return self.__mode
       
        
    def handle_expose(self, src, gc, x, y, w, h):
        """
        Override this method if the player has to handle GTK expose events
        on the player window.
        """
    
        pass


    def __on_idle_timeout(self):
        """
        Reacts on idle timeout and suspends the player.
        """

        logging.info("media backend idle timeout")
        self.__state_machine.send_input(_INPUT_IDLE)
            

    def __update_position(self, beginpos, timestamp):
        """
        Regularly updates the position in the file.
        """

        ctx_id = self.__state_machine.get_property("context id")

        pos = self.__state_machine.get_property("position")
        total = self.__state_machine.get_property("length")
 
        if (pos < 3):
            pos, total = self._get_position()
            timestamp = time.time()
            beginpos = pos
        else:
            # we don't ask the backend for position every time because
            # this could be inefficient with some backends
            pos = beginpos + (time.time() - timestamp)

        self.__state_machine.set_property("position", pos)
        self.__state_machine.set_property("length", total)
        if (pos != -1):
            self.emit_event(self.EVENT_POSITION_CHANGED,
                            ctx_id, pos, total)

        if (total > 0 and total - pos < 1):
            delay = max(0, int((total - pos) * 1000))
        else:
            delay = 500
        self.__position_handler = \
              gobject.timeout_add(delay, self.__update_position,
                                  beginpos, timestamp)

        # detect EOF
        if (pos >= 0 and self._is_eof()):
            self.__state_machine.send_input(_INPUT_EOF)


    def __parse_playlist(self, url):
        """
        Parses the playlist at the given URL and returns a list of URLs.
        """
    
        uris = []
        try:
            fd = urllib.urlopen(url)
        except:
            return uris
            
        data = fd.read()
        fd.close()

        filelines = [ l for l in data.splitlines()
                      if l.startswith("File") ]
        httplines = [ l for l in data.splitlines()
                      if l.startswith("http") ]
        for line in filelines:
            idx = line.find("=")
            uri = line[idx + 1:].strip()
            uris.append(uri)
        #end for

        for line in httplines:
            uri = line.strip()
            uris.append(uri)
        #end for

        return uris
        
        
    def set_window(self, xid):
        """
        Sets the window for video output.
        
        @param xid: Xid of the window
        """
    
        self._set_window(xid)
        
        
    def send_key(self, key):
    
        return self._send_key(key)


    def load_audio(self, uri):
    
        self.__mode = self.MODE_AUDIO
        return self.__load(uri)
        
        
    def load_video(self, uri):
    
        self.__mode = self.MODE_VIDEO
        return self.__load(uri)

        
    def __load(self, uri):  #, ctx_id = -1):
        """
        Loads and plays the given file.
        
        @param uri: URI of the file
        @param ctx_id: context ID to use; for internal use only
        @return: context ID
        """

        if (uri.startswith("http") and not uri.startswith("http://127.0.0.1")):
            s_type = self.__stream_analyzer.analyze(uri)
        else:
            s_type = StreamAnalyzer.STREAM

        if (s_type == StreamAnalyzer.PLAYLIST):
            uris = self.__parse_playlist(uri)
            if (uris):
                uri = uris[0]
            else:
                uri = ""

        print "LOAD", uri
        # new context id is needed
        self.__state_machine.set_property("context id", self._new_context_id())

        self.__state_machine.set_property("suspension point", None)
        self.__state_machine.set_property("uri", uri)
        self.__state_machine.send_input(_INPUT_LOAD)

        return self.__state_machine.get_property("context id")


    def _report_volume(self, vol):
        """
        The subclass calls this to report the sound volume.
        
        @param vol: volume level between 0 and 100
        """
        
        self.emit_event(self.EVENT_VOLUME_CHANGED, vol)
    


    def _report_aspect_ratio(self, ratio):
        """
        The subclass calls this to report the video aspect ratio.
        
        @param ratio: the aspect ratio
        """
        
        ctx_id = self.__state_machine.get_property("context id")
        self.emit_event(self.EVENT_ASPECT_CHANGED, ctx_id, ratio)


    def _report_tag(self, tag, value):
        """
        The subclass calls this to report ID tags.
        """
        
        ctx_id = self.__state_machine.get_property("context id")
        tags = self.__state_machine.get_property("tags")
        tags[tag] = value
        self.emit_event(self.EVENT_TAG_DISCOVERED,
                        ctx_id, tags)
    
    def _report_connecting(self):
        """
        The subclass calls this to report connecting to a server.
        """
        
        ctx_id = self.__state_machine.get_property("context id")
        self.emit_event(self.EVENT_STATUS_CHANGED,
                        ctx_id, self.STATUS_CONNECTING)
        
    
    def _report_buffering(self, value):
        """
        The subclass calls this to report stream buffering.
        """
        
        ctx_id = self.__state_machine.get_property("context id")
        self.emit_event(self.EVENT_STATUS_CHANGED,
                        ctx_id, self.STATUS_BUFFERING)
        
        
    def _report_error(self, err, message):
        """
        The subclass calls this to report errors.
        
        @param err: error code
        """
        
        self.__state_machine.set_property("error", err)
        self.__state_machine.send_input(None)
      
      
    def get_position(self):
    
        pos = self.__state_machine.get_property("position")
        total = self.__state_machine.get_property("length")
        return (pos, total)
        
        
    def play(self):
        """
        Starts playback.
        """
        
        self.__state_machine.send_input(_INPUT_PLAY)
        
        
    def pause(self):
        """
        Pauses playback or starts it if it was paused.
        """

        self.__state_machine.send_input(_INPUT_PAUSE)
        
        
    def stop(self):
        """
        Stops playback.
        """

        self.__state_machine.send_input(_INPUT_STOP)
        
        
    def close(self):
        """
        Closes the player.
        """
    
        self.__state_machine.send_input(_INPUT_IDLE)
        
        
    def set_volume(self, volume):
        """
        Sets the audio volume.
        
        @param volume: volume as a value between 0 and 100
        """

        self._set_volume(volume)    
        
        
    def seek(self, pos):
        """
        Seeks to the given position.
        
        @param pos: position in seconds
        """
    
        self._seek(pos)
        self.__state_machine.set_property("position", -1)
        self.__state_machine.send_input(_INPUT_SEEK)
        
        ctx_id = self.__state_machine.get_property("context id")
        total = self.__state_machine.get_property("length")
        self.emit_event(self.EVENT_POSITION_CHANGED,
                        ctx_id, pos, total)
        
        
    def seek_percent(self, percent):
        """
        Seeks to the given position.
        
        @param percent: position in percents
        """
    
        total = self.__state_machine.get_property("length")
        pos = total * percent / 100.0
        self.seek(pos)



    def rewind(self):
        """
        Rewinds the media.
        @since: 0.96.5
        """
        
        return
        
        """
        pos, total = self.__position
        if (pos > 0):
            print pos,
            pos = max(0, pos - 30)
            print pos
            self.seek(pos)
            self.__position = self._get_position()
            print pos, self.__position
            ctx_id = self.__state_machine.get_property("context id")
            self.emit_event(self.EVENT_POSITION_CHANGED,
                            ctx_id, *self.__position)
        """ 
        
    def forward(self):
        """
        Fast forwards the media.
        @since: 0.96.5
        """
        
        return

        """
        print "FORWARD"
        pos, total = self.__position
        print pos, total
        if (pos > 0):
            print pos,
            pos = min(total - 1, pos + 30)
            print pos
            self.seek(pos)
            self.__position = self._get_position()
            print pos, self.__position
            ctx_id = self.__state_machine.get_property("context id")
            self.emit_event(self.EVENT_POSITION_CHANGED,
                            ctx_id, *self.__position)
        """

    def _get_icon(self):
        """
        May be implemented by the backend to provide an icon representing the
        backend.
        """
        
        return None


    def _ensure_backend(self):
        """
        To be implemented by the backend.
        """
    
        raise NotImplementedError

    
    def _close(self):
        """
        To be implemented by the backend.
        
        This operation MUST BE a no-op if the backend is not loaded.
        """
        
        raise NotImplementedError

    
    def _set_window(self, xid):
        """
        May be implemented by the backend.
        """
        
        pass
        
        
    def _send_key(self, key):
        """
        May be implemented by the backend.
        """
        
        return False


    def _load(self, uri):
        """
        To be implemented by the backend.
        """
        
        raise NotImplementedError


    def _is_eof(self):
        """
        To be implemented by the backend.
        """

        raise NotImplementedError

    
    def _play(self):
        """
        To be implemented by the backend.
        
        This operation MUST BE a no-op if already playing.
        """
        
        raise NotImplementedError
        
        
    def _stop(self):
        """
        To be implemented by the backend.
        
        This operation MUST BE a no-op if already paused.
        """

        raise NotImplementedError


    def _seek(self, pos):
        """
        To be implemented by the backend.
        
        This operation is expected to resume playing if paused.
        """
    
        raise NotImplementedError
        
        
    def _set_volume(self, vol):
        """
        To be implemented by the backend.
        """
    
        raise NotImplementedError
        
        
    def _get_position(self):
        """
        To be implemented by the backend.
        """
    
        raise NotImplementedError

