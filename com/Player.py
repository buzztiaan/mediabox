from Component import Component
import msgs
from ui.Widget import Widget


class Player(Component, Widget):
    """
    Base class for Player components.
    @since: 0.97
    """

    def __init__(self):
    
        Component.__init__(self)
        Widget.__init__(self)
        
        
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
        
        
    def handle_MEDIA_ACT_LOAD(self, f):
    
        pass
