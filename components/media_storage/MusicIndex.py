from mediabox import tagreader
from mediabox import values
from utils import logging

import os


_INDEX_FILE = os.path.join(values.USER_DIR, "audio.idx")

# when the index format becomes incompatible, raise the magic number to force
# rejection of old index
_MAGIC = 0xbeef0002


class _MusicIndex(object):
    """
    Class for a audio metadata index, because a SQL database would be overkill
    and calls for trouble.
    """

    def __init__(self):

        # list of tuples (artist, album, folderfullpath)
        self.__index = []
        
        # function scheduled for scanning
        self.__scheduled_scanner = None

        self.__load_index()
        
        
    def __save_index(self):
        """
        Persists the index to file.
        """
    
        try:
            import cPickle
            fd = open(_INDEX_FILE, "wb")
        except:
            return
            
        try:
            cPickle.dump((_MAGIC, self.__index), fd, 2)
        except:
            pass
        finally:
            fd.close()
            
            

    def __load_index(self):
        """
        Restores the index from file.
        """
    
        try:
            import cPickle
            fd = open(_INDEX_FILE, "rb")
        except:
            return
            
        try:
            magic, data = cPickle.load(fd)
        except:
            logging.error(logging.stacktrace())
            return
        finally:
            fd.close()

        # ignore the file if it isn't compatible
        if (magic == _MAGIC):
            self.__index = data


    def __check_scanner(self):
    
        if (self.__scheduled_scanner):
            try:
                self.__scheduled_scanner()
            except:
                logging.error(logging.stacktrace())
            self.__scheduled_scanner = None
            self.__save_index()
        #end if


    def schedule_scanner(self, scanner):
    
        self.__scheduled_scanner = scanner


    def save(self):
        
        self.__save_index()
        
  
    def list_artists(self):
    
        self.__check_scanner()
        artists = []
        for ar, al, fp in self.__index:
            if (not ar in artists):
                artists.append(ar)
        #end for
        
        return artists


    def list_albums(self, artist):

        self.__check_scanner()    
        albums = []
        for ar, al, fp in self.__index:
            if (ar == artist and not (al, fp) in albums):
                albums.append((al, fp))
        #end for
        
        return albums


    def get_album(self, artist, album):

        self.__check_scanner()
        for ar, al, fp in self.__index:
            if ((ar, al) == (artist, album)):
                return fp
        #end for

        return None
        

    def add_album(self, folder):
    
        album_fp = folder.full_path

        for f in folder.get_children():
            if (not f.mimetype.startswith("audio/")): continue
            
            tags = tagreader.get_tags(f)
            artist = (tags.get("ARTIST") or "unknown").encode("utf-8")
            album = (tags.get("ALBUM") or "").encode("utf-8")
            if (not album):
                album = os.path.basename(album_fp)

            # TODO: albums sharing the same name cause problems
            artist = artist.replace("/", "|")
            album = album.replace("/", "|")

            key = (artist, album, album_fp)
            if (not key in self.__index):
                self.__index.append(key)
        #end for
      
        
    def remove_album(self, folder):
    
        album_fp = folder.full_path
        
        new_index = []
        for artist, album, fp in self.__index:
            if (fp != album_fp):
                new_index.append((artist, album, fp))
        #end for
        self.__index = new_index

        


        
_singleton = _MusicIndex()
def MusicIndex(): return _singleton

