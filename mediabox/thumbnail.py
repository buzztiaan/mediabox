from utils import mimetypes
from theme import theme
from ui import pixbuftools

import gtk
import os


_WIDTH = 160
_HEIGHT = 120

_PBUF = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, _WIDTH, _HEIGHT)


# cache for thumbnail frames
_frame_cache = {}

# cache for thumbnails
_CACHE_SIZE = 10
_thumbnail_cache = {}
_cache_history = []



def clear_cache():
    """
    Clears the thumbnail cache.
    """
    
    _frame_cache.clear()
    _thumbnail_cache.clear()
    while (_cache_history):
        _cache_history.pop()
    #end while
    
    
    
def render_on_pixbuf(thumbfile, mimetype):
    """
    Decorates the given thumbnail according to the given MIME type and returns
    a pixbuf. This pixbuf is shared and volatile and must NOT be stored for
    later use.
    """

    return _render_thumbnail(None, 0, 0, _WIDTH, _HEIGHT, thumbfile, mimetype)
    
    
def render_on_canvas(cnv, x, y, w, h, thumbfile, mimetype):

    return _render_thumbnail(cnv, x, y, w, h, thumbfile, mimetype)



def _make_frame(mimetype):
    """
    Returns the appropriate frame as pixbuf for the given MIME type, or None
    if there is no frame.
    """

    if (mimetype == "application/x-music-folder"):
        #if (os.path.exists(thumbfile)):
        tx, ty, tw, th = 3, 3, 109, 109
        frame = theme.mb_frame_music
        #else:
        #    tx, ty, tw, th = 0, 0, _WIDTH, _HEIGHT
        #    frame = None

    elif (mimetype == "application/x-image-folder"):
        tx, ty, tw, th = 35, 30, 100, 69
        frame = theme.mb_thumbnail_image_folder
        
    elif (mimetype.endswith("-folder")):
        tx, ty, tw, th = 3, 3, 109, 109
        frame = None       
        
    elif (mimetype in mimetypes.get_audio_types()):
        tx, ty, tw, th = 3, 3, 109, 109
        #if (os.path.exists(thumbfile)):
        frame = None
        #else:
        #    frame = None

    elif (mimetype in mimetypes.get_image_types()):
        tx, ty, tw, th = 7, 7, 142, 102
        frame = theme.mb_frame_image
        
    elif (mimetype in mimetypes.get_video_types()):
        tx, ty, tw, th = 14, 4, 134, 112
        frame = theme.mb_frame_video
        
    else:
        tx, ty, tw, th = 0, 0, _WIDTH, _HEIGHT
        frame = None

    return (frame, tx, ty, tw, th)



def _make_thumbnail(thumbnail, mimetype):
    """
    Loads and returns the thumbnail image.
    """

    # render thumbnail
    if (type(thumbnail) == type("")):
        try:
            thumb_pbuf = gtk.gdk.pixbuf_new_from_file(thumbnail)
            cachable = True
        except:
            thumb_pbuf = _get_fallback_thumbnail(mimetype)
            cachable = False
    else:
        thumb_pbuf = thumbnail
        cachable = False
        
    return (thumb_pbuf, cachable)
    


def _render_thumbnail(cnv, x, y, w, h, thumbfile, mimetype):
    """
    Decorates the given thumbnail according to the given MIME type and,
    if C{cnv} is not C{None}, renders it onto the canvas at the given
    coordinates, or returns a pixbuf, if C{cnv} is C{None}.
    """
   
    if (not cnv):
        _PBUF.fill(0x00000000)
   
    frame_pbuf, tx, ty, tw, th = _frame_cache.get(mimetype, (None, 0, 0, _WIDTH, _HEIGHT))
    if (not frame_pbuf):
        frame_pbuf, tx, ty, tw, th = _make_frame(mimetype)
        _frame_cache[mimetype] = (frame_pbuf, tx, ty, tw, th)
    #end if
    
    # render frame
    if (frame_pbuf):
        sx = w / float(frame_pbuf.get_width())
        sy = h / float(frame_pbuf.get_height())
        scale = min(sx, sy)

        if (cnv):
            cnv.fit_pixbuf(frame_pbuf, x, y, w, h)
        else:
            pixbuftools.draw_pbuf(_PBUF, frame_pbuf, 0, 0)
            
        fx = (w - scale * frame_pbuf.get_width()) / 2
        fy = (h - scale * frame_pbuf.get_height()) / 2
    else:
        sx = w / float(_WIDTH)
        sy = h / float(_HEIGHT)
        scale = min(sx, sy)
        
        fx = (w - scale * _WIDTH) / 2
        fy = (h - scale * _HEIGHT) / 2
    #end if

    pbuf = _thumbnail_cache.get((thumbfile, w, h))
    if (not pbuf):
        #print "not in cache:", thumbfile
        pbuf, cachable = _make_thumbnail(thumbfile, mimetype)
        if (pbuf and cachable and thumbfile):
            _thumbnail_cache[(thumbfile, w, h)] = pbuf
            _cache_history.append((thumbfile, w, h))
        #end if
    #end if
    
    while (len(_cache_history) > _CACHE_SIZE):
        key = _cache_history.pop(0)
        del _thumbnail_cache[key]
    #end while
    
    # render thumbnail
    if (pbuf):
        if (cnv):
            cnv.fit_pixbuf(pbuf, int(x + fx + tx * scale),
                                 int(y + fy + ty * scale),
                                 int(tw * scale), int(th * scale))
        else:
            pixbuftools.fit_pbuf(_PBUF, pbuf,
                                 int(fx + tx * scale),
                                 int(fy + ty * scale),
                                 int(tw * scale), int(th * scale))

        del pbuf
    #end if
    
    if (not cnv):
        return _PBUF
    

def _get_fallback_thumbnail(mimetype):
    """
    Returns the fallback thumbnail for the given MIME type, or None, if there
    is no fallback.
    """

    if (mimetype == "application/x-music-folder"):
        return theme.mb_filetype_loading
        #theme.mb_unknown_album
    elif (mimetype == "application/x-image-folder"):
        #return theme.mb_filetype_loading
        return None
    elif (mimetype.endswith("-folder")):
        return theme.mb_filetype_folder
    elif (mimetype in mimetypes.get_audio_types()):
        return theme.mb_filetype_audio
    elif (mimetype in mimetypes.get_image_types()):
        #return theme.mb_filetype_image
        return theme.mb_filetype_loading
    elif (mimetype in mimetypes.get_video_types()):
        return theme.mb_filetype_loading
    else:
        return theme.mb_filetype_unknown

