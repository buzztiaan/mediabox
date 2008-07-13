from com import MediaWidgetFactory, msgs
from VideoWidget import VideoWidget


class Factory(MediaWidgetFactory):

    def __init__(self):
    
        # table: caller_id -> 
        self.__callers = {}
    
        MediaWidgetFactory.__init__(self)
        
        
    def get_mimetypes(self):
    
        return ["audio/*",
                "image/*",
                "video/*"]
                
                
    def get_widget_class(self, mimetype):

        if (mimetype.startswith("video/")):
            return VideoWidget

