"""
Module for persisting media bookmarks.
"""

from zipfile import ZipFile
import values
import os


#_BM_DIR = os.path.join(values.USER_DIR, "bookmarks")
_BM_ZIP = os.path.join(values.USER_DIR, "media_bookmarks.zip")


def set_bookmarks(f, bookmarks):

    out = " ".join([ `b` for b in bookmarks ])
    try:
        bm_zip = ZipFile(_BM_ZIP, os.path.exists(_BM_ZIP) and "a" or "w")
        bm_zip.writestr(f.md5, out)
        bm_zip.close()
    except:
        pass
    
    
def get_bookmarks(f):

    try:
        bm_zip = ZipFile(_BM_ZIP, "r")
        data = bm_zip.read(f.md5)
        bm_zip.close()
        return [ float(b) for b in data.split() ]
    except:
        return []



"""
def _ensure_bm_dir():

    if (not os.path.exists(_BM_DIR)):
        try:
            os.makedirs(_BM_DIR)
        except:
            pass


def set_bookmarks(f, bookmarks):

    _ensure_bm_dir()
    bm_file = os.path.join(_BM_DIR, f.md5)
    out = " ".join([ `b` for b in bookmarks ])
    if (not bookmarks):
        try:            
            os.unlink(bm_file)
        except:
            pass
    else:
        try:
            open(bm_file, "w").write(out)
        except:
            pass
    
    
def get_bookmarks(f):

    _ensure_bm_dir()
    bm_file = os.path.join(_BM_DIR, f.md5)
    try:
        data = open(bm_file, "r").read()
        return [ float(b) for b in data.split() ]
    except:
        return []
"""

