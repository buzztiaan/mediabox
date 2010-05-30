from com import Thumbnailer, msgs
from theme import theme

import gtk


class AudioThumbnailer(Thumbnailer):
    """
    Thumbnailer for audio-related media.
    """

    def __init__(self):
    
        Thumbnailer.__init__(self)
        
        
    def get_mime_types(self):
    
        return ["audio/*",
                "application/ogg",
                "application/x-music-folder"]


    def make_quick_thumbnail(self, f):

        #if (f.mimetype == "application/x-music-folder"):
        f.frame = (theme.mb_frame_music_album, 25, 5, 106, 106)
        #else:
        #    f.frame = (theme.mb_file_audio, 0, 40, 80, 80)

        thumb = self._get_thumbnail(f)
        if (thumb):
            return (thumb, True)
        else:
            is_final = not f.is_local            
            return ("", is_final)


    def make_thumbnail(self, f, cb, *args):
    
        def on_loaded(pbuf, mimetype):
            if (pbuf):
                path = self._set_thumbnail(f, pbuf)    
                del pbuf
            else:
                path = ""
            cb(path, *args)

        if (f.mimetype == "application/x-music-folder"):
            children = f.get_children()
            if (children):
                self.call_service(msgs.COVERSTORE_SVC_GET_COVER,
                                  children[0], on_loaded, f.mimetype)
            else:
                cb("", *args)
                
        else:
            self.call_service(msgs.COVERSTORE_SVC_GET_COVER,
                              f, on_loaded, f.mimetype)
        
