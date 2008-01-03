import video
import audio
import image

import md5
import os
import cPickle


class _Item(object):
    def __init__(self):
        self.mediatype = 0
        self.name = ""
        self.uri = ""
        self.thumbnail = ""


class _MediaScanner(object):
    """
    Singleton class for efficient scanning for media.
    """

    MEDIA_VIDEO = 1
    MEDIA_AUDIO = 2
    MEDIA_IMAGE = 4
    

    def __init__(self):
    
        # table: path -> (md5sum, mediatype)
        try:
            self.__media = cPickle.load(open("/tmp/mediabox-mediacache", "r"))
        except:
            self.__media = {}
            
        self.__thumb_folder = "/home/user/.thumbnails/mediabox"        
        self.__media_roots = []
        
        
    def __is_up_to_date(self, uri):
            
        try:
            thumb = self.__thumb_folder + "/" + self.__media[uri][0] + ".jpg"
        except:
            thumb = self.__thumb_folder + "/" + self.__md5sum(uri) + ".jpg"
            
        try:
            mtime1 = os.path.getmtime(uri)
            mtime2 = os.path.getmtime(thumb)

            return (mtime1 <= mtime2)

        except:
            return False


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
        print "searching"
        seen = {}
        for mediaroot, mediatypes in self.__media_roots:
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
                    self.__process_media(mediatypes, uri)
                #end for
            #end for
        #end for
        
        cPickle.dump(self.__media, open("/tmp/mediabox-mediacache", "w"))
        
        
    def __process_media(self, mediatypes, uri):

        for mediatype, module in [(self.MEDIA_VIDEO, video),
                                  (self.MEDIA_AUDIO, audio),
                                  (self.MEDIA_IMAGE, image)]:

            if (mediatypes & mediatype and module.is_media(uri)):
                md5sum = self.__md5sum(uri)
                self.__media[uri] = (md5sum, mediatype)            
                if (not self.__is_up_to_date(uri)):
                    module.make_thumbnail(uri, self.__thumb_folder + "/" + \
                                          md5sum + ".jpg")
                #end if
             #end if
         #end for
        
        
    def get_media(self, mediatypes):
        """
        Returns a list of media items of the given media types.
        """
    
        media = []
        for uri, entry in self.__media.items():
            md5sum, mediatype = entry
            if (mediatypes & mediatype):
                item = _Item()
                item.mediatype = mediatype
                item.name = os.path.basename(uri)
                item.uri = uri
                item.thumbnail = self.__thumb_folder + "/" + md5sum + ".jpg"
                media.append(item)
        #end for
        
        def comp(a, b): return cmp(a.name.lower(), b.name.lower())
        media.sort(comp)
        
        return media


_singleton = _MediaScanner()
def MediaScanner(): return _singleton
