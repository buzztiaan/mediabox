import m3u
from utils import urlquote

import os


class Playlist(object):

    def __init__(self):
    
        self.__current_pos = -1
        self.__name = "playlist"
        self.__path = ""
    
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
              
        
    def get_files(self):
    
        return self.__files[:]


    def prepend(self, f):
    
        self.__files = [f] + self.__files
        self.__is_modified = True
        
        
    def append(self, f):
    
        self.__files.append(f)
        self.__is_modified = True
        
        
    def remove(self, idx):

        del self.__files[idx]
        self.__is_modified = True


    def shift(self, pos, amount):
    
        if (self.__current_pos != -1):
            tmp = self.__files[self.__current_pos]
        
        f = self.__files.pop(pos)
        self.__files.insert(pos + amount, f)

        if (self.__current_pos != -1):
            self.__current_pos = self.__files.index(tmp)
            
        self.__is_modified = True


    def get_position(self):
    
        return self.__current_pos
        
        
    def set_position(self, idx):
    
        self.__current_pos = idx


    def get_size(self):
    
        return len(self.__files)


    def load_from_file(self, path, cb):
        """
        Loads the playlist from the given file.
        """

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


    def delete_playlist(self):
    
        if (self.__path):
            try:
                os.unlink(self.__path)
            except:
                pass
        #end if

        self.__current_pos = -1
        self.__path = ""
        self.__files = []

