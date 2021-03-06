from utils.Config import Config

import os


REPEAT_MODE_NONE = "none"
REPEAT_MODE_ONE = "one"
REPEAT_MODE_ALL = "all"

SHUFFLE_MODE_NONE = "none"
SHUFFLE_MODE_ONE = "one"
SHUFFLE_MODE_ALL = "all"

MEDIA_VIDEO = 1
MEDIA_AUDIO = 2
MEDIA_IMAGE = 4

ORIENTATION_LANDSCAPE = "landscape"
ORIENTATION_PORTRAIT = "portrait"
ORIENTATION_AUTOMATIC = "automatic"


_cfg = Config("",
              [("current_device", Config.STRING, ""),
               ("current_viewer", Config.STRING, ""),
               ("mediaroot", Config.STRING_LIST,
                             ["/home/user/MyDocs",
                              "/media"]),
               ("mediaroot_types", Config.INTEGER_LIST, []),
               ("orientation", Config.STRING, ORIENTATION_LANDSCAPE),
               ("portrait_swap_volume", Config.BOOL, True),
               ("repeat_mode", Config.STRING, REPEAT_MODE_NONE),
               ("shuffle_mode", Config.STRING, SHUFFLE_MODE_NONE),
               ("scan_at_startup", Config.BOOL, True),
               ("scan_with_inotify", Config.BOOL, True),
               ("store_thumbnails_on_medium", Config.BOOL, True),
               ("thumbnails_epoch", Config.INTEGER, 0),
               ("thumbnails_folder", Config.STRING, 
                              os.path.expanduser("~/.thumbnails/mediabox")),
               ("theme", Config.STRING, "kuro"),
               ("volume", Config.INTEGER, 50)]
             )


def current_device():

    return _cfg["current_device"]
    

def set_current_device(v):

    _cfg["current_device"] = v


def current_viewer():

    return _cfg["current_viewer"]
    

def set_current_viewer(v):

    _cfg["current_viewer"] = repr(v)


def mediaroot():

    roots = _cfg["mediaroot"]
    mtypes = _cfg["mediaroot_types"]
    
    ret = []
    while roots:
        r = roots.pop(0)
        try:
            mtype = int(mtypes.pop(0))
        except:
            mtype = 7  # %00000111
        ret.append((r, mtype))
    #end while
    
    return ret    


def set_mediaroot(l):
    
    roots = []
    mtypes = []
    for r, mtype in l:
        roots.append(r)
        mtypes.append(mtype)

    _cfg["mediaroot"] = roots
    _cfg["mediaroot_types"] = mtypes


def orientation():

    return _cfg["orientation"]
    
    
def set_orientation(o):

    _cfg["orientation"] = o


def portrait_swap_volume():

    return _cfg["portrait_swap_volume"]
    
    
def set_portrait_swap_volume(v):

    _cfg["portrait_swap_volume"] = v
    

def repeat_mode():

    return _cfg["repeat_mode"]
    
    
def set_repeat_mode(m):

    _cfg["repeat_mode"] = m


def shuffle_mode():

    return _cfg["shuffle_mode"]


def set_shuffle_mode(m):

    _cfg["shuffle_mode"] = m


def scan_at_startup():

    return _cfg["scan_at_startup"]
    
    
def set_scan_at_startup(v):

    _cfg["scan_at_startup"] = v


def scan_with_inotify():

    return _cfg["scan_with_inotify"]
    
    
def set_scan_with_inotify(v):

    _cfg["scan_with_inotify"] = v


def store_thumbnails_on_medium():

    return _cfg["store_thumbnails_on_medium"]
    
    
def set_store_thumbnails_on_medium(v):

    _cfg["store_thumbnails_on_medium"] = v


def thumbnails_epoch():

    return _cfg["thumbnails_epoch"]


def set_thumbnails_epoch(v):

    _cfg["thumbnails_epoch"] = v


def thumbdir():

    return _cfg["thumbnails_folder"]


def theme():

    return _cfg["theme"]
    

def set_theme(name):

    _cfg["theme"] = name


def volume():

    return _cfg["volume"]
    
    
def set_volume(v):

    _cfg["volume"] = v

