from com import Component, msgs
from mediabox import config

import commands
import os
import gobject
import time


class TrackerScanner(Component):
    """
    FileScanner that uses tracker for finding files.
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


    def __get_tracker_music(self, lines):
    
        lines += self.__get_tracker_files("Music")
        gobject.idle_add(self.__get_tracker_videos, lines)


    def __get_tracker_videos(self, lines):
    
        lines += self.__get_tracker_files("Videos")
        gobject.idle_add(self.__get_tracker_images, lines)


    def __get_tracker_images(self, lines):
    
        lines += self.__get_tracker_files("Images")
        gobject.idle_add(self.__process_tracker_files, lines)


    def __process_tracker_files(self, lines):
    
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


    def handle_CORE_EV_APP_STARTED(self):

        if (config.scan_at_startup()):
            gobject.idle_add(self.__get_tracker_music, [])


    def handle_FILEINDEX_ACT_SCAN(self):
    
        gobject.idle_add(self.__get_tracker_music, [])

