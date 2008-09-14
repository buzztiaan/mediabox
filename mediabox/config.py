from utils.Config import Config

import os


REPEAT_MODE_NONE = "none"
REPEAT_MODE_ONE = "one"
REPEAT_MODE_ALL = "all"

SHUFFLE_MODE_NONE = "none"
SHUFFLE_MODE_ONE = "one"
SHUFFLE_MODE_ALL = "all"


_cfg = Config("",
              [("current_viewer", Config.STRING, ""),
               ("mediaroot", Config.STRING_LIST,
                             ["/home/user/MyDocs/.videos",
                              "/home/user/MyDocs/.sounds",
                              "/home/user/MyDocs/.images"]),
               ("mediaroot_types", Config.INTEGER_LIST, []),
               ("repeat_mode", Config.STRING, REPEAT_MODE_NONE),
               ("shuffle_mode", Config.STRING, SHUFFLE_MODE_NONE),
               ("thumbnails_folder", Config.STRING, 
                              os.path.expanduser("~/.thumbnails/mediabox")),
               ("theme", Config.STRING, "default"),
               ("volume", Config.INTEGER, 50)]
             )


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



def repeat_mode():

    return _cfg["repeat_mode"]
    
    
def set_repeat_mode(m):

    _cfg["repeat_mode"] = m


def shuffle_mode():

    return _cfg["shuffle_mode"]


def set_shuffle_mode(m):

    _cfg["shuffle_mode"] = m


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

