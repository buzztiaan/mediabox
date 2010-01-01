from com import Component, msgs
from mediabox import config

import os
import gobject


_DOTTED_WHITELIST = [".images", ".sounds", ".videos"]


class SimpleScanner(Component):

    def __init__(self):
    
        self.__homedir = os.path.expanduser("~")
    
        Component.__init__(self)


    def __file_walker(self, files):

        path = files.pop(0)
        try:
            mtime = int(os.path.getmtime(path))
        except:
            return True
        self.call_service(msgs.FILEINDEX_SVC_DISCOVER, path, mtime)
        
        if (files):
            return True
        else:
            self.emit_message(msgs.UI_ACT_SHOW_INFO,
                              "Finished indexing media.")
            return False




    def __scan(self):

        paths = []
        for dirpath, dirnames, files in os.walk(self.__homedir):
            #print "scanning", dirpath
            for f in files:
                path = os.path.join(dirpath, f)
                paths.append(path)
            #end for
            
            # don't enter hidden directories
            dotted = [ d for d in dirnames
                       if d.startswith(".") and not d in _DOTTED_WHITELIST ]
            while (dotted): dirnames.remove(dotted.pop())
        #end for

        gobject.idle_add(self.__file_walker, paths)        


    def handle_CORE_EV_APP_STARTED(self):

        if (config.scan_at_startup()):
            self.__scan()


    def handle_FILEINDEX_ACT_SCAN(self):
    
        self.__scan()

