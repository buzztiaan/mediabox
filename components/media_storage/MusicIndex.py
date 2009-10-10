from mediabox import tagreader
from mediabox import values
from utils import logging

import os


_INDEX_FILE = os.path.join(values.USER_DIR, "audio.idx")

# when the index format becomes incompatible, raise the magic number to force
# rejection of old index
_MAGIC = 0xbeef0004


_FOLDER_PATH = 0
_FILE_PATH = 1
_TITLE = 2
_ARTIST = 3
_ALBUM = 4
_GENRE = 5


class _MusicIndex(object):
    """
    Class for a audio metadata index, because a SQL database would be overkill
    and calls for trouble.
    """

    def __init__(self):
    
        self.__index = []
               
        # function scheduled for scanning
        self.__scheduled_scanner = None

        self.__load_index()
        



    def __add_to_index(self, folderpath, filepath, title, artist, album, genre):

        key = (folderpath, filepath, title, artist, album, genre)
        if (not key in self.__index):
            self.__index.append(key)
            
            
    def __delete_from_index(self, folderpath):
    
        new_index = []
        for item in self.__index:
            if (item[0] != folderpath):
                new_index.append(item)
        #end for
        
        self.__index = new_index


    def __list_index(self, selector, column):
    
        out = []
        for item in self.__index:
            value = item[column]
            if (selector):
                if (selector(item) and not value in out):
                    out.append(value)
            else:
                if (not value in out):
                    out.append(value)
            #end if
        #end for
        out.sort()
        
        return out

        
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
            cPickle.dump((_MAGIC, self.__index),
                         fd, 2)
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
        artists = self.__list_index(None, _ARTIST)
        return artists


    def list_albums(self):
    
        self.__check_scanner()
        albums = self.__list_index(None, _ALBUM)
        return albums


    def list_genres(self):
    
        self.__check_scanner()
        genres = self.__list_index(None, _GENRE)
        return genres


    def list_albums_by_artist(self, artist):

        self.__check_scanner()
        selector = lambda item: item[_ARTIST] == artist
        albums = self.__list_index(selector, _ALBUM)
        return albums


    def list_albums_by_genre(self, genre):

        self.__check_scanner()
        selector = lambda item: item[_GENRE] == genre
        albums = self.__list_index(selector, _ALBUM)
        return albums


    def list_files(self, album):

        self.__check_scanner()
        selector = lambda item: item[_ALBUM] == album
        tracks = self.__list_index(selector, _FILE_PATH)
        return tracks


    def clear(self):
        
        self.__index = []
        

    def add_album(self, folder):

        for f in folder.get_children():
            if (not f.mimetype.startswith("audio/")): continue

            tags = tagreader.get_tags(f)
            title = (tags.get("TITLE") or f.name).encode("utf-8")
            artist = (tags.get("ARTIST") or "unknown").encode("utf-8")
            album = (tags.get("ALBUM") or "").encode("utf-8")
            try:
                genre = (tags.get("GENRE") or "unknown").encode("utf-8")
            except:
                genre = "unknown"
            if (not album):
                album = os.path.basename(folder.full_path)

            self.__add_to_index(folder.full_path,
                                f.full_path,
                                title,
                                artist,
                                album,
                                genre)
        #end for            
      
        
    def remove_album(self, folder):
    
        self.__delete_from_index(folder.full_path)
       
       
    def add_file(self, f):

        tags = tagreader.get_tags(f)
        title = (tags.get("TITLE") or f.name).encode("utf-8")
        artist = (tags.get("ARTIST") or "unknown").encode("utf-8")
        album = (tags.get("ALBUM") or "").encode("utf-8")
        try:
            genre = (tags.get("GENRE") or "unknown").encode("utf-8")
        except:
            genre = "unknown"
        if (not album):
            parent = os.path.dirname(f.full_path)
            album = os.path.basename(parent)
        else:
            parent = ""

        self.__add_to_index(parent,
                            f.full_path,
                            title,
                            artist,
                            album,
                            genre)

        
        
    def remove_file(self, f):
    
        new_index = []
        for item in self.__index:
            if (item[_FILE_PATH] != f.full_path):
                new_index.append(item)
        #end for

        self.__index = new_index

        
_singleton = _MusicIndex()
def MusicIndex(): return _singleton

