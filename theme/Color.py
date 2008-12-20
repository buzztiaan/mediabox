class Color(object):
    
    def __init__(self, value):
        
        self.__value = value
        self.__needs_reload = False

        
    def set_objdef(self, value):
    
        self.__value = value
        self.__needs_reload = True


    def reload(self):
    
        self.__needs_reload = False

        
    def __str__(self):
    
        return self.__value

