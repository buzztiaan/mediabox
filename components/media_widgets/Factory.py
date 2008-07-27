from com import MediaWidgetFactory, msgs
from VideoWidget import VideoWidget
from AudioWidget import AudioWidget
from ImageWidget import ImageWidget


class Factory(MediaWidgetFactory):

    def __init__(self):
    
        # table: caller_id -> 
        self.__callers = {}
    
        MediaWidgetFactory.__init__(self)
        
        
    def get_mimetypes(self):
    
        return ["audio/*",
                "image/*",
                "video/*",
                "application/ogg",
                "application/vnd.rn-realmedia"]
                
                
    def get_widget_class(self, mimetype):

        if (mimetype.startswith("video/")):
            return VideoWidget
            
        elif (mimetype.startswith("audio/") or
              mimetype == "application/ogg"):
            return AudioWidget

        elif (mimetype.startswith("image/") or
              mimetype == "application/vnd.rn-realmedia"):
            return ImageWidget

