from MediaItem import MediaItem
from utils.Observable import Observable

import video
import audio
import image

import md5
import os
import time
#import cPickle
    

class _MediaScanner(Observable):
    """
    Singleton class for efficient scanning of media.
    """

    OBS_THUMBNAIL_GENERATED = 0

    MEDIA_VIDEO = 1
    MEDIA_AUDIO = 2
    MEDIA_IMAGE = 4
    

    def __init__(self):
    
        # table: path -> (md5sum, mediatype)
        #try:
        #    self.__media = cPickle.load(open("/tmp/mediabox-mediacache", "r"))
        #except:
        
        # time of the last scan
        self.__scantime = 0
        
        # table: path -> item
        self.__media = {}
            
        self.__thumb_folder = "/home/user/.thumbnails/mediabox"        
        self.__media_roots = []
        
        
    def __is_up_to_date(self, uri):
           
        item = self.__media[uri]
        thumb = self.__thumb_folder + "/" + item.md5 + ".jpg"
        broken = thumb + ".broken"
        
        if (os.path.exists(broken)):
            thumburi = broken
        else:
            thumburi = thumb
          
        try:
            mtime1 = os.path.getmtime(uri)
            mtime2 = os.path.getmtime(thumburi)
            item.mtime = mtime1

            return (mtime1 <= mtime2)

        except:        
            return False



    def __mark_as_unavailable(self, thumburi):
        """
        Marks the given thumbnail as unavailable so that we don't try to
        thumbnail it again, unless the mtime has changed.
        """
        
        # simply touch it
        try:
            open(thumburi + ".broken", "w")
        except:
            pass


    def __unmark_as_unavailable(self, thumburi):
        """
        Removes the unavailability mark on the given thumbnail.
        """

        try:
            os.unlink(thumburi + ".broken")
        except:
            pass


    def __md5sum(self, path):
    
        m = md5.new(path)
        return m.hexdigest()
        
        
    def set_thumb_folder(self, path):
        """
        Sets the folder for storing the thumbnails.
        """
    
        self.__thumb_folder = path
        # create directory for thumbnails if it doesn't exist yet
        try:
            if (not os.path.exists(path)):
                os.mkdir(path)
        except:
            pass          


    def set_media_roots(self, media_roots):
        """
        Sets the list of root directories where to look for media.
        """
    
        self.__media_roots = media_roots


    def scan(self):
        """
        Scans the media folders recursively.
        """

        collection = []
        #self.__media = {}
        self.__scantime = int(time.time())
        print "searching"
        seen = {}
        for mediaroot, mediatypes in self.__media_roots:
            try:
                self.__process_media(mediatypes, mediaroot)
            except:
                pass
                
            for dirpath, dirs, files in os.walk(mediaroot):
                # don't be so stupid to follow circular links
                if (seen.get(dirpath)): continue
                seen[dirpath] = True
                            
                # don't allow scanning the thumbnail directory as this may
                # loop endlessly
                if (dirpath == self.__thumb_folder): continue

                for f in dirs + files:
                    # skip hidden files
                    if (f[0] == "."): continue
                    uri = os.path.join(dirpath, f)
                    try:
                        self.__process_media(mediatypes, uri)
                    except:
                        import traceback; traceback.print_exc()
                        pass
                #end for
            #end for
        #end for

        # get rid of items which haven't been found now
        for key, item in self.__media.items():
            if (item.scantime < self.__scantime):
                del self.__media[key]
        #end for

        #cPickle.dump(self.__media, open("/tmp/mediabox-mediacache", "w"))
        
        
    def __process_media(self, mediatypes, uri):

        for mediatype, module in [(self.MEDIA_VIDEO, video),
                                  (self.MEDIA_AUDIO, audio),
                                  (self.MEDIA_IMAGE, image)]:

            if (mediatypes & mediatype and module.is_media(uri)):
                try:
                    item = self.__media[uri]
                except:
                    item = MediaItem()
                    self.__media[uri] = item
                    
                item.scantime = self.__scantime
                item.mediatype = mediatype                
                item.name = os.path.basename(uri)
                item.uri = uri
                item.md5 = self.__md5sum(uri)
                item.thumbnail = self.__thumb_folder + "/" + item.md5 + ".jpg"

                
                if (not self.__is_up_to_date(uri)):
                    item.thumbnail_pmap = None
                    module.make_thumbnail(uri, item.thumbnail)
                    
                    # no thumbnail generated? remember this
                    if (not os.path.exists(item.thumbnail)):
                        self.__mark_as_unavailable(item.thumbnail)
                    else:
                        self.__unmark_as_unavailable(item.thumbnail)
                    
                    self.update_observer(self.OBS_THUMBNAIL_GENERATED,
                                         item.thumbnail, uri)
                #end if
             #end if
         #end for
        
        
    def get_media(self, mediatypes):
        """
        Returns a list of media items of the given media types.
        """
    
        media = [ item for item in self.__media.values()
                  if mediatypes & item.mediatype ]
                  
        #for uri, entry in self.__media.items():
        #    md5sum, mediatype = entry
        #    if (mediatypes & mediatype):
        #        item = _Item()
        #        item.mediatype = mediatype
        #        item.name = os.path.basename(uri)
        #        item.uri = uri
        #        item.thumbnail = self.__thumb_folder + "/" + md5sum + ".jpg"
        #        media.append(item)
        ##end for
        
        def comp(a, b): return cmp(a.uri.lower(), b.uri.lower())
        media.sort(comp)
        
        return media


_singleton = _MediaScanner()
def MediaScanner(): return _singleton

