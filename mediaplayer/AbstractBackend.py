from utils.EventEmitter import EventEmitter
from utils import logging

import gobject
import time




# idle timeout in milliseconds
_IDLE_TIMEOUT = 1000 * 60 * 3


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
    ERR_INVALID = 0
    ERR_NOT_FOUND = 1
    ERR_CONNECTION_TIMEOUT = 2
    ERR_NOT_SUPPORTED = 3
    ERR_SERVER_FULL = 4

    EVENT_STARTED = "event-started"
    EVENT_KILLED = "event-killed"
    EVENT_SUSPENDED = "event-suspended"
    EVENT_ERROR = "event-error"
    
    EVENT_STATUS_CHANGED = "event-status-changed"
    
    EVENT_POSITION_CHANGED = "event-position-changed"
    EVENT_ASPECT_CHANGED = "event-aspect-changed"
    EVENT_TAG_DISCOVERED = "event-tag-discovered"

    """
    # observer events
    OBS_STARTED = 0
    OBS_KILLED = 1
    OBS_SUSPENDED = 2
    OBS_ERROR = 3
        
    OBS_PLAYING = 4
    OBS_STOPPED = 5
    OBS_EOF = 6
    
    OBS_POSITION = 7
    
    OBS_ASPECT = 8
    OBS_TAG_INFO = 9
    
    OBS_CONNECTING = 10
    OBS_BUFFERING = 11
    """
    
    # error codes
    ERR_INVALID = 0
    ERR_NOT_FOUND = 1
    ERR_CONNECTION_TIMEOUT = 2
    ERR_NOT_SUPPORTED = 3
    ERR_SERVER_FULL = 4
    
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

        # ID tags
        self.__tags = {}

        # URI of the current file
        self.__uri = ""
        
        # point to resume from
        self.__suspension_point = None

        # current position and total length
        self.__position = (0, 0)
        
        # whether we are at end-of-file
        self.__eof_reached = False

        # whether the player is currently playing
        self.__playing = False
        
        # current volume level (0..100)
        self.__volume = 50
        
        self.__context_id = 0
        
        
        self.__position_handler = None
        self.__idle_handler = None
        
        
        EventEmitter.__init__(self)
        
        
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


    def __on_eof(self):
        """
        Reacts on end-of-file.
        """

        self.__playing = False
        logging.info("reached end-of-file")
        self.__eof_reached = True
        #self.__suspension_point = (self.__uri, 0)
        self.emit_event(self.EVENT_STATUS_CHANGED,
                        self.__context_id, self.STATUS_EOF)


    def __on_idle_timeout(self):
        """
        Reacts on idle timeout and suspends the player.
        """

        logging.info("media backend idle timeout")
        gobject.source_remove(self.__idle_handler)
        self.__idle_handler = None
        
        self.__playing = False
        pos, total = self.__position
        self.__suspension_point = (self.__uri, pos)
        logging.debug("setting suspension point: (%s, %d)", self.__uri, pos)
        self._close()


    def __resume_if_necessary(self):
    
        if (self.__suspension_point):
            uri, pos = self.__suspension_point
            self.__suspension_point = None

            self._ensure_backend()

            self._load(uri)
            self._set_volume(self.__volume)
            self._seek(pos)
            self._stop()
            self.__position = (0, 0)
            self.__watch_progress()
            
        elif (self.__eof_reached):
            self.__eof_reached = False
            
            self._load(self.__uri)
            self._set_volume(self.__volume)
            self._stop()
            self.__position = (0, 0)
            self.__watch_progress()
        #end if


    def __watch_progress(self):
        """
        Starts watching the time position progress.
        """
    
        if (not self.__position_handler):
            self.__position_handler = \
                  gobject.timeout_add(0, self.__update_position, 0, time.time())
            

    def __update_position(self, beginpos, timestamp):
        """
        Regularly updates the position in the file.
        """

        if (self.__playing):
            pos, total = self.__position
            if (pos < 3):
                pos, total = self._get_position()
                timestamp = time.time()
                beginpos = pos
            else:
                # we don't ask the backend for position every time because
                # this could be inefficient with some backends
                pos = beginpos + (time.time() - timestamp)
                
            self.__position = (pos, total)
            if (pos != 0 or total > 0):
                if (pos >= 0):
                    self.emit_event(self.EVENT_POSITION_CHANGED,
                                    self.__context_id, pos, total)

            if (total > 0 and total - pos < 1):
                delay = 200
            else:
                delay = 500
            self.__position_handler = \
                  gobject.timeout_add(delay, self.__update_position,
                                      beginpos, timestamp)

            # detect EOF
            if (pos > 1 and self._is_eof()):
                self.__on_eof()
                

        else:
            # stop updating when not playing
            self.__position_handler = None

        # reset idle timeout
        if (self.__idle_handler):
            gobject.source_remove(self.__idle_handler)
        self.__idle_handler = gobject.timeout_add(_IDLE_TIMEOUT,
                                                  self.__on_idle_timeout)          

        
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

        
    def __load(self, uri, ctx_id = -1):
        """
        Loads and plays the given file.
        
        @param uri: URI of the file
        @param ctx_id: context ID to use; for internal use only
        @return: context ID
        """

        self._ensure_backend()
        
        self.__tags.clear()
        self.__uri = uri
        self.__playing = False
        self.__eof_reached = False
        self.__suspension_point = None
       
        self.stop()

        self._load(uri)
        self._set_volume(self.__volume)
        
        print "DELAY PLAY", uri
        gobject.timeout_add(0, self.play)

        if (ctx_id != -1):
            self.__context_id = ctx_id
        else:
            self.__context_id = self._new_context_id()
        logging.debug("new context ID is %s", self.__context_id)

        return self.__context_id



    def _report_aspect_ratio(self, ratio):
        """
        The subclass calls this to report the video aspect ratio.
        
        @param ratio: the aspect ratio
        """
        
        self.emit_event(self.EVENT_ASPECT_CHANGED, self.__context_id, ratio)


    def _report_tag(self, tag, value):
        """
        The subclass calls this to report ID tags.
        """
        
        self.__tags[tag] = value
        self.emit_event(self.EVENT_TAG_DISCOVERED,
                        self.__context_id, self.__tags)
    
    
    def _report_connecting(self):
        """
        The subclass calls this to report connecting to a server.
        """
        
        self.emit_event(self.EVENT_STATUS_CHANGED,
                        self.__context_id, self.STATUS_CONNECTING)
        
    
    def _report_buffering(self, value):
        """
        The subclass calls this to report stream buffering.
        """
        
        self.emit_event(self.EVENT_STATUS_CHANGED,
                        self.__context_id, self.STATUS_BUFFERING)
        
        
    def _report_error(self, err, message):
        """
        The subclass calls this to report errors.
        
        @param err: error code
        """
        
        self.stop()
        self.emit_event(self.EVENT_ERROR, self.__context_id, err)
        self.__eof_reached = True
       
        
        
    def play(self):
        """
        Starts playback.
        """
        
        self.__resume_if_necessary()

        if (not self.__playing):
            self.__position = (0, 0)
            self._play()

        self.__playing = True
        print "PLAY"
        self.emit_event(self.EVENT_STATUS_CHANGED,
                        self.__context_id, self.STATUS_PLAYING)
        self.__watch_progress()
        
        
    def pause(self):
        """
        Pauses playback or starts it if it was paused.
        """

        self.__resume_if_necessary()

        if (self.__playing):
            self._stop()
            self.__playing = False
            self.emit_event(self.EVENT_STATUS_CHANGED,
                            self.__context_id, self.STATUS_STOPPED)
        else:
            self._play()
            self.__playing = True
            self.emit_event(self.EVENT_STATUS_CHANGED,
                            self.__context_id, self.STATUS_PLAYING)
            self.__watch_progress()
        
        
    def stop(self):
        """
        Stops playback.
        """

        if (self.__playing):
            self._stop()
            self.update_observer(self.OBS_STOPPED, self.__context_id)
        self.__playing = False
        
        
    def close(self):
        """
        Closes the player.
        """
    
        self._close()
        self.__context_id = 0
        logging.info("%s stopped", `self`)
        
        
    def set_volume(self, volume):
        """
        Sets the audio volume.
        
        @param volume: volume as a value between 0 and 100
        """

        #self._ensure_backend()
        self.__volume = volume
        self._set_volume(volume)    
        
        
    def seek(self, pos):
        """
        Seeks to the given position.
        
        @param pos: position in seconds
        """
    
        self.__resume_if_necessary()
        
        self.__position = (0, 0)
        self._seek(pos)
        self.__playing = True
        self.emit_event(self.EVENT_STATUS_CHANGED,
                        self.__context_id, self.STATUS_PLAYING)
        self.__watch_progress()
        
        
    def seek_percent(self, percent):
        """
        Seeks to the given position.
        
        @param percent: position in percents
        """
    
        nil, total = self.__position
        pos = total * percent / 100.0
        self.seek(pos)



    def rewind(self):
        """
        Rewinds the media.
        @since: 0.96.5
        """
        
        pos, total = self.__position
        if (pos > 0):
            print pos,
            pos = max(0, pos - 30)
            print pos
            self.seek(pos)
            self.__position = self._get_position()
            print pos, self.__position
            self.emit_event(self.EVENT_POSITION_CHANGED,
                            self.__context_id, *self.__position)
            
        
    def forward(self):
        """
        Fast forwards the media.
        @since: 0.96.5
        """

        pos, total = self.__position
        if (pos > 0):
            print pos,
            pos = min(total - 1, pos + 30)
            print pos
            self.seek(pos)
            self.__position = self._get_position()
            print pos, self.__position
            self.emit_event(self.EVENT_POSITION_CHANGED,
                            self.__context_id, *self.__position)


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
        """
        
        raise NotImplementedError
        
        
    def _stop(self):
        """
        To be implemented by the backend.
        """

        raise NotImplementedError


    def _seek(self, pos):
        """
        To be implemented by the backend.
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

