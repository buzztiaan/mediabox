class Layout(object):

    def __init__(self, *blocks):
    
        self.__blocks = blocks
        
        
    def get_blocks(self):
    
        return self.__blocks
        
        

class Block(object):

    def __init__(self, size, *rows):
    
        self.__rows = rows
        self.__size = size
        
        
    def get_rows(self):
    
        return self.__rows
        
        
    def get_size(self):
    
        return self.__size
        
        
        
class Row(object):

    def __init__(self, *keys):
    
        self.__keys = keys
        
        
    def get_keys(self):
    
        return self.__keys
        
        

class Key(object):

    def __init__(self, char, shifted_char = "", alt_char = ""):
    
        self.__char = unicode(char)
        self.__shifted_char = unicode(shifted_char)
        self.__alt_char = unicode(alt_char)
        
        
    def get_char(self):
    
        return self.__char
        
    
    def get_shifted_char(self):

        return self.__shifted_char


    def get_alt_char(self):
    
        return self.__alt_char


BACKSPACE = Key("BACKSPACE")
SHIFT = Key("SHIFT")
ALT = Key("&!@", "&!@", "abc")
HIDE = Key("HIDE")

