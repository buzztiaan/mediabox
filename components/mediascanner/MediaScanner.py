from com import Component, events
from Thumbnailer import Thumbnailer
from mediabox import config
from utils import logging

# these modules handle the particular media types
import video
import audio
import image

import md5
import os
import time


class MediaScanner(Component):

    MEDIA_VIDEO = 1
    MEDIA_AUDIO = 2
    MEDIA_IMAGE = 4
    

    def __init__(self):

        # time of the last scan
        self.__scantime = 0
        
        # table: resource -> scantime
        self.__scantimes = {}
        
        # table: path -> item
        self.__media = {}
        
        self.__thumbnailer = Thumbnailer()    
        self.__media_roots = []
        
    
        Component.__init__(self)
        
        
        
    def handle_event(self, ev, *args):
    
        if (ev == events.MEDIASCANNER_ACT_SCAN):
            mediaroots = args[0]
            self.__scan(mediaroots)
            return True
            
        elif (ev == events.MEDIASCANNER_SVC_GET_MEDIA):
            mime_types = args[0]
            return self.__get_media(mime_types)
            
        elif (ev == events.MEDIASCANNER_SVC_GET_THUMBNAIL):
            f = args[0]
            return self.__thumbnailer.get_thumbnail_path(f)




    def __scan(self, mediaroots):
        """
        Scans the media folders recursively.
        """

        self.__thumbnailer.set_thumb_folder(os.path.abspath(config.thumbdir()))
        self.__scantime = int(time.time())
        self.emit_event(events.MEDIASCANNER_EV_SCANNING_STARTED)
        
        for mediaroot, mediatypes in mediaroots:
            logging.info("scanning [%s] for media", mediaroot.resource)
            
            try:
                self.__process_media(mediatypes, mediaroot, {})
            except:
                import traceback; traceback.print_exc()
                pass

            logging.debug("finished scanning [%s]", mediaroot.resource)
        #end for

        # get rid of items which haven't been found now
        for key, item in self.__media.items():
            if (self.__scantimes.get(key, self.__scantime) < self.__scantime):
                del self.__media[key]
        #end for
        
        self.emit_event(events.MEDIASCANNER_EV_SCANNING_FINISHED)
        
        
    def __process_media(self, mediatypes, path, seen):
        """
        Checks the given path for the given mediatypes
        """

        # don't be so stupid to follow circular links
        if (path in seen): return
        seen[path] = True
        
        # skip thumbnail folder
        if (path.resource == config.thumbdir()):
            return
               
        # process directory recursively
        if (path.mimetype == path.DIRECTORY):
            for f in path.get_children():
                self.__process_media(mediatypes, f, seen)
        #end if
        
        for mediatype, module in [(self.MEDIA_VIDEO, video),
                                  (self.MEDIA_AUDIO, audio),
                                  (self.MEDIA_IMAGE, image)]:

            if (mediatypes & mediatype and module.is_media(path)):
                path.md5 = md5.new(path.path).hexdigest()
                logging.debug("thumbnailing [%s]", path.resource)
                
                self.__media[path.resource] = path
                self.__scantimes[path.resource] = self.__scantime
                
                if (not self.__thumbnailer.is_thumbnail_up_to_date(path)):
                    # get rid of old thumbnail first
                    self.__thumbnailer.remove_thumbnail(path)
                    try:
                        module.make_thumbnail(path,
                                   self.__thumbnailer.get_thumbnail_path(path))
                    except:
                        import traceback; traceback.print_exc()
                        pass
                    
                    # no thumbnail generated? remember this
                    if (not self.__thumbnailer.has_thumbnail(path)):
                        self.__thumbnailer.mark_as_unavailable(path)
                    else:
                        self.__thumbnailer.unmark_as_unavailable(path)
                    
                        self.emit_event(events.MEDIASCANNER_EV_THUMBNAIL_GENERATED,
                                   self.__thumbnailer.get_thumbnail_path(path),
                                   path)
                
                else:
                    logging.debug("thumbnail up to date: %s" % path.resource)
                #end if
             #end if
         #end for
         

    def __get_media(self, mime_types):
        """
        Returns the media files of the given mimetypes.
        """
        
        media = []
        for f in self.__media.values():
            for m in mime_types:
                if (f.mimetype.startswith(m)):
                    media.append(f)
                    continue
            #end for
        #end for

        def comp(a, b): return cmp(a.path.lower(), b.path.lower())
        media.sort(comp)
        
        return media
        
