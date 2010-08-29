from com import Component, msgs
from mediabox import config

import commands
import os
import gobject
import threading
import time


class TrackerScanner(Component):
    """
    File scanner component that uses tracker for finding files.
    """

    def __init__(self):
    
        Component.__init__(self)


    def __get_tracker_files(self, category):

        fail, out = commands.getstatusoutput("/usr/bin/tracker-files " \
                                             "-s %s -l 10000000" % category)
        if (not fail):
            # first line is skipped as it shows number of results only
            return out.splitlines()[1:]
        else:
            return []


    def __get_tracker_list(self):
    
        def discover(path, mtime, lock):
            self.call_service(msgs.FILEINDEX_SVC_DISCOVER, path, mtime)
            lock.release()
    
        lines = []
        lines += self.__get_tracker_files("Music")    
        lines += self.__get_tracker_files("Videos")
        lines += self.__get_tracker_files("Images")

        lock = threading.Lock()
        while (lines):
            line = lines.pop(0)
            path = line.strip()
            try:
                mtime = int(os.path.getmtime(path))
            except:
                continue
                
            lock.acquire()
            gobject.idle_add(discover, path, mtime, lock)
            time.sleep(0.01)
        #end while
  
        gobject.idle_add(self.emit_message, msgs.UI_ACT_SHOW_INFO,
                        "Scanning for media finished.")


    def handle_COM_EV_APP_STARTED(self):

        if (config.scan_at_startup()):
            t = threading.Thread(target = self.__get_tracker_list)
            t.setDaemon(True)
            t.start()    

            #self.emit_message(msgs.UI_ACT_SHOW_INFO,
            #              "not querying tracker")


    def handle_FILEINDEX_ACT_SCAN(self):

        t = threading.Thread(target = self.__get_tracker_list)
        t.setDaemon(True)
        t.start()    
        #gobject.idle_add(self.__get_tracker_music, [])

