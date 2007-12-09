from viewers.MediaItem import MediaItem

class RadioItem(MediaItem):

    def __init__(self, name):

        MediaItem.__init__(self)
    
        self.__uri = name


    def get_uri(self):
    
        return self.__uri
