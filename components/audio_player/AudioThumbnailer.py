from com import Thumbnailer, msgs
from ui import pixbuftools
from theme import theme

import gtk


_PBUF = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, 160, 120)


class AudioThumbnailer(Thumbnailer):

    def __init__(self):
    
        Thumbnailer.__init__(self)
        
        
    def get_mime_types(self):
    
        return ["audio/*",
                "application/ogg",
                "application/x-music-folder"]


    def make_quick_thumbnail(self, f):

        thumb = self._get_thumbnail(f)
        if (thumb):
            return (thumb, True)
        else:
            is_final = not f.is_local
            
            if (f.mimetype == "application/x-music-folder"):
                thumb = theme.mb_frame_music.get_path()
            else:
                thumb = theme.mb_filetype_audio.get_path()
            
            return (thumb, is_final)


    def make_thumbnail(self, f, cb, *args):
    
        def on_loaded(pbuf):
            if (pbuf):
                _PBUF.fill(0x00000000)
                pixbuftools.draw_pbuf(_PBUF, theme.mb_frame_music, 0, 0)
                pixbuftools.fit_pbuf(_PBUF, pbuf, 7, 7, 142, 102)
                path = self._set_thumbnail(f, _PBUF)
                del pbuf
            else:
                path = ""
            cb(path, *args)

        if (f.mimetype == "application/x-music-folder"):
            children = f.get_children()
            if (children):
                self.call_service(msgs.COVERSTORE_SVC_GET_COVER,
                                  children[0], on_loaded)
        else:
            self.call_service(msgs.COVERSTORE_SVC_GET_COVER,
                              f, on_loaded)
        
