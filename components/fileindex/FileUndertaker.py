from com import Component, msgs

import os
import time
import gobject


class FileUndertaker(Component):
    """
    Component for removing dead entries from the file index.
    """

    def __init__(self):
    
        Component.__init__(self)
        
        
    def __exists(self, path):
    
        try:
            return os.path.exists(path)
        except:
            return False
        
    
    def __remove_corpses(self):

        corpses = self.call_service(msgs.FILEINDEX_SVC_QUERY,
                                    "File.Path of all")
        gobject.timeout_add(500, self.__remove_corpse, corpses)
        return False
        

    def __remove_corpse(self, corpses):

        now = time.time()
        while (time.time() < now + 0.05 and corpses):
            path = corpses.pop()[0]
            if (not self.__exists(path)):
                self.call_service(msgs.FILEINDEX_SVC_REMOVE, path)
        #end while
        
        if (corpses):
            return True
        else:
            return False


    def handle_CORE_EV_APP_STARTED(self):

        gobject.timeout_add(1000, self.__remove_corpses)


    def handle_FILEINDEX_ACT_SCAN(self):

        self.__remove_corpses()

