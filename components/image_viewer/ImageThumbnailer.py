from com import Thumbnailer
from mediabox import imageloader
from theme import theme

import gtk


class ImageThumbnailer(Thumbnailer):
    """
    Thumbnailer for image media.
    """

    def __init__(self):
    
        Thumbnailer.__init__(self)

        
    def get_mime_types(self):
    
        return ["image/*",
                "application/x-image-folder"]

    
    def make_quick_thumbnail(self, f):

        if (f.mimetype == "application/x-image-folder"):
            f.frame = (theme.mb_frame_image_album, 14, 10, 133, 96)
        else:
            f.frame = (theme.mb_frame_image, 7, 7, 142, 102)
            
        thumb = self._get_thumbnail(f)
        if (thumb):
            return (thumb, True)
        else:
            return ("", False)

        
    def make_thumbnail(self, f, cb, *args):

        def on_loaded_folder(pbuf):
            if (pbuf):
                path = self._set_thumbnail(f, pbuf)
                del pbuf
            else:
                path = ""
            cb(path, *args)
    
        def on_loaded_image(pbuf):
            if (pbuf):
                path = self._set_thumbnail(f, pbuf)
                del pbuf
            else:
                path = ""
            cb(path, *args)

        if (f.mimetype == "application/x-image-folder"):
            children = f.get_children()
            if (children):
                uri = children[0].resource
                imageloader.load(uri, on_loaded_folder)
            else:
                cb("", *args)

        else:
            uri = f.resource
            imageloader.load(uri, on_loaded_image)


