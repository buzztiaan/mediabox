from com import Thumbnailer
#from ui import pixbuftools
from utils import imageloader
from theme import theme

import gtk


#_PBUF = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, 160, 120)


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
                #_PBUF.fill(0x00000000)
                #pixbuftools.draw_pbuf(_PBUF, theme.mb_frame_image_album, 0, 0)
                # TODO: the frame coords should really be supplied by the theme
                #pixbuftools.fit_pbuf(_PBUF, pbuf, 49, 38, 79, 42)
                path = self._set_thumbnail(f, pbuf)
                del pbuf
            else:
                path = ""
            cb(path, *args)
    
        def on_loaded_image(pbuf):
            if (pbuf):
                #_PBUF.fill(0x00000000)
                #pixbuftools.draw_pbuf(_PBUF, theme.mb_frame_image, 0, 0)
                #pixbuftools.fit_pbuf(_PBUF, pbuf, 7, 7, 142, 102)
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


