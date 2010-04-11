"""
Runtime container for running components.
"""

from Component import Component
import msgs
from utils import logging

import os
import sys
import gobject


class Container(Component):
    """
    Runtime container for running components.
    The Container loads and instantiates components.
    """
    
    def __init__(self, plugins):
        """
        @param paths: paths where to look for components
        """
    
        self.__components = []
        self.__devices = []
        self.__whitelist = []
        
        Component.__init__(self)
        
        mods = self.__load_modules(plugins)
        delayed_mods = [ mod for mod in mods if hasattr(mod, "delayed") ]
        other_mods = [ mod for mod in mods if not hasattr(mod, "delayed") ]

        for mod in mods:
            self.__register_messages(mod)

        for mod in other_mods:
            self.__load_components(mod)

        self.__report_loadings()
        if (delayed_mods):
            gobject.idle_add(self.__load_delayed_modules, delayed_mods)


    def __report_loadings(self):

        for c in self.__components:
            self.emit_message(msgs.COM_EV_COMPONENT_LOADED, c)

        for dev in self.__devices:
            self.emit_message(msgs.CORE_EV_DEVICE_ADDED, dev.get_device_id(), dev)
            self.emit_message(msgs.COM_EV_COMPONENT_LOADED, dev)

        self.__components = []
        self.__devices = []
        


    def __load_delayed_modules(self, mods):

        mod = mods.pop(0)
        self.__load_components(mod)

        if (mods):
            gobject.idle_add(self.__load_delayed_modules, mods)
        else:
            self.__report_loadings()

        

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
                logging.debug("registering message: %s", msg)
                msgs._register(msg)
        #end if        


    def __load_components(self, mod):
        """
        Loads the components of the given module.
        """

        syspath = sys.path[:]
        sys.path = [mod._syspath] + syspath

        logging.debug("loading module [%s]", mod.__file__)
        
        try:
            classes = mod.get_classes()
        except AttributeError:
            classes = []
        except:
            logging.error(logging.stacktrace())
            classes = []
            
        for c in classes:
            try:
                logging.debug("creating [%s]" % c.__name__)
                comp = c()
                #comp._attach_to_message_bus()
                self.__components.append(comp)
                
            except:
                logging.error("could not instantiate class [%s]:\n%s" %
                              (`c`, logging.stacktrace()))
        #end for        

        try:
            device_classes = mod.get_devices()
        except AttributeError:
            device_classes = []
        except:
            logging.error(logging.stacktrace())
            device_classes = []

        for c in device_classes:
            try:
                logging.debug("adding device [%s]" % c.__name__)
                comp = c()
                #comp._attach_to_message_bus()
                self.__devices.append(comp)

            except:
                logging.error("could not instantiate class [%s]:\n%s" %
                              (`c`, logging.stacktrace()))
        #end for
        
        sys.path = syspath

            
    def __load_modules(self, paths):
    
        return [ self.__load_module(path) for path in paths ]


    def load_module(self, path):
    
        mod = self.__load_module(path)
        if (mod):
            self.__register_messages(mod)
            #self.emit_message(msgs.COM_EV_LOADING_MODULE, mod.__name__)
            self.__load_components(mod)
        #end if
