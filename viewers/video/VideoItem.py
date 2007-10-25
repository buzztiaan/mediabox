from viewers.MediaItem import MediaItem

class VideoItem(MediaItem):

    def __init__(self, videofile):

        MediaItem.__init__(self)
    
        self.__uri = videofile


    def get_uri(self):
    
        return self.__uri
