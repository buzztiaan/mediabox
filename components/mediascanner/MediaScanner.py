from com import Component, msgs
from FileIndex import FileIndex
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
               
        # index for files that is serialized to disk
        self.__file_index = FileIndex()
        
        # table: root path -> types
        self.__mediaroot_types = {}
        
        self.__thumbnailer = Thumbnailer()
        self.__thumbnailer.set_thumb_folder(os.path.abspath(config.thumbdir()))
        
    
        Component.__init__(self)
        
        
        for mediaroot, types in config.mediaroot():
            self.__mediaroot_types[mediaroot] = types
        
        
        
    def handle_message(self, ev, *args):
    
        if (ev == msgs.MEDIASCANNER_ACT_SCAN):
            mediaroots, rebuild_index = args
            self.__scan(mediaroots, rebuild_index)
            
        elif (ev == msgs.MEDIASCANNER_SVC_CREATE_THUMBNAIL):
            f, cb = args[:2]
            u_args = args[2:]
            
            gobject.timeout_add(0, self.__make_thumbnail,
                                self.MEDIA_VIDEO |
                                self.MEDIA_AUDIO |
                                self.MEDIA_IMAGE,
                                f, cb, *u_args)
            return 0#self.__thumbnailer.get_thumbnail_path(f)
            
        elif (ev == msgs.MEDIASCANNER_SVC_GET_MEDIA):
            mime_types = args[0]
            return self.__get_media(mime_types)
            
        elif (ev == msgs.MEDIASCANNER_SVC_GET_THUMBNAIL):
            f = args[0]
            path = self.__thumbnailer.get_thumbnail_path(f)
            uptodate = self.__thumbnailer.is_thumbnail_up_to_date(f)
            return (path, uptodate)

        elif (ev == msgs.MEDIASCANNER_SVC_SET_THUMBNAIL):
            f, pbuf = args
            thumbpath = self.__thumbnailer.get_thumbnail_path(f)
            pbuf.save(thumbpath, "jpeg")
            print "saving thumbnail for %s as %s" % (f.name, thumbpath)
            return thumbpath


    def __file_exists(self, fp):
    
        f = self.call_service(msgs.CORE_SVC_GET_FILE, fp)
        if (not f):
            return False
        else:
            return len(f.get_children()) > 0
        


    def __scan(self, paths, rebuild_index):
        """
        Scans the media folders recursively.
        """

        self.__scantime = int(time.time())
        self.emit_event(msgs.MEDIASCANNER_EV_SCANNING_STARTED)
        
        self.__file_index.clear_status()
        scanned_roots = self.__file_index.get_roots()

        mediaroots = []
        for path, mtypes in paths:
            f = self.call_service(msgs.CORE_SVC_GET_FILE, path)
            if (f): mediaroots.append((f, mtypes))
        #end for
        
        new_types = {}
        for m, t in mediaroots:
            new_types[m.full_path] = t
        
        # find out which media roots are new
        new_roots = [ m.full_path for m, t in mediaroots
                      if not m.full_path in scanned_roots
                         and self.__file_exists(m.full_path) ]

        # find out which media roots have been removed
        mediapaths = [ m.full_path for m, t in mediaroots ]
        removed_roots = [ m for m in scanned_roots
                          if not m in mediapaths or not self.__file_exists(m) ]

        # find out which media roots haven't changed
        unchanged_roots = [ m for m in scanned_roots
                            if not m in removed_roots]
                          
        logging.debug("new mediaroots:       %s", new_roots)
        logging.debug("removed mediaroots:   %s", removed_roots)
        logging.debug("unchanged mediaroots: %s", unchanged_roots)

        # remove items of removed roots
        for root in removed_roots:
            for fp in self.__file_index.get_files_of_root(root):
                logging.debug("removing from file index [%s]", fp)
                self.__file_index.set_field(FileIndex.STATUS, fp,
                                            FileIndex.STATUS_REMOVED)
            #end for
        #end for
        
        # scan new roots
        if (rebuild_index):
            to_scan = new_roots + unchanged_roots
        else:
            to_scan = new_roots + unchanged_roots

        for mediaroot in to_scan:           
            f = self.call_service(msgs.CORE_SVC_GET_FILE, mediaroot)
            if (not f or not os.path.exists(f.resource)): continue

            mediatypes = new_types.get(mediaroot, 0)

            # skip those with all types unchanged (not for new_roots)
            if (not rebuild_index 
                and mediatypes == self.__mediaroot_types.get(mediaroot, 0)
                and not mediaroot in new_roots):
                continue
            else:
                self.__mediaroot_types[mediaroot] = mediatypes

            self.emit_event(msgs.MEDIASCANNER_EV_SCANNING_PROGRESS,
                            mediaroot)
            logging.info("scanning [%s] for media", mediaroot)

            try:
                self.__process_media(mediaroot, mediatypes, f, {})
            except:
                logging.error(logging.stacktrace())


            # get rid of items in this mediaroot which haven't been found now
            for fp in self.__file_index.get_files_of_root(mediaroot):
                scantime = self.__file_index.get_field(FileIndex.SCANTIME, fp)
                if (scantime < self.__scantime):
                    logging.debug("removing from file index [%s]", fp)
                    self.__file_index.set_field(FileIndex.STATUS, fp,
                                                FileIndex.STATUS_REMOVED)
            #end for


            logging.info("finished scanning [%s]", mediaroot)
        #end for

        self.emit_event(msgs.MEDIASCANNER_EV_SCANNING_FINISHED)
        
        
    def __process_media(self, mediaroot, mediatypes, f, seen):
        """
        Checks the given path for the given mediatypes
        """

        # don't be so stupid to follow circular links
        if (f in seen): return
        seen[f] = True
        
      
        # skip thumbnail folder
        if (f.resource == self.__thumbnailer.get_thumb_folder()):
            return
            
        # process directory recursively
        if (f.mimetype == f.DIRECTORY):
            for child in f.get_children():
                self.__process_media(mediaroot, mediatypes, child, seen)
        #end if
        
        for mediatype, module in [(self.MEDIA_VIDEO, video),
                                  (self.MEDIA_AUDIO, audio),
                                  (self.MEDIA_IMAGE, image)]:

            if (mediatypes & mediatype and module.is_media(f)):
                if (self.__file_index.has_file(f.full_path)):
                    logging.debug("already in file index [%s]", f.full_path)
                    self.__file_index.set_field(FileIndex.STATUS, f.full_path,
                                                FileIndex.STATUS_UNCHANGED)
                else:
                    logging.debug("adding to file index [%s]", f.full_path)
                    self.__file_index.set_field(FileIndex.STATUS, f.full_path,
                                                FileIndex.STATUS_NEW)
                    self.__file_index.set_field(FileIndex.ROOT, f.full_path,
                                                mediaroot)
                    self.__file_index.set_field(FileIndex.MIMETYPE, f.full_path,
                                                f.mimetype)
                
                self.__file_index.set_field(FileIndex.SCANTIME, f.full_path,
                                            self.__scantime)

                break
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
                        on_generated()
                        
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

