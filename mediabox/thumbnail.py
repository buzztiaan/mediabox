from utils import mimetypes
import theme

import gtk
import os


_WIDTH = 160
_HEIGHT = 120

_PBUF = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, _WIDTH, _HEIGHT)


def render_pixbuf(thumbfile, mimetype):
    """
    Decorates the given thumbnail according to the given MIME type and returns
    a pixbuf. This pixbuf is shared and volatile and must NOT be stored for
    later use.
    """

    if (mimetype == "application/x-directory"):
        fx, fy = 20, 0
        tx, ty, tw, th = 23, 3, 109, 109
        if (os.path.exists(thumbfile)):
            frame = theme.viewer_music_frame
        else:
            frame = None

    elif (mimetype == "audio/x-music-folder"):
        fx, fy = 20, 0
        tx, ty, tw, th = 23, 3, 109, 109
        if (os.path.exists(thumbfile)):
            frame = theme.viewer_music_frame
        else:
            frame = None
        
    elif (mimetype in mimetypes.get_audio_types()):
        fx, fy = 20, 0
        tx, ty, tw, th = 23, 3, 109, 109
        if (os.path.exists(thumbfile)):
            frame = theme.viewer_music_frame
        else:
            frame = None

    elif (mimetype in mimetypes.get_image_types()):
        fx, fy = 0, 0
        tx, ty, tw, th = 7, 7, 142, 102
        frame = theme.viewer_image_frame
        
    elif (mimetype in mimetypes.get_video_types()):
        fx, fy = 0, 0
        tx, ty, tw, th = 14, 4, 134, 112
        frame = theme.viewer_video_film
        
    else:
        fx, fy = 0, 0
        tx, ty, tw, th = 0, 0, _WIDTH, _HEIGHT
        frame = None

    _PBUF.fill(0x00000000)

    # render frame
    if (frame):
        pw, ph = frame.get_width(), frame.get_height()
        subpbuf = _PBUF.subpixbuf(fx, fy, pw, ph)
        frame.composite(subpbuf, 0, 0, pw, ph, 0, 0, 1, 1,
                        gtk.gdk.INTERP_NEAREST, 0xff)
        del subpbuf
        
    # render thumbnail
    try:
        thumb_pbuf = gtk.gdk.pixbuf_new_from_file(thumbfile)
    except:
        thumb_pbuf = _get_fallback_thumbnail(mimetype)
        
    if (thumb_pbuf):
        pw, ph = thumb_pbuf.get_width(), thumb_pbuf.get_height()
        sx = tw / float(pw)
        sy = th / float(ph)
        scale = min(sx, sy)
        pw = int(pw * scale)
        ph = int(ph * scale)
        
        offx = (tw - pw) / 2
        offy = (th - ph) / 2
        subpbuf = _PBUF.subpixbuf(tx + offx, ty + offy, pw, ph)
        thumb_pbuf.composite(subpbuf, 0, 0, pw, ph, 0, 0,
                             scale, scale, gtk.gdk.INTERP_BILINEAR, 0xff)
        del subpbuf
        del thumb_pbuf
        
    return _PBUF


def draw_decorated(cnv, x, y, w, h, thumbfile, mimetype):
    """
    Decorates the given thumbnail according to the given MIME type and renders
    it onto the canvas at the given coordinates.
    """
   
    pbuf = render_pixbuf(thumbfile, mimetype)
    cnv.fit_pixbuf(pbuf, x, y, w, h)



def _get_fallback_thumbnail(mimetype):

    if (mimetype == "application/x-directory"):
        return theme.mb_filetype_folder
    elif (mimetype == "audio/x-music-folder"):
        return theme.mb_unknown_album
    elif (mimetype in mimetypes.get_audio_types()):
        return theme.mb_filetype_audio
    elif (mimetype in mimetypes.get_image_types()):
        return theme.mb_filetype_image
    elif (mimetype in mimetypes.get_video_types()):
        return None #theme.mb_filetype_video
    else:
        return theme.mb_filetype_unknown

