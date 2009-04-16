from com import Component
from ui.Widget import Widget


class MediaWidget(Widget, Component):
    """
    Base class for media widgets.
    """

    EVENT_MEDIA_POSITION = "media-position"
    EVENT_MEDIA_EOF = "media-eof"
    EVENT_MEDIA_VOLUME = "media-volume"
    EVENT_FULLSCREEN_TOGGLED = "media-fullscreen-toggled"
    EVENT_MEDIA_PREVIOUS = "media-previous"
    EVENT_MEDIA_NEXT = "media-next"
    EVENT_MEDIA_SCALE = "media-scale"
    """@since: 0.96.5"""
    
    
    DIRECTION_PREVIOUS = 0
    DIRECTION_NEXT = 1
    DIRECTION_NONE = 2
    

    def __init__(self):
    
        self.__controls = None
        
        Component.__init__(self)
        Widget.__init__(self)
        

        
    def load(self, uri, direction = DIRECTION_NEXT):
        """
        Loads media from the given URI. This is either a local file system
        path or an URL.
        """
    
        raise NotImplementedError
        
        
    def preload(self, uri):
        """
        Preloads the given URI, if the media widget supports this.
        """
        
        pass
        
        
    def _set_controls(self, *widgets):
        """
        Sets the control widgets (toolbar widgets) provided by this widget.
        """
        
        self.__controls = list(widgets)


    def get_controls(self):
        """
        Returns the controls of this widget.
        """
        
        return self.__controls[:]


    def play_pause(self):
        """
        Plays or pauses the current file.
        """
        
        pass


    def stop(self):
        """
        Stops playing the current file.
        """
        
        pass
        
        
    def close(self):
        """
        Closes the player.
        """
        
        pass


    def decrement(self):
        """
        Decrements the scaling value.
        """
        
        pass
        
        
    def increment(self):
        """
        Increments the scaling value.
        """
        
        pass
        
        
    def set_volume(self, vol):
        """
        Sets the volume.
        @deprecated: use L{set_scaling} instead
        """
        
        pass
        
        
    def set_scaling(self, v):
        """
        Sets the scaling value.
        @since: 0.96.5
        
        @param v: a scaling value between 0.0 and 1.0
        """
        
        # stay compatible with media widgets that only implement the
        # deprecated set_volume method
        self.set_volume(int(v * 100))


    def rewind(self):
        """
        Rewinds the media.
        @since: 0.96.5
        """
        
        pass
        
        
    def forward(self):
        """
        Fast forwards the media.
        @since: 0.96.5
        """
        
        pass


    def connect_media_position(self, cb, *args):
    
        self._connect(self.EVENT_MEDIA_POSITION, cb, *args)
        
        
    def connect_media_eof(self, cb, *args):
    
        self._connect(self.EVENT_MEDIA_EOF, cb, *args)


    def connect_media_volume(self, cb, *args):
    
        self._connect(self.EVENT_MEDIA_VOLUME, cb, *args)
        

    def connect_fullscreen_toggled(self, cb, *args):
    
        self._connect(self.EVENT_FULLSCREEN_TOGGLED, cb, *args)


    def connect_media_previous(self, cb, *args):
    
        self._connect(self.EVENT_MEDIA_PREVIOUS, cb, *args)


    def connect_media_next(self, cb, *args):
    
        self._connect(self.EVENT_MEDIA_NEXT, cb, *args)


    def connect_media_scaled(self, cb, *args):
    
        self._connect(self.EVENT_MEDIA_SCALE, cb, *args)

