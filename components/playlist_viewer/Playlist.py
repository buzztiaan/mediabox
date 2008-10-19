import m3u
from utils import urlquote

import os


class Playlist(object):

    def __init__(self):
    
        self.__current_pos = -1
        self.__name = "playlist"
        self.__path = ""
    
        self.__items = []
        self.__thumbnails = []
        self.__files = []
    
        self.__is_modified = False
        
        
    def has_previous(self):
    
        return (self.__current_pos > 0)
        
        
    def has_next(self):
    
        return (self.__current_pos < self.get_size() - 1)

        
    def get_name(self):
    
        return self.__name
        
        
    def set_name(self, name):
    
        self.__name = name
        # TODO: remove file of previous name
        self.__is_modified = True
        
        
    def get_items(self):
    
        return self.__items[:]
        
        
    def get_thumbnails(self):
    
        return self.__thumbnails[:]
        
        
    def get_files(self):
    
        return self.__files[:]
        
        
    def append(self, item, tn, f):
    
        self.__items.append(item)
        self.__thumbnails.append(tn)
        self.__files.append(f)
        self.__is_modified = True
        
        
    def remove(self, idx):
    
        del self.__items[idx]
        del self.__thumbnails[idx]
        del self.__files[idx]
        self.__is_modified = True


    def swap(self, idx1, idx2):
    
        temp = self.__items[idx1]
        self.__items[idx1] = self.__items[idx2]
        self.__items[idx2] = temp

        temp = self.__thumbnails[idx1]
        self.__thumbnails[idx1] = self.__thumbnails[idx2]
        self.__thumbnails[idx2] = temp

        temp = self.__files[idx1]
        self.__files[idx1] = self.__files[idx2]
        self.__files[idx2] = temp

        if (self.__current_pos == idx1):
            self.__current_pos = idx2
        elif (self.__current_pos == idx2):
            self.__current_pos = idx1


    def get_position(self):
    
        return self.__current_pos
        
        
    def set_position(self, idx):
    
        self.__current_pos = idx


    def get_size(self):
    
        return len(self.__items)


    def load_from_file(self, path, cb):
        """
        Loads the playlist from the given file.
        """

        self.__items = []
        self.__thumbnails = []
        self.__files = []

        for location, name in m3u.load(path):
            cb(self, name, location)

        self.__path = path
        self.__is_modified = False    

        self.__name = urlquote.unquote(
                                 os.path.splitext(os.path.basename(path))[0])
        
        
    def save_as(self, path):
        """
        Saves the playlist to the given file.
        """
    
        if (not self.__is_modified): return
        
        items = [ (f.full_path, f.name) for f in self.__files ]
        m3u.save(path, items)
        
        self.__path = path
        self.__is_modified = False



    def save(self):
    
        if (self.__path):
            self.save_as(self.__path)

