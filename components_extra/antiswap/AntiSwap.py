from com import Component, msgs
from utils import logging

import os
import gobject


class AntiSwap(Component):
    """
    AntiSwap is a component specially for the Nokia 770 with its limited
    amount of RAM. By regularly allocating a constant amount of RAM for the
    application, swap operations are reduced to a minimum. The application
    is thus much more responsive.
    """

    def __init__(self):

        self.__pid = os.getpid()    
        Component.__init__(self)
        
        self.__alloc()
        # TODO: shut down when idle
        gobject.timeout_add(5000, self.__alloc)
        
        
        
    def __alloc(self):
    
        # get memory consumption      
        size = int(open("/proc/%d/status" % self.__pid, "r") \
               .read().splitlines()[15].split()[1])
        
        remaining = 25 * 1024 - size
        remaining /= 4
        
        if (remaining > 0):
            logging.debug("running AntiSwap to gather %f MB of RAM" \
                          % (remaining / 1024))
            alloc = [0] * remaining
            del alloc
        
        return True
