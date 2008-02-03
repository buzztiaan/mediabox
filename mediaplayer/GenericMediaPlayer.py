try:
    from utils.Observable import Observable as _Observable
except:
    class _Observable(object):
        def update_observer(*args): pass
        def add_observer(*args): pass
        def remove_observer(*args): pass


class MPlayerError(StandardError): pass
class MPlayerNotFoundError(MPlayerError): pass
class MPlayerDiedError(MPlayerError): pass
class FileNotFoundError(MPlayerError): pass
class InvalidFileError(MPlayerError): pass
        

class GenericMediaPlayer(_Observable):
    """
    Base class for media player implementations.
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
    ERR_NOT_SUPPORTED = 3
    
    
    def __init__(self):
    
        pass


    def __repr__(self):
    
        return self.__class__.__name__

       
    def is_available(self):
    
        return True
        
        
    def handles(self, filetype):
    
        return True
        
        
    def set_window(self, xid):
    
        pass
        
        
    def set_options(self, opts):
    
        pass
        
        
    def load_audio(self, uri):
    
        return self.load(uri)
       
        
    def load_video(self, uri):
    
        return self.load(uri)
        
        
    def load(self, uri):
    
        raise NotImplementedError
        
        
    def play(self):
    
        raise NotImplementedError
        
        
    def pause(self):
    
        raise NotImplementedError
        
        
    def stop(self):
    
        raise NotImplementedError
        
        
    def set_volume(self, volume):
    
        raise NotImplementedError
        
        
    def seek(self, pos):
    
        raise NotImplementedError
        
        
    def seek_percent(self, percent):
    
        raise NotImplementedError
        
        
    def get_position(self):
    
        raise NotImplementedError
        
        
    def show_text(self, text, duration):
    
        pass
        
        
    def is_playing(self):
    
        raise NotImplementedError
        
        
    def has_video(self):
    
        raise NotImplementedError
        
        
    def has_audio(self):
    
        raise NotImplementedError

