import values
import idtags

import base64
import os


_TAG_DIR = os.path.join(values.USER_DIR, "idtags")


def _ensure_tag_dir():
    
    if (not os.path.exists(_TAG_DIR)):
        try:
            os.makedirs(_TAG_DIR)
        except:
            pass
    #end if


def _have_tags(f, tagfile):

    res = f.resource
    if (os.path.exists(tagfile)):
        if (res.startswith("/")):
            if (os.path.exists(f.resource)):
                if (os.path.getmtime(res) < os.path.getmtime(tagfile)):
                    return True
    #end if

    return False
    

def _scan_tags(f, tagfile):

    _ensure_tag_dir()

    res = f.resource
    if (res.startswith("/")):
        tags = idtags.read(res)
    else:
        tags = {}
        
    if (tags):
        try:
            fd = open(tagfile, "w")
            for k, v in tags.items():
                fd.write("%s=%s\n" % (k, base64.b64encode(v)))
            fd.close()
        except:
            pass
    #end if
    
    return tags
    
    
def _read_cached_tags(tagfile):

    try:
        fd = open(tagfile, "r")
        lines = fd.readlines()
        fd.close()
    except:
        return {}
    
    tags = {}
    for line in lines:
        idx = line.find("=")
        key = line[:idx]
        value = base64.b64decode(line[idx + 1:-1])
        tags[key] = value
    #end for
    
    return tags


def get_tags(f):
    """
    Returns a dictionary of tags.
    
    @param f: the file to scan
    """
    
    tagfile = os.path.join(_TAG_DIR, f.md5 + ".tags")
    if (_have_tags(f, tagfile)):
        return _read_cached_tags(tagfile)
    else:
        return _scan_tags(f, tagfile)

