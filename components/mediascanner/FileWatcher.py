from com import Component, msgs
from pyinotify import WatchManager, Notifier, ProcessEvent, EventsCodes
from mediabox import config as config_mb
from utils import logging

import gobject
import os


class FileWatcher(Component, ProcessEvent):
    """
    Component for watching the media roots for changes using inotify.
    """

    def __init__(self):
    
        # flag for indicating whether the mediascanner is currently running
        self.__currently_scanning = False
        
        # flag for indicating whether the scanner has to run again
        self.__requires_rescan = False
    
        # list (well, actually a dictionary) of active watch descriptors
        self.__watch_descriptors = {}
              
    
        Component.__init__(self)
        
        self.__watch_manager = WatchManager()
        self.__notifier = Notifier(self.__watch_manager, self)
        self.__setup_watches()

        self.__scanner = gobject.timeout_add(1000, self.__scanning_handler)


    def handle_event(self, ev, *args):

        if (ev == msgs.CORE_EV_APP_IDLE_BEGIN):
            gobject.source_remove(self.__scanner)
            
        elif (ev == msgs.CORE_EV_APP_IDLE_END):
            self.__scanner = gobject.timeout_add(1000, self.__scanning_handler)
    
        elif (ev == msgs.MEDIASCANNER_EV_SCANNING_STARTED):
            self.__currently_scanning = True
            self.__setup_watches()

        elif (ev == msgs.MEDIASCANNER_EV_SCANNING_FINISHED):
            self.__currently_scanning = False

           
    def __setup_watches(self):
        """
        Installs watches for the media roots on the filesystem.
        """
    
        # remove all watches
        for path, wd in self.__watch_descriptors.items():
            self.__watch_manager.rm_watch(wd)
        
        # watch media roots
        mediaroots = config_mb.mediaroot()
        for path, t in mediaroots:
            if (path.startswith("file://")):
                path = path[7:]
            elif (path.startswith("/")):
                pass
            else:
                continue
            
            logging.debug("installing filewatch for %s", path)
            self.__watch_manager.add_watch(path, EventsCodes.IN_CREATE |
                                                 EventsCodes.IN_CLOSE_WRITE |
                                                 EventsCodes.IN_DELETE |
                                                 EventsCodes.IN_MOVED_FROM |
                                                 EventsCodes.IN_MOVED_TO,
                                           None, True, True)
        #end for
            
            
    
    def __scanning_handler(self):

        self.__notifier.process_events()
        if (self.__notifier.check_events(0)):
            self.__notifier.read_events()

        if (self.__requires_rescan and not self.__currently_scanning):
            self.emit_event(msgs.CORE_ACT_SCAN_MEDIA, True)
        
        self.__requires_rescan = False
        
        return True
           
            
    def __report_change(self):
        """
        Reports a change in the filesystem.
        """
        
        self.__requires_rescan = True



    def process_IN_CREATE(self, ev):

        if (ev.is_dir):
            logging.debug("IN_CREATE: %s", os.path.join(ev.path, ev.name))
            self.__report_change()


    def process_IN_CLOSE_WRITE(self, ev):

        logging.debug("IN_CLOSE_WRITE: %s", os.path.join(ev.path, ev.name))
        self.__report_change()


    def process_IN_DELETE(self, ev):

        logging.debug("IN_DELETE: %s", os.path.join(ev.path, ev.name))
        self.__report_change()


    def process_IN_MOVED_FROM(self, ev):

        logging.debug("IN_MOVED_FROM: %s", os.path.join(ev.path, ev.name))
        self.__report_change()


    def process_IN_MOVED_TO(self, ev):

        logging.debug("IN_MOVED_TO: %s", os.path.join(ev.path, ev.name))
        self.__report_change()
