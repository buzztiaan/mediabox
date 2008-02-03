from GenericMediaPlayer import *
import gobject


class _DummyPlayer(GenericMediaPlayer):
    """
    Singleton class for a dummy player which cannot play anything.
    """            

    def __init__(self):
        """
        Creates the DummyPlayer singleton.
        """

        GenericMediaPlayer.__init__(self)
        
        self.__context_id = 0


    def is_available(self):
        
        return True
        

    def set_window(self, xid):
    
        pass
        
        
    def set_options(self, opts):
    
        pass


    def load_audio(self, uri):

        return self.load(uri)


    def load_video(self, uri):
    
        return self.load(uri)
        

    def load(self, uri, ctx_id = -1):

        def f():
            self.update_observer(self.OBS_ERROR, self.__context_id,
                                 self.ERR_NOT_SUPPORTED)
        gobject.idle_add(f)

        if (ctx_id != -1):
            self.__context_id = ctx_id
        else:
            self.__context_id +=1
        print "CTX", self.__context_id
        return self.__context_id
        


    def set_volume(self, volume):

        pass


    def play(self):

        pass           

        
    def pause(self):

        pass          


    def close(self):
    
        pass



    def stop(self):

        pass


    def seek(self, pos):

        pass    


    def seek_percent(self, pos):

        pass    


    def get_position(self):
         
        return (0, 0)
        
        
    def show_text(self, text, duration):

        pass
        

    def is_playing(self):
        """
        Returns whether the player is currently playing.
        """
    
        return False
    
    
    
    def has_video(self):

        return False


    def has_audio(self):
        
        return False
        


_singleton = _DummyPlayer()
def DummyPlayer(): return _singleton

