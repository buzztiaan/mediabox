"""
Module for persisting media bookmarks.
"""

from zipfile import ZipFile
import values
import os


_BM_ZIP = os.path.join(values.USER_DIR, "media_bookmarks.zip")



def set_bookmarks(f, bookmarks):
    """
    Sets bookmarks in the given file. Pass an empty list of bookmarks to
    clear all bookmarks in that file.
    
    @param f: file object
    @param bookmarks: list of bookmarks
    """

    out = " ".join([ `b` for b in bookmarks ])
    try:
        bm_zip = ZipFile(_BM_ZIP, os.path.exists(_BM_ZIP) and "a" or "w")
        bm_zip.writestr(f.md5, out)
        bm_zip.close()
    except:
        pass
        
    
def get_bookmarks(f):
    """
    Returns the bookmarks set in the given file.
    
    @param f: file object
    @return: list of bookmarks
    """

    try:
        bm_zip = ZipFile(_BM_ZIP, "r")
        data = bm_zip.read(f.md5)
        bm_zip.close()
        return [ float(b) for b in data.split() ]
    except:
        return []


def clear_all():
    """
    Clears all bookmarks.
    @since: 0.96.5
    """

    os.unlink(_BM_ZIP)

