from com import Thumbnailer
from theme import theme


class GenericThumbnailer(Thumbnailer):

    def __init__(self):
    
        Thumbnailer.__init__(self)
        
        
    def get_mime_types(self):
    
        return ["application/x-folder",
                "application/x-unknown"]


    def make_quick_thumbnail(self, f):

        if (f.mimetype == "application/x-folder"):    
            return (theme.mb_filetype_folder.get_path(), True)
        else:
            return (theme.mb_filetype_unknown.get_path(), True)

