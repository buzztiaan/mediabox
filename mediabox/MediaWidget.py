from ui.Widget import Widget


class MediaWidget(Widget):

    EVENT_MEDIA_POSITION = "media-position"
    EVENT_MEDIA_EOF = "media-eof"
    EVENT_FULLSCREEN_TOGGLED = "fullscreen-toggled"
    

    def __init__(self):
    
        self.__controls = None
        
        Widget.__init__(self)
        
        
    def destroy(self):
    
        pass
        
        
    def load(self, uri):
    
        raise NotImplementedError
        
        
    def _set_controls(self, *widgets):
        """
        Creates a new toolbar set.
        """
        
        self.__controls = list(widgets)


    def get_controls(self):
        """
        Returns the controls of this widget.
        """
        
        return self.__controls[:]
        
        
    def connect_media_position(self, cb, *args):
    
        self._connect(self.EVENT_MEDIA_POSITION, cb, *args)
        
        
    def connect_media_eof(self, cb, *args):
    
        self._connect(self.EVENT_MEDIA_EOF, cb, *args)
        

    def connect_fullscreen_toggled(self, cb, *args):
    
        self._connect(self.EVENT_FULLSCREEN_TOGGLED, cb, *args)

