from Component import Component
import msgs
from ui.Widget import Widget


class Player(Component, Widget):
    """
    Base class for Player components.
    @since: 0.97
    """

    def __init__(self):
    
        self.__is_active = False
    
        Component.__init__(self)
        Widget.__init__(self)
        
        
    def seconds_to_hms(self, v):
        """
        Useful function for converting seconds into a well-readable H:MM:SS
        format.
        """
        
        v = int(v)
        secs = v % 60
        v /= 60
        mins = v % 60
        v /= 60
        hours = v
        
        if (hours > 0):
            return "%d:%02d:%02d" % (hours, mins, secs)
        else:
            return "%0d:%02d" % (mins, secs)


    def set_player_active(self, value):
        """
        Sets whether this player is active. Only active players may react to
        events.
        """
    
        self.__is_active = value
        
        
    def is_player_active(self):
        """
        Returns whether this player is currently active.
        """
    
        return self.__is_active

        
    def get_mime_types(self):
        """
        Returns supported MIME types as a list of strings. The Wild card '*'
        may be used in the form of 'audio/*'. Wildcard MIME types are consulted
        only as a last resort when looking for an appropriate player.
        
        @return: list of strings
        """
    
        return []


    def load(self, f):
        """
        Loads the given file into the player. Override this method in your
        player implementation.
        
        @param f: file object to load
        """
        
        pass
        
        
    def set_bookmark(self):
        """
        Sets a bookmark for the current position. Override this method in your
        player implementation.
        """
        
        pass
        
        
    def handle_MEDIA_ACT_LOAD(self, f):
    
        pass
