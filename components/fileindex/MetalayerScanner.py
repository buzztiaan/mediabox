from com import Component, msgs
from mediabox import config

import os
import gobject
import sqlite3
import threading


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
            
        while (lines):
            line = lines.pop(0)
            path = line.strip()
            try:
                mtime = int(os.path.getmtime(path))
            except:
                continue

            gobject.timeout_add(0, self.call_service,
                                msgs.FILEINDEX_SVC_DISCOVER, path, mtime)
        #end while

        gobject.idle_add(self.emit_message, msgs.UI_ACT_SHOW_INFO,
                         "Scanning for media finished.")


    def handle_COM_EV_APP_STARTED(self):

        if (config.scan_at_startup()):
            t = threading.Thread(target = self.__get_metalayer_files)
            t.setDaemon(True)
            t.start()
            #gobject.idle_add(self.__get_metalayer_files)


    def handle_FILEINDEX_ACT_SCAN(self):
    
        #gobject.idle_add(self.__get_metalayer_files)
        t = threading.Thread(target = self.__get_metalayer_files)
        t.setDaemon(True)
        t.start()

