from mediabox.MediaViewer import MediaViewer
from ImageDevice import ImageDevice
from theme import theme


class ImageViewer(MediaViewer):

    ICON = theme.mb_viewer_image
    PRIORITY = 30

    def __init__(self):
    
        MediaViewer.__init__(self, ImageDevice(), "Browser", "Image")
        #self.add_tab("EXIF", None, self.__on_tab_exif)
        
        
        
    def __on_tab_exif(self):
    
        pass

