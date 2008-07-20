from Config import Config

import os



_cfg = Config("",
              [("mediaroot", Config.STRING_LIST,
                             ["/home/user/MyDocs/.videos",
                              "/home/user/MyDocs/.sounds",
                              "/home/user/MyDocs/.images"]),
               ("mediaroot_types", Config.INTEGER_LIST, []),
               ("thumbnails_folder", Config.STRING, 
                              os.path.expanduser("~/.thumbnails/mediabox")),
               ("theme", Config.STRING, "default")]
             )


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


def set_mediaroot():
    
    roots = []
    mtypes = []
    for r, mtype in l:
        roots.append(r)
        mtypes.append(mtype)

    _cfg["mediaroot"] = roots
    _cfg["mediaroot_types"] = mtypes



def thumbdir():

    return _cfg["thumbnails_folder"]


def theme():

    return _cfg["theme"]
    

def set_theme(name):

    _cfg["theme"] = name

