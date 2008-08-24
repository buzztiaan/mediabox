"""
Runtime container for running components.
"""

from Component import Component
import msgs
from utils import logging

import os
import sys


class Container(Component):
    """
    Class for running components. The Container loads and instantiates
    components.
    """
    
    def __init__(self, *paths):
    
        self.__components = []
        
        Component.__init__(self)
        
        for p in paths:
            self.load_path(p)

        
    def __find_modules(self, path):
        """
        Returns a list of the modules of all components under the given path.
        """
        
        modules = []

        dirs = os.listdir(path)
        dirs.sort()
        # a module called "core" gets loaded first
        if ("core" in dirs):
            dirs.remove("core")
            dirs = ["core"] + dirs

        for f in dirs:
            comppath = os.path.join(path, f)
            if (os.path.isdir(comppath) and 
                  not f.startswith(".")):
                mod = self.__load_module(comppath)
                modules.append(mod)
        #end for

        return modules


    def __load_module(self, path):
        """
        Loads and returns the module from the given path. Returns None if
        the module could not be loaded.
        """
        
        syspath = sys.path[:]
        sys.path = [os.path.dirname(path)] + syspath
        
        try:
            mod = __import__(os.path.basename(path))
            mod._syspath = os.path.dirname(path)
            sys.path = syspath
            return mod
        except:
            logging.error("could not load component [%s]:\n%s" \
                          % (path, logging.stacktrace()))
            sys.path = syspath
            return None
        
        
    def __register_messages(self, mod):
        """
        Registers the messages of the given module.
        """
        
        if (hasattr(mod, "messages")):
            for msg in mod.messages:
                msgs._register(msg)
        #end if        


    def __load_components(self, mod):
        """
        Loads the components of the given module.
        """

        syspath = sys.path[:]
        sys.path = [mod._syspath] + syspath

        try:
            classes = mod.get_classes()
        except:
            logging.error("could not retrieve classes:\n%s" \
                          % logging.stacktrace())
            classes = []
            
        for c in classes:
            try:
                comp = c()
                comp._attach_to_message_bus()
                self.__components.append(comp)
                
            except:
                logging.error("could not instantiate class [%s]:\n%s" %
                              (`c`, logging.stacktrace()))
        #end for        

        sys.path = syspath


    def load_path(self, path):
        """
        Loads the components from the given path.
        
        @param path: path of components directory
        """
        
        mods = self.__find_modules(path)
        for mod in mods:
            self.__register_messages(mod)
        for mod in mods:
            self.__load_components(mod)

        for c in self.__components:
            self.emit_event(msgs.COM_EV_COMPONENT_LOADED, c)
