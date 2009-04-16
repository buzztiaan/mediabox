"""
This module reads ID tags of media files. The tags are cached automatically
so that the files don't need to be parsed when reading the tags again.
"""

import config
import values
import idtags

import base64
import os


_TAG_DIR = os.path.join(values.USER_DIR, "idtags")
_STORE_ON_MEDIUM = config.store_thumbnails_on_medium()

# curiously, it appears to be faster without caching...
_USE_CACHE = False


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

    #_ensure_tag_dir()

    res = f.resource
    if (res.startswith("/")):
        tags = idtags.read(res)
    else:
        tags = {}
        
    if (_USE_CACHE and tags):  # don't cache...
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
    Returns a dictionary of tags for the given File object.
    
    @param f: the file to scan
    """
       
    if (not _STORE_ON_MEDIUM):
        prefix = _TAG_DIR

    else:    
        medium = f.medium
        if (not medium or medium == "/"):
            prefix = _TAG_DIR
        else:
            prefix = os.path.join(medium, ".mediabox", "idtags")

    if (not os.path.exists(prefix)):
        try:
            os.makedirs(prefix)
        except:
            pass
    #end if


    tagfile = os.path.join(prefix, f.md5 + ".tags")
    
    if (_USE_CACHE and _have_tags(f, tagfile)):
        return _read_cached_tags(tagfile)
    else:
        return _scan_tags(f, tagfile)

