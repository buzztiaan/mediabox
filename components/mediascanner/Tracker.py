from com import Component, msgs
from FileIndex import FileIndex

import commands
import os


class Tracker(Component):
    """
    Media scanner interface for tracker. All the scanning stuff is done by
    tracker, and we simply query its database.
    """
    
    def __init__(self):
    
        self.__files = []
        
        # index for files that is serialized to disk
        self.__file_index = FileIndex()
    
        Component.__init__(self)
        
        
    def handle_MEDIASCANNER_ACT_SCAN(self, mediaroots, rebuild_index):
    
        if (rebuild_index):
            self.__file_index.clear()
        #    self.__tracker_update()

        self.__tracker_files(mediaroots)

        self.emit_message(msgs.MEDIASCANNER_EV_SCANNING_FINISHED)


    def handle_MEDIASCANNER_SVC_GET_MEDIA(self, mime_types):

        return self.__get_media(mime_types)



    def __find_mediaroot(self, path, mediaroots):
    
        for m, n in mediaroots:
            if (path.startswith(m)):
                return m
            #end if
        #end for
        
        return None


    def __tracker_files(self, mediaroots):
    
        lines = []
        fail, out = commands.getstatusoutput("/usr/bin/tracker-files " \
                                             "-s Music -l 10000000")
        if (not fail):
            # first line is skipped as it shows number of results only
            lines += out.splitlines()[1:]

        fail, out = commands.getstatusoutput("/usr/bin/tracker-files " \
                                             "-s Videos -l 10000000")
        if (not fail):
            lines += out.splitlines()[1:]

        fail, out = commands.getstatusoutput("/usr/bin/tracker-files " \
                                             "-s Images -l 10000000")
        if (not fail):
            lines += out.splitlines()[1:]

        self.__file_index.clear_status()
        cnt = 0
        for line in lines:
            path = line.strip()
            fullpath = "file://" + path
            
            mediaroot = self.__find_mediaroot(fullpath, mediaroots)
            if (not mediaroot):
                continue

            f = self.call_service(msgs.CORE_SVC_GET_FILE, fullpath)
            if (f):
                mtime = os.path.getmtime(path)
                self.__file_index.discover_file(mediaroot, f.full_path,
                                                mtime, f.mimetype)
                
            if (cnt % 100 == 0):
                self.emit_message(msgs.MEDIASCANNER_EV_SCANNING_PROGRESS,
                                    f.full_path)
            cnt += 1
        #end for


    def __get_media(self, mime_types):
    
        media = []
        for f in self.__files:
            for m in mime_types:
                if (f.mimetype.startswith(m)):
                    media.append(f)
            #end for
        #end for
        
        return (media, [], [])




    def __get_media(self, mime_types):
        """
        Returns the media files of the given mimetypes.
        """
        
        media = []
        added = []
        removed = []

        unchanged_files = [ self.call_service(msgs.CORE_SVC_GET_FILE, fp)
                            for fp in self.__file_index.get_unchanged_files() ]
                            
        new_files = [ self.call_service(msgs.CORE_SVC_GET_FILE, fp)
                      for fp in self.__file_index.get_new_files() ]
                      
        removed_files = [ (self.call_service(msgs.CORE_SVC_GET_FILE, fp),
                           self.__file_index.get_mimetype(fp))
                          for fp in self.__file_index.get_removed_files() ]
        
        for f in unchanged_files:
            if (not f): continue
            for m in mime_types:
                if (f.mimetype.startswith(m)):
                    media.append(f)
            #end for
        #end for

        for f in new_files:
            if (not f): continue
            for m in mime_types:
                if (f.mimetype.startswith(m)):
                    added.append(f)
                    media.append(f)
            #end for
        #end for

        for f, mt in removed_files:
            if (not f): continue
            for m in mime_types:
                if (mt.startswith(m)):
                    removed.append(f)
            #end for
        #end for
                
        #print "CURRENT", media
        #print "NEW", added
        #print "REMOVED", removed
        return (media, added, removed)

