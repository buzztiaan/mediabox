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
    
        self.__layout = None
        self.__char = unicode(char, "utf-8")
        self.__shifted_char = unicode(shifted_char, "utf-8")
        self.__alt_char = unicode(alt_char, "utf-8")


    def set_layout(self, layout):
    
        self.__layout = layout
        
        
    def get_layout(self):
    
        return self.__layout
        
       
    def get_char(self):
    
        return self.__char
        
    
    def get_shifted_char(self):

        return self.__shifted_char


    def get_alt_char(self):
    
        return self.__alt_char


LAYOUT = Key("LAYOUT")
BACKSPACE = Key("BACKSPACE")
SHIFT = Key("SHIFT")
ALT = Key("123", "123", "abc")
HIDE = Key("HIDE")

