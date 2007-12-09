"""
This package contains the media viewers as sub packages. Valid viewers are
detected automatically.
"""

import os
import sys



def _load_viewer(path):
    
    dirname = os.path.dirname(path)
    name = os.path.basename(path)
    viewer = None
    print name, dirname, path    
    syspath = sys.path[:]
    sys.path = [dirname] + syspath
    try:    
        mod = __import__(name)
        viewer = mod.get_viewer()
    except ImportError:
        print "Could not load viewer [%s]" % name
        import traceback; traceback.print_exc()        
    finally:
        sys.path = syspath
        
    return viewer


def _viewer_comparator(a, b):

    return cmp(a.PRIORITY, b.PRIORITY)


def get_viewers():

    viewers = []
    
    path = os.path.dirname(__file__)
    for f in os.listdir(path):
        if (os.path.isdir(os.path.join(path, f)) and not f.startswith(".")):
            
            viewer = _load_viewer(os.path.join(path, f))
            try:
                if (viewer and viewer.is_available()): viewers.append(viewer)
            except:                
                pass
    #end for
    
    viewers.sort(_viewer_comparator)    
    return viewers

