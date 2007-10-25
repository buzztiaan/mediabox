from viewers.MediaItem import MediaItem

class ImageItem(MediaItem):

    def __init__(self, imagefile):

        MediaItem.__init__(self)
    
        self.__uri = imagefile
        

    def get_uri(self):
    
        return self.__uri
