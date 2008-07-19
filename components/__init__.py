from com import msgs
from utils import logging

import os
import sys


_COMPONENTS_PATH = os.path.dirname(__file__)


def _list_paths():
    """
    Returns a list of paths of the available components.
    """
    
    paths = []
    
    for f in os.listdir(_COMPONENTS_PATH):
        if (os.path.isdir(os.path.join(_COMPONENTS_PATH, f)) and 
              not f.startswith(".")):
            paths.append(f)
    #end for

    return paths
        
    
def load_components():
    """
    Loads the available components and returns a list of all instantiated
    components.
    """
    
    components = []
    all_classes = []    
    for path in _list_paths():
        syspath = sys.path[:]
        sys.path = [_COMPONENTS_PATH] + syspath
        
        try:
            mod = __import__(path)
            classes = mod.get_classes()
        except:
            logging.error("could not load component [%s]", path)
            import traceback; traceback.print_exc()

        if (hasattr(mod, "messages")):
            for msg in mod.messages:
                msgs.register(msg)
                #logging.debug("registering message [%s]", msg)

        if (not isinstance(classes, list)):
            logging.error("function %s.get_classes() must return a list", path)
            continue

        all_classes += classes
        sys.path = syspath
    #end for

    for c in all_classes:
        try:
            components.append(c())
        except:
            logging.error("could not instantiate class [%s] of [%s]",
                          `c`, path)
            import traceback; traceback.print_exc()
    #end for
        
    return components

