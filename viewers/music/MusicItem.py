from viewers.MediaItem import MediaItem

class MusicItem(MediaItem):

    def __init__(self, album):

        MediaItem.__init__(self)
    
        self.__uri = album


    def get_uri(self):
    
        return self.__uri
