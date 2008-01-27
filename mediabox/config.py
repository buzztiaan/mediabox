try:
    # GNOME
    import xgconf
except:
    try:
        # Maemo    
        import xgnome.gconf as gconf
    except:
        # last resort...
        from utils import gconftool as gconf

import os


_CLIENT = gconf.client_get_default()
_PREFIX = "/apps/maemo-mediabox/"


def mediaroot():
    
    roots = _CLIENT.get_list(_PREFIX + "mediaroot", gconf.VALUE_STRING) or \
           ["/home/user/MyDocs/.videos", "/home/user/MyDocs/.sounds",
            "/home/user/MyDocs/.images"]
    mtypes = _CLIENT.get_list(_PREFIX + "mediaroot_types", gconf.VALUE_STRING)
    
    ret = []
    while roots:
        r = roots.pop(0)
        if (mtypes):
            mtype = int(mtypes.pop(0))
        else:
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

    _CLIENT.set_list(_PREFIX + "mediaroot", gconf.VALUE_STRING, roots)
    _CLIENT.set_list(_PREFIX + "mediaroot_types", gconf.VALUE_INT, mtypes)


def thumbdir():

    return _CLIENT.get_string(_PREFIX + "thumbnails_folder") or \
        os.path.expanduser("~/.thumbnails/mediabox")
        


def theme():

    return _CLIENT.get_string(_PREFIX + "theme") or "default"
    
def set_theme(name):

    _CLIENT.set_string(_PREFIX + "theme", name)

