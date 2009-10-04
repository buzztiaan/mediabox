from com import Component, msgs
from FileIndex import FileIndex
from Thumbnailer import Thumbnailer
from mediabox import config
from utils import logging

# these modules handle the particular media types
import video
import audio
import image

import os
import time


class MediaScanner(Component):
    """
    Component for scanning the filesystem for media files.
    
    How scanning works:
    
    The user specifies several media root directories which subtrees contain
    media files.
    
    First, we check for new media roots and for media roots that have been gone,
    either by removing from the filesystem, or by removing the media root from
    the list of media roots. All files that are registered under such a media
    root have to be removed from the index.
    
    Next, we look for new media roots. The new roots and the unchanged roots
    get scanned recursively for media files.
    
    If we discover a media file during scanning, it can be
    
     * not indexed yet, so we add it as new
     
     * already indexed, but the mtime changed, so we add it as new/updated
     
     * already indexed and up to date, so we just mark it as unchanged
     
    The indexed media files that have not been found by scanning get removed
    from the index, afterwards, because they are no longer there.
    
    Storage devices query for three sets of files containing their media types:
    
     * the files that have not changed
     
     * the files that are new
     
     * the files that have been removed
    """  

    def __init__(self):

        # time of the last scan
        self.__scantime = 0
               
        # index for files that is serialized to disk
        self.__file_index = FileIndex()
        
        # table: root path -> types
        self.__mediaroot_types = {}
        
        self.__thumbnailer = Thumbnailer()
        
    
        Component.__init__(self)
        
        
        for mediaroot, types in config.mediaroot():
            self.__mediaroot_types[mediaroot] = types
        
        
        
    def handle_MEDIASCANNER_ACT_SCAN(self, mediaroots, rebuild_index):
    
        self.__scan_roots(mediaroots, rebuild_index)


    def handle_MEDIASCANNER_SVC_GET_MEDIA(self, mime_types):

        return self.__get_media(mime_types)


    """
    def handle_MEDIASCANNER_SVC_GET_THUMBNAIL(self, f):

        logging.warning("MEDIASCANNER_SVC_GET_THUMBNAIL is deprecated")
        path = self.__thumbnailer.get_thumbnail_path(f)
        uptodate = self.__thumbnailer.is_thumbnail_up_to_date(f)
        return (path, uptodate)


    def handle_MEDIASCANNER_SVC_SET_THUMBNAIL(self, f, pbuf):

        logging.warning("MEDIASCANNER_SVC_SET_THUMBNAIL is deprecated")
        thumbpath = self.__thumbnailer.get_thumbnail_path(f)
        pbuf.save(thumbpath, "jpeg")
        print "saving thumbnail for %s as %s" % (f.name, thumbpath)
        return thumbpath
    """


    def __file_exists(self, fp):
    
        f = self.call_service(msgs.CORE_SVC_GET_FILE, fp)
        if (not f):
            return False
        else:
            return len(f.get_children()) > 0
        
        
        
    def __find_new_roots(self, roots, mediatypes):
        """
        Returns the media roots that are new or have changed media types.
        """
        
        scanned_roots = self.__file_index.get_roots()
        
        new_roots = []
        for root in roots:
            if (not self.__file_exists(root)):
                #print "doesn't exist:", root
                continue
            
            if (not root in scanned_roots):
                #print "is new:", root
                new_roots.append(root)
            elif (mediatypes[root] != self.__mediaroot_types.get(root, 0)
                  and mediatypes[root] != 0):
                #print "type changed:", root
                new_roots.append(root)
        #end for

        return new_roots
        
        
    def __find_removed_roots(self, roots):
        """
        Returns the media roots that have been removed.
        """
    
        scanned_roots = self.__file_index.get_roots()
        
        removed_roots = [ root for root in scanned_roots
                          if not root in roots
                             or not self.__file_exists(root) ]
        
        return removed_roots
        
        
    def __scan_roots(self, mediaroots, rebuild_index):
        """
        Scans the given roots.
        """

        self.__scantime = int(time.time())

        mediatypes = {}
        roots = []
        for path, mtypes in mediaroots:
            mediatypes[path] = mtypes
            roots.append(path)
        #end for
        print "MEDIAROOTS:", roots

        new_roots = self.__find_new_roots(roots, mediatypes)
        removed_roots = self.__find_removed_roots(roots)
        self.__mediaroot_types.update(mediatypes)
        
        #print "NEW:", new_roots
        #print "REMOVED:", removed_roots
        
        if (rebuild_index):
            # scan all when rebuilding index
            to_scan = [ root for root in roots if not root in removed_roots ]
        else:
            # only scan new roots otherwise
            to_scan = [ root for root in new_roots if not root in removed_roots ]
        logging.debug("media roots to scan:\n%s", to_scan)

        self.__file_index.clear_status()

        # don't do anything if there's nothing to scan or remove
        if (not to_scan and not removed_roots):
            self.emit_message(msgs.MEDIASCANNER_EV_SCANNING_FINISHED)
            return
        
        self.emit_message(msgs.MEDIASCANNER_EV_SCANNING_STARTED)

        # remove from index
        for root in removed_roots:
            # remove all files belonging to that root from index
            for fp in self.__file_index.get_files_of_root(root):
                logging.debug("removing from file index [%s]", fp)
                self.__file_index.set_field(FileIndex.STATUS, fp,
                                            FileIndex.STATUS_REMOVED)
            #end for
        #end for

        # scan present roots
        for root in to_scan:
            f = self.call_service(msgs.CORE_SVC_GET_FILE, root)
            if (not f or not os.path.exists(f.resource)): continue
        
            self.emit_message(msgs.MEDIASCANNER_EV_SCANNING_PROGRESS,
                            root)
            logging.info("scanning [%s] for media", root)

            try:
                self.__process_media(root, mediatypes.get(root, 0), f, {})
            except:
                logging.error(logging.stacktrace())


            # get rid of items in this mediaroot which haven't been found now
            for fp in self.__file_index.get_files_of_root(root):
                scantime = self.__file_index.get_field(FileIndex.SCANTIME, fp)
                if (scantime < self.__scantime):
                    logging.debug("removing from file index [%s]", fp)
                    self.__file_index.set_field(FileIndex.STATUS, fp,
                                                FileIndex.STATUS_REMOVED)
            #end for

            logging.info("finished scanning [%s]", root)
        #end for            
        
        self.emit_message(msgs.MEDIASCANNER_EV_SCANNING_FINISHED)
  
        
    def __process_media(self, mediaroot, mediatypes, f, seen):
        """
        Checks the given path for the given mediatypes
        """

        # don't be so stupid to follow circular links
        if (f in seen): return
        seen[f] = True
        
      
        # skip thumbnail folder
        #if (f.resource == self.__thumbnailer.get_thumb_folder()):
        #    return
            
        # process directory recursively
        if (f.mimetype == f.DIRECTORY):
            for child in f.get_children():
                self.__process_media(mediaroot, mediatypes, child, seen)
        #end if
        
        for mediatype, module in [(config.MEDIA_VIDEO, video),
                                  (config.MEDIA_AUDIO, audio),
                                  (config.MEDIA_IMAGE, image)]:

            if (mediatypes & mediatype and module.is_media(f)):
                if (self.__file_index.has_file(f.full_path)):
                    scantime = self.__file_index.get_field(FileIndex.SCANTIME,
                                                           f.full_path)
                    if (os.path.exists(f.resource)):
                        mtime = os.path.getmtime(f.resource)
                    else:
                        mtime = 0
                                      
                    if (mtime > scantime):
                        logging.debug("updating in file index [%s]", f.full_path)
                        self.__file_index.set_field(FileIndex.STATUS, f.full_path,
                                                    FileIndex.STATUS_NEW)
                    else:
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
        # TODO: remove from here eventually

        def on_generated():
            # no thumbnail generated? remember this
            if (not self.__thumbnailer.has_thumbnail(f)):
                self.__thumbnailer.mark_as_unavailable(f)
            else:
                self.__thumbnailer.unmark_as_unavailable(f)
            
            cb(self.__thumbnailer.get_thumbnail_path(f), *args)
            
        handled = False
        for mediatype, module in [(config.MEDIA_VIDEO, video),
                                  (config.MEDIA_AUDIO, audio),
                                  (config.MEDIA_IMAGE, image)]:

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

