from com import Component, msgs
from mediabox import config

import os
import time
import threading
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
        
        t = threading.Thread(target = self.__remove_corpse, args = [corpses])
        t.setDaemon(True)
        t.start()    
        

    def __remove_corpse(self, corpses):

        def remove(path, lock):
            self.call_service(msgs.FILEINDEX_SVC_REMOVE, path)
            lock.release()
            
        lock = threading.Lock()
        while (corpses):        
            path = corpses.pop()[0]
            if (not self.__exists(path)):
                lock.acquire()
                gobject.idle_add(remove, path, lock)
                time.sleep(0.1)
        #end while


    def handle_COM_EV_APP_STARTED(self):

        #if (config.scan_at_startup()):
        pass #self.__remove_corpses()
            

    def handle_FILEINDEX_ACT_BURY(self):

        self.__remove_corpses()

