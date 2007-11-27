try:
    # GNOME
    import gconf
except:
    try:
        # Maemo    
        import gnome.gconf as gconf
    except:
        # last resort...
        from utils import gconftool as gconf

import os


_CLIENT = gconf.client_get_default()
_PREFIX = "/apps/maemo-mediabox/"


def mediaroot():
    return _CLIENT.get_list(_PREFIX +"mediaroot", gconf.VALUE_STRING) or \
           ["/home/user/MyDocs/.videos", "/home/user/MyDocs/.sounds",
            "/home/user/MyDocs/.images"]
        
def set_mediaroot(l):
    _CLIENT.set_list(_PREFIX + "mediaroot", gconf.VALUE_STRING, l)


def thumbdir():
    return _CLIENT.get_string(_PREFIX + "thumbnails_folder") or \
        os.path.expanduser("~/.thumbnails/mediabox")
        


def theme():
    return _CLIENT.get_string(_PREFIX + "theme") or "default"
    
def set_theme(name):
    _CLIENT.set_string(_PREFIX + "theme", name)

