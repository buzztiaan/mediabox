# Wow, MAFW is an excellent example of useless documentation written by
# technicians. All you can find is how to implement plugins and use playlists,
# but not simple stuff such as controlling the sound volume or setting the
# video overlay window.


from AbstractBackend import AbstractBackend
from utils import c_gobject
from utils import logging

import time
import gtk
import gobject
import ctypes


_MAFW_SEEK_ABSOLUTE = 0
_MAFW_SEEK_RELATIVE = 1

_MAFW_STATE_STOPPED = 0
_MAFW_STATE_PLAYING = 1
_MAFW_STATE_PAUSED = 2
_MAFW_STATE_TRANSITIONING = 3


_MAFW_RENDERER_ERROR_NO_MEDIA = 0
_MAFW_RENDERER_ERROR_URI_NOT_AVAILABLE = 1
_MAFW_RENDERER_ERROR_INVALID_URI = 2
_MAFW_RENDERER_ERROR_MEDIA_NOT_FOUND = 3
_MAFW_RENDERER_ERROR_STREAM_DISCONNECTED = 4
_MAFW_RENDERER_ERROR_TYPE_NOT_AVAILABLE = 5
_MAFW_RENDERER_ERROR_PLAYBACK = 6
_MAFW_RENDERER_ERROR_UNABLE_TO_PERFORM = 7
_MAFW_RENDERER_ERROR_UNSUPPORTED_TYPE = 8
_MAFW_RENDERER_ERROR_UNSUPPORTED_RESOLUTION = 9
_MAFW_RENDERER_ERROR_UNSUPPORTED_FPS = 10
_MAFW_RENDERER_ERROR_DRM = 11
_MAFW_RENDERER_ERROR_DEVICE_UNAVAILABLE = 12
_MAFW_RENDERER_ERROR_CORRUPTED_FILE = 13
_MAFW_RENDERER_ERROR_PLAYLIST_PARSING = 14
_MAFW_RENDERER_ERROR_CODEC_NOT_FOUND = 15
_MAFW_RENDERER_ERROR_VIDEO_CODEC_NOT_FOUND = 16
_MAFW_RENDERER_ERROR_AUDIO_CODEC_NOT_FOUND = 17
_MAFW_RENDERER_ERROR_NO_PLAYLIST = 18
_MAFW_RENDERER_ERROR_INDEX_OUT_OF_BOUNDS = 19
_MAFW_RENDERER_ERROR_CANNOT_PLAY = 20
_MAFW_RENDERER_ERROR_CANNOT_STOP = 21
_MAFW_RENDERER_ERROR_CANNOT_PAUSE = 22
_MAFW_RENDERER_ERROR_CANNOT_SET_POSITION = 23
_MAFW_RENDERER_ERROR_CANNOT_GET_POSITION = 24
_MAFW_RENDERER_ERROR_CANNOT_GET_STATUS = 25


class _GError(ctypes.Structure): pass
_GError._fields_ = [
    ("domain", ctypes.c_uint32),
    ("code", ctypes.c_int),
    ("message", ctypes.c_char_p)
]

class _GList(ctypes.Structure): pass
_GList._fields_ = [
    ("data", ctypes.c_void_p),
    ("next", ctypes.POINTER(_GList)),
    ("prev", ctypes.POINTER(_GList))
]

# callback prototypes
_MAFW_PLAYBACK_CB = ctypes.CFUNCTYPE(None,
                                     ctypes.c_void_p,
                                     ctypes.c_void_p,
                                     ctypes.POINTER(_GError))

_MAFW_POSITION_CB = ctypes.CFUNCTYPE(None,
                                     ctypes.c_void_p,
                                     ctypes.c_int,
                                     ctypes.c_void_p,
                                     ctypes.POINTER(_GError))

_MAFW_EXTENSION_PROPERTY_CB = ctypes.CFUNCTYPE(None,
                                               ctypes.c_void_p,
                                               ctypes.c_char_p,
                                               ctypes.c_void_p,
                                               ctypes.POINTER(_GError))
                                               


class MAFWBackend(AbstractBackend):
    """
    Class for a MAFW backend for Maemo5.
    """            

    def __init__(self):
    
        self.__is_eof = False

        # reference to the MAFW registry gobject
        self.__registry = None

        # reference to the MAFW renderer gobject
        self.__renderer = None
        
        # current state of the renderer
        self.__current_state = _MAFW_STATE_TRANSITIONING
        
        # current position in the stream (used during retrieving the position)
        self.__current_position = -1
        
        # track duration
        self.__duration = -1
        
        self.__to_seek = 0
        
        # sound volume
        self.__volume = 50
        
        # time of loading for profiling
        self.__load_time = 0
        
        
        # time when MediaBox has last changed the sound volume
        self.__last_volume_change_time = 0

        
        # reference to the callbacks, so that they don't get garbage
        # collected too early
        self.__playback_cb = _MAFW_PLAYBACK_CB(self.__playback_cb)
        self.__position_cb = _MAFW_POSITION_CB(self.__position_cb)
        self.__property_cb = _MAFW_EXTENSION_PROPERTY_CB(self.__property_cb)
        
        # MAFW libraries
        self.__mafw = ctypes.CDLL("libmafw.so.0")
        self.__mafw_shared = ctypes.CDLL("libmafw-shared.so.0")

        AbstractBackend.__init__(self)

        # retrieve and initialise registry
        registry_p = self.__mafw.mafw_registry_get_instance()
        if (not registry_p):
            logging.error("could not get MAFW registry")
            return
        #end if
        self.__registry = c_gobject.wrap(registry_p)
        err_p = ctypes.POINTER(_GError)()
        self.__mafw_shared.mafw_shared_init(registry_p,
                                            ctypes.byref(err_p))
        if (err_p):
            print "GError occured", err_p[0].message
            return
        #end if

        # listen for incoming renderers (this should be how we find
        # the gst-renderer)
        self.__registry.connect("renderer_added", self.__on_renderer_added)

        # some renderers could be loaded already (not really...). look for them
        list_p = self.__mafw.mafw_registry_get_renderers(registry_p)
        while (list_p):
    	    item = _GList(list_p[0])
            logging.info("found preloaded MAFW renderer")
            renderer_p = item.data
            self.__register_renderer(c_gobject.wrap(renderer_p))
            list_p = item.next
        #end while


    def _get_icon(self):
    
        from theme import theme
        return theme.mb_backend_mafw


    def __on_renderer_added(self, registry, renderer):

        # renderer ought to be python-wrapped already
        self.__register_renderer(renderer)


    def __register_renderer(self, renderer):
    
        name = ctypes.cast(self.__mafw.mafw_extension_get_name(hash(renderer)),
                           ctypes.c_char_p).value
        #name = self.__mafw.mafw_extension_get_name(hash(renderer))
        
        logging.info("found new MAFW renderer %s", name)
        if (name == "Mafw-Gst-Renderer"):
            logging.info("using MAFW Gst-Renderer")

            # remember renderer and setup callbacks
            self.__renderer = renderer
            self.__renderer.connect("buffering-info", self.__on_buffering)
            self.__renderer.connect("state-changed", self.__on_change_state)
            self.__renderer.connect("metadata-changed", self.__on_change_metadata)
            self.__renderer.connect("property-changed", self.__on_change_property)
            
            # request initial volume
            self.__mafw.mafw_extension_get_property(hash(self.__renderer),
                                                    "volume",
                                                    self.__property_cb,
                                                    None)
        #end if

        
    def __playback_cb(self, renderer, user_data, err):
    
        print "MAFW PLAYBACK", renderer, user_data, err
        if (err):
            print err[0].message

        if (self.__load_time):
            logging.profile(self.__load_time, "[mafw] loaded media")
            self.__load_time = 0


    def __position_cb(self, renderer, pos, user_data, err):
    
        print "MAFW POSITION", pos
        self.__current_position = pos


    def __property_cb(self, extension, name, value_p, err):
    
        print "MAFW PROPERTY RECEIVED", extension, name, value_p, err
        if (name == "volume"):
            value = ctypes.c_uint.from_address(value_p).value
            print "volume", value
            #value = ctypes.cast(value_p, ctypes.c_int_p)[0].value
            self.__volume = value


    def __on_buffering(self, renderer, value):
    
        print "MAFW BUFFERING", value
        self._report_buffering(int(value * 100))


    def __on_change_state(self, renderer, state):
    
        print "MAFW STATE CHANGED", state
        self.__current_state = state
        
        if (state == _MAFW_STATE_STOPPED):
            print "GOT STOPPED BY MAFW"
            self.__is_eof = True
            
        elif (state == _MAFW_STATE_PLAYING and self.__to_seek):
            self._seek(self.__to_seek)
            self.__to_seek = 0


    def __on_change_metadata(self, renderer, name, value):
    
        print "MAFW METADATA CHANGED", name, value
        if (name == "title"):
            self._report_tag("TITLE", value[0])
        elif (name == "artist"):
            self._report_tag("ARTIST", value[0])
        elif (name == "album"):
            self._report_tag("ALBUM", value[0])
        elif (name == "renderer-art-uri"):
            self._report_tag("PICTURE", open(value[0], "r").read())
        elif (name == "duration"):
            self.__duration = value[0]


    def __on_change_property(self, renderer, name, value):
    
        print "MAFW PROPERTY CHANGED", name, value, type(value)
        if (name == "volume" and time.time() > self.__last_volume_change_time + 1):
            volume = value #ctypes.c_uint.from_address(hash(value_p))
            self.__volume = volume
            self._report_volume(volume)


    def _ensure_backend(self):
    
        pass
        

    def _set_window(self, xid):
    
        self.__mafw.mafw_extension_set_property_uint(hash(self.__renderer),
                                                     "xid",
                                                     ctypes.c_uint(xid))


    def _load(self, uri):

        if (self.__renderer):
            self.__is_eof = False
            self.__duration = -1
            self.__load_time = time.time()
            self.__mafw.mafw_renderer_play_uri(hash(self.__renderer),
                                               uri,
                                               self.__playback_cb,
                                               None)
            self._report_volume(self.__volume)
            
        else:            
            self._report_error(self.ERR_NOT_SUPPORTED, "")
        

    def _set_volume(self, volume):

        self.__mafw.mafw_extension_set_property_uint(hash(self.__renderer),
                                                    "volume",
                                                    ctypes.c_uint(volume))
        self.__last_volume_change_time = time.time()
        self.__volume = volume


    def _is_eof(self):
    
        return self.__is_eof


    def _play(self):

        if (self.__current_state == _MAFW_STATE_PAUSED):
            self.__is_eof = False
            self.__mafw.mafw_renderer_resume(hash(self.__renderer),
                                             self.__playback_cb,
                                             None)  

        
    def _stop(self):

        if (self.__current_state == _MAFW_STATE_PLAYING):
            self.__mafw.mafw_renderer_pause(hash(self.__renderer),
                                            self.__playback_cb,
                                            None)


    def _close(self):
    
        if (self.__renderer):
            self.__mafw.mafw_renderer_stop(hash(self.__renderer),
                                           self.__playback_cb,
                                           None)


    def _seek(self, pos):

        # resolution is coarse grained by seconds, WTF..?
        if (self.__current_state == _MAFW_STATE_PLAYING):
            self.__mafw.mafw_renderer_set_position(hash(self.__renderer),
                                                   _MAFW_SEEK_ABSOLUTE,
                                                   int(pos),
                                                   self.__position_cb,
                                                   None)
        else:
            self.__to_seek = pos
            self._play()


    def _get_position(self):
        
        self.__current_position = -1
        self.__mafw.mafw_renderer_get_position(hash(self.__renderer),
                                               self.__position_cb,
                                               None)

        timeout = time.time() + 0.25
        while (time.time() < timeout and self.__current_position == -1):
            #gobject.timeout_add(10, lambda :False)
            gtk.main_iteration(True)
        
        return (self.__current_position, self.__duration)


if __name__ == "__main__":
    import gtk
    mafw = MAFWBackend()
    gtk.main()

