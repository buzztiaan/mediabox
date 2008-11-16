from com import Component, msgs
from Thumbnailer import Thumbnailer
from mediabox import config
from utils import logging

# these modules handle the particular media types
import video
import audio
import image

import gtk
import gobject
import os
import time
import threading


class MediaScanner(Component):

    MEDIA_VIDEO = 1
    MEDIA_AUDIO = 2
    MEDIA_IMAGE = 4
    

    def __init__(self):

        # time of the last scan
        self.__scantime = 0
        
        # table: resource -> scantime
        self.__scantimes = {}
        
        # table: root path -> items
        self.__media_items = {}
        
        # table: path -> 1
        self.__media = {}
        
        # paths of previously scanned mediaroots
        self.__scanned_media_roots = []
        
        self.__thumbnailer = Thumbnailer()
        self.__thumbnailer.set_thumb_folder(os.path.abspath(config.thumbdir()))
        
    
        Component.__init__(self)
        
        
        
    def handle_event(self, ev, *args):
    
        if (ev == msgs.MEDIASCANNER_ACT_SCAN):
            mediaroots = args[0]
            self.__scan(mediaroots)
            
        elif (ev == msgs.MEDIASCANNER_SVC_SCAN_FILE):
            f, cb = args[:2]
            u_args = args[2:]
            
            gobject.timeout_add(0, self.__make_thumbnail,
                                self.MEDIA_VIDEO |
                                self.MEDIA_AUDIO |
                                self.MEDIA_IMAGE,
                                f, cb, *u_args)
            #self.__process_media(self.MEDIA_VIDEO |
            #                     self.MEDIA_AUDIO |
            #                     self.MEDIA_IMAGE,
            #                     f, {}, notify = False, recursive = False)
            return 0#self.__thumbnailer.get_thumbnail_path(f)
            
        elif (ev == msgs.MEDIASCANNER_SVC_GET_MEDIA):
            mime_types = args[0]
            return self.__get_media(mime_types)
            
        elif (ev == msgs.MEDIASCANNER_SVC_GET_THUMBNAIL):
            f = args[0]
            return self.__thumbnailer.get_thumbnail_path(f)

        elif (ev == msgs.MEDIASCANNER_SVC_SET_THUMBNAIL):
            f, pbuf = args
            thumbpath = self.__thumbnailer.get_thumbnail_path(f)
            pbuf.save(thumbpath, "jpeg")
            print "saving thumbnail for %s as %s" % (f.name, thumbpath)
            return thumbpath


    def __scan(self, mediaroots):
        """
        Scans the media folders recursively.
        """

        self.__scantime = int(time.time())
        self.emit_event(msgs.MEDIASCANNER_EV_SCANNING_STARTED)
        
        # find out which media roots are new
        new_roots = [ m.resource for m, t in mediaroots
                      if not (m.resource, t) in self.__scanned_media_roots and
                         os.path.exists(m.resource) ]
                
        # find out which media roots have been removed
        mediapaths = [ m.resource for m, t in mediaroots ]
        removed_roots = [ m for m, t in self.__scanned_media_roots
                          if not os.path.exists(m) or not m in mediapaths ]

        # find out which media roots haven't changed
        unchanged_roots = [ (m, t) for m, t in self.__scanned_media_roots
                            if not m in new_roots and not m in removed_roots ]
                          
        logging.debug("new mediaroots:       %s", new_roots)
        logging.debug("removed mediaroots:   %s", removed_roots)
        logging.debug("unchanged mediaroots: %s", unchanged_roots)
                          
        # remove items of removed roots
        for root in removed_roots:
            del self.__media_items[root]
        
        # scan new roots
        self.__scanned_media_roots = unchanged_roots
        self.__media = {}
        to_scan = [ (m, t) for m, t in mediaroots
                    if m.resource in new_roots ]
        for mediaroot, mediatypes in to_scan:
            self.__scanned_media_roots.append((mediaroot.resource, mediatypes))
            logging.info("scanning [%s] for media", mediaroot.resource)
            
            if (not mediaroot in self.__media_items):
                self.__media_items[mediaroot.resource] = []
            
            try:
                self.__process_media(mediaroot, mediatypes, mediaroot, {})
            except:
                import traceback; traceback.print_exc()
                pass

            logging.info("finished scanning [%s]", mediaroot.resource)
        #end for

        # get rid of items which haven't been found now
        for root, nil in to_scan:
            new_items = []            
            for item in self.__media_items[root.resource]:
                scantime = self.__scantimes.get(item.resource, self.__scantime)
                if (scantime < self.__scantime):
                    logging.info("file '%s' is gone", item.resource)
                else:
                    new_items.append(item)
            #end for
            self.__media_items[root.resource] = new_items
        #end for
                    
            
        #for key, item in self.__media.items():
        #    if (self.__scantimes.get(key, self.__scantime) < self.__scantime):
        #        del self.__media[key]
        #end for
             
        self.emit_event(msgs.MEDIASCANNER_EV_SCANNING_FINISHED)
        
        
    def __process_media(self, mediaroot, mediatypes, path, seen):
        """
        Checks the given path for the given mediatypes
        """

        # don't be so stupid to follow circular links
        if (path in seen): return
        seen[path] = True
        
        # skip thumbnail folder
        if (path.resource == self.__thumbnailer.get_thumb_folder()):
            return
            
        # process directory recursively
        if (path.mimetype == path.DIRECTORY):
            for f in path.get_children():
                self.__process_media(mediaroot, mediatypes, f, seen)
        #end if
        
        
        for mediatype, module in [(self.MEDIA_VIDEO, video),
                                  (self.MEDIA_AUDIO, audio),
                                  (self.MEDIA_IMAGE, image)]:

            if (mediatypes & mediatype and module.is_media(path)):
                if (not path.resource in self.__media):
                    self.__media_items[mediaroot.resource].append(path)
                    self.__media[path.resource] = 1
                self.__scantimes[path.resource] = self.__scantime
            #end if
        #end for
        
        
    def __make_thumbnail(self, mediatypes, f, cb, *args):

        def on_generated():
            # no thumbnail generated? remember this
            if (not self.__thumbnailer.has_thumbnail(f)):
                self.__thumbnailer.mark_as_unavailable(f)
            else:
                self.__thumbnailer.unmark_as_unavailable(f)
            
            cb(self.__thumbnailer.get_thumbnail_path(f), *args)
            
        handled = False
        for mediatype, module in [(self.MEDIA_VIDEO, video),
                                  (self.MEDIA_AUDIO, audio),
                                  (self.MEDIA_IMAGE, image)]:

            if (mediatypes & mediatype and module.is_media(f)):
                handled = True

                if (not self.__thumbnailer.is_thumbnail_up_to_date(f)):
                    logging.debug("thumbnailing '%s'", f.resource)
                    
                    # get rid of old thumbnail first
                    self.__thumbnailer.remove_thumbnail(f)

                    try:
                        module.make_thumbnail_async(f,
                                      self.__thumbnailer.get_thumbnail_path(f),
                                      on_generated)
                    except:
                        pass
                        
                else:
                    logging.debug("thumbnail up to date for %s" % f.resource)
                    on_generated()
                #end if
                
                break
                
            #end if
        #end for
        
        if (not handled):
            on_generated()
    
        
         

    def __get_media(self, mime_types):
        """
        Returns the media files of the given mimetypes.
        """
        
        media = []
        for items in self.__media_items.values():
            for f in items:
                for m in mime_types:
                    if (f.mimetype.startswith(m)):
                        media.append(f)
                        continue
                #end for
            #end for
        #end for
            
        #for f in self.__media.values():
        #    for m in mime_types:
        #        if (f.mimetype.startswith(m)):
        #            media.append(f)
        #            continue
        #    #end for
        ##end for

        def comp(a, b): return cmp(a.path.lower(), b.path.lower())
        media.sort(comp)
        
        return media
        
