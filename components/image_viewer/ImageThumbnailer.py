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
            f.frame = (theme.mb_frame_image_album, 13, 12, 148, 143)
            is_final = False
        else:
            f.frame = (theme.mb_frame_image, 5, 5, 150, 150)
            is_final = True
            
        thumb = self._get_thumbnail(f)
        if (thumb):
            return (thumb, is_final)
        else:
            return (theme.mb_default_image.get_path(), False)

        
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


