from com import MediaWidgetFactory, msgs
from VideoWidget import VideoWidget


class Factory(MediaWidgetFactory):

    def __init__(self):
    
        MediaWidgetFactory.__init__(self)
        
        
    def get_mimetypes(self):
    
        return ["audio/*",
                "image/*",
                "video/*"]
                
                
    def new_widget(self, mimetype):

        if (mimetype.startswith("video/")):
            return VideoWidget()

