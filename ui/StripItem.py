class StripItem(object):
    """
    Base class for items for the ImageStrip.
    """

    def __init__(self):
    
        self.__width = 0
        self.__height = 0
        self.__canvas = None
        self.__is_hilighted = False


    def set_size(self, w, h):
    
        self.__width = w
        self.__height = h


    def get_size(self):
    
        return (self.__width, self.__height)
                
        
    def set_canvas(self, canvas):
    
        self.__canvas = canvas
        self.__canvas.set_renderer(self, self.render)
        
        
    def invalidate(self):
    
        if (self.__canvas):
            self.__canvas.invalidate_cache(self)
        

    def render(self):
    
        if (self.__canvas):
            self.__canvas.invalidate_cache(self)
            self.render_this(self.__canvas)


    def render_this(self, canvas):
    
        raise NotImplementedError
        
        
    def is_hilighted(self):
    
        return self.__is_hilighted
        
        
    def set_hilighted(self, value):
    
        if (value != self.__is_hilighted):
            self.__is_hilighted = value
            self.render()

