from ui.Widget import Widget


class MediaWidget(Widget):
    """
    Base class for media widgets.
    """

    EVENT_MEDIA_POSITION = "media-position"
    EVENT_MEDIA_EOF = "media-eof"
    EVENT_MEDIA_VOLUME = "media-volume"
    EVENT_FULLSCREEN_TOGGLED = "media-fullscreen-toggled"
    EVENT_MEDIA_PREVIOUS = "media-previous"
    EVENT_MEDIA_NEXT = "media-next"
    

    def __init__(self):
    
        self.__controls = None
        
        Widget.__init__(self)
        

        
    def load(self, uri):
        """
        Loads media from the given URI. This is either a local file system+
        path or an URL.
        """
    
        raise NotImplementedError
        
        
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


    def stop(self):
        """
        Stops playing the current file.
        """
        
        pass


    def decrement(self):
        """
        Performs a DECREMENT action.
        """
        
        pass
        
        
    def increment(self):
        """
        Performs an INCREMENT action.
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

