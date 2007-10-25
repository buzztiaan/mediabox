class MediaItem(object):
    """
    Abstract base class for media items.
    """
       
    def __init__(self):
    
        self.__thumbnail = None


    def set_thumbnail(self, t):
    
        self.__thumbnail = t
        
        
    def get_thumbnail(self):
    
        return self.__thumbnail


    def get_uri(self):
        
        raise NotImplementedError
        
        
