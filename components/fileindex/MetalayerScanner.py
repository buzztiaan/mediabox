from com import Component, msgs
from mediabox import config

import os
import gobject
import time
import sqlite3


_META_DB = os.path.expanduser("~/.meta_storage")


class MetalayerScanner(Component):
    """
    File scanner component that uses the Diablo Metalayer Crawler for finding
    files.
    """

    def __init__(self):
    
        Component.__init__(self)


    def __get_metalayer_files(self):

        try:
            conn = sqlite3.connect(_META_DB)
        except:
            return []
            
        csr = conn.cursor()
        csr.execute("SELECT Filename " \
                    "FROM Metadata " \
                    "WHERE Present=1")
        lines = [ row[0] for row in csr ]
        conn.close()
        
        gobject.idle_add(self.__process_metalayer_files, lines)


    def __process_metalayer_files(self, lines):
    
        now = time.time()
        while (time.time() < now + 0.05 and lines):
            line = lines.pop(0)
            path = line.strip()
            try:
                mtime = int(os.path.getmtime(path))
                self.call_service(msgs.FILEINDEX_SVC_DISCOVER, path, mtime)
            except:
                pass
        #end while
        
        if (lines):
            return True
        else:
            self.emit_message(msgs.UI_ACT_SHOW_INFO,
                              "Scanning for media finished.")
            return False


    def handle_COM_EV_APP_STARTED(self):

        if (config.scan_at_startup()):
            gobject.idle_add(self.__get_metalayer_files)


    def handle_FILEINDEX_ACT_SCAN(self):
    
        gobject.idle_add(self.__get_metalayer_files)

