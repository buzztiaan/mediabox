from com import Component, msgs
from mediabox import config

import os
import gobject
import threading
import time


_DCIM_PATHS = ["/home/user/MyDocs/DCIM",
               "/media/mmc1/DCIM"]
               

class DCIMScanner(Component):
    """
    File scanner component for the camera folder.
    """

    def __init__(self):
    
        Component.__init__(self)


    def __get_dcim_files(self):
    
        def discover(path, mtime, lock):
            self.call_service(msgs.FILEINDEX_SVC_DISCOVER, path, mtime)
            lock.release()
    
        lock = threading.Lock()
        for folder in _DCIM_PATHS:
            if (not os.path.isdir(folder)): continue
            
            files = os.listdir(folder)
            print files
            
            for f in files:
                path = os.path.join(folder, f)
                try:
                    mtime = int(os.path.getmtime(path))
                except:
                    continue
                
                lock.acquire()
                gobject.idle_add(discover, path, mtime, lock)
                time.sleep(0.01)
            #end for
        #end for


    def handle_COM_EV_APP_STARTED(self):

        if (config.scan_at_startup()):
            t = threading.Thread(target = self.__get_dcim_files)
            t.setDaemon(True)
            t.start()


    def handle_FILEINDEX_ACT_SCAN(self):

        t = threading.Thread(target = self.__get_dcim_files)
        t.setDaemon(True)
        t.start()

