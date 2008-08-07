from com import MediaWidgetFactory, msgs
from VideoWidget import VideoWidget
from AudioWidget import AudioWidget
from ImageWidget import ImageWidget
from utils import mimetypes


class Factory(MediaWidgetFactory):

    def __init__(self):
    
        # table: caller_id -> 
        self.__callers = {}
    
        MediaWidgetFactory.__init__(self)
        
        
    def get_mimetypes(self):
    
        return mimetypes.get_audio_types() + \
               mimetypes.get_video_types() + \
               mimetypes.get_image_types()
                
                
    def get_widget_class(self, mimetype):

        if (mimetype in mimetypes.get_video_types() + ["video/*"]):
            return VideoWidget
            
        elif (mimetype in mimetypes.get_audio_types() + ["audio/*"]):
            return AudioWidget

        elif (mimetype in mimetypes.get_image_types() + ["image/*"]):
            return ImageWidget

