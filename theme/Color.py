class Color(object):
    
    def __init__(self, value):
        
        self.__value = value
        
    def set_color(self, value):
    
        self.__value = value
        
        
    def __str__(self):
    
        return self.__value

