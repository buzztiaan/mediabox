from Component import Component
from utils.EventEmitter import EventEmitter


class MediaOutput(Component, EventEmitter):
    """
    Base class for media output components.
    @since: 2009.10.31
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

    # events
    EVENT_ERROR = "event-error"
    EVENT_VOLUME_CHANGED = "event-volume-changed"
    EVENT_STATUS_CHANGED = "event-status-changed"
    EVENT_POSITION_CHANGED = "event-position-changed"
    EVENT_ASPECT_CHANGED = "event-aspect-changed"
    EVENT_TAG_DISCOVERED = "event-tag-discovered"
    
    
    TITLE = "Without a Name"

    def __init__(self):
    
        Component.__init__(self)
        EventEmitter.__init__(self)


    def connect_error(self, cb, *args):
    
        self._connect(self.EVENT_ERROR, cb, *args)


    def connect_volume_changed(self, cb, *args):
    
        self._connect(self.EVENT_VOLUME_CHANGED, cb, *args)
        

    def connect_status_changed(self, cb, *args):
    
        self._connect(self.EVENT_STATUS_CHANGED, cb, *args)


    def connect_position_changed(self, cb, *args):
    
        self._connect(self.EVENT_POSITION_CHANGED, cb, *args)
        
        
    def connect_aspect_changed(self, cb, *args):
    
        self._connect(self.EVENT_ASPECT_CHANGED, cb, *args)


    def connect_tag_discovered(self, cb, *args):
    
        self._connect(self.EVENT_TAG_DISCOVERED, cb, *args)        

        
    def load_audio(self, f):
    
        pass
        
        
    def load_video(self, f):
    
        pass
        
        
    def play(self):
    
        pass
        
        
    def pause(self):
    
        pass
        
        
    def stop(self):
    
        pass
        
        
    def seek(self, pos):
    
        pass


    def seek_percent(self, percent):
    
        pass


    def rewind(self):
    
        pass
        
        
    def forward(self):
    
        pass
        
        
    def set_volume(self, vol):
    
        pass


    def set_window(self, xid):
    
        pass

