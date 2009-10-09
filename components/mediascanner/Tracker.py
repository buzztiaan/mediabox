from com import Component, msgs

import commands


class Tracker(Component):
    """
    Media scanner interface for tracker. All the scanning stuff is done by
    tracker, and we simply query its database.
    """
    
    def __init__(self):
    
        self.__files = []
    
        Component.__init__(self)
        
        
    def handle_MEDIASCANNER_ACT_SCAN(self, mediaroots, rebuild_index):
    
        if (rebuild_index):
            self.__tracker_update()

        self.__tracker_files(mediaroots)

        self.emit_message(msgs.MEDIASCANNER_EV_SCANNING_FINISHED)


    def handle_MEDIASCANNER_SVC_GET_MEDIA(self, mime_types):

        return self.__get_media(mime_types)



    def __is_on_mediaroots(self, path, mediaroots):
    
        for m, n in mediaroots:
            if (path.startswith(m)):
                return True
            #end if
        #end for
        
        return False


    def __tracker_files(self, mediaroots):
    
        fail, out = commands.getstatusoutput("/usr/bin/tracker-files " \
                                             "-s files -l 10000000")
        self.__files = []
        if (not fail):
            cnt = 0
            for line in out.splitlines():
                path = "file://" + line.strip()
                
                if (not self.__is_on_mediaroots(path, mediaroots)):
                    continue

                f = self.call_service(msgs.CORE_SVC_GET_FILE, path)
                if (f):
                    self.__files.append(f)
                    
                if (cnt % 100 == 0):
                    self.emit_message(msgs.MEDIASCANNER_EV_SCANNING_PROGRESS,
                                      path)
                cnt += 1
            #end for
        #end if


    def __get_media(self, mime_types):
    
        media = []
        for f in self.__files:
            for m in mime_types:
                if (f.mimetype.startswith(m)):
                    media.append(f)
            #end for
        #end for
        
        return (media, [], [])

