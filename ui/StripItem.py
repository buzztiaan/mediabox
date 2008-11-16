from Pixmap import Pixmap


class StripItem(object):
    """
    Base class for items for the ImageStrip.
    """

    # table for sharing the same prerendered background pixmap among instances
    __bg_store = {}
    

    def __init__(self):
    
        self.__width = 0
        self.__height = 0
        self.__canvas = None
        self.__is_hilighted = False
        self.__selection_frame = None

        self.__background = None


    def set_size(self, w, h):
    
        self.__width = w
        self.__height = h
        
        if (self.__canvas in self.__bg_store):
            del self.__bg_store[(self.__class__, self.__canvas)]
        if (self.__background):
            self.set_background(self.__background)


    def get_size(self):
    
        return (self.__width, self.__height)


    def set_background(self, bg):
    
        self.__background = bg
    
        if (not self.__canvas): return
        
        # prerender the background pixmap in order to have it ready on the
        # server-side
        if (not (self.__class__, self.__canvas) in self.__bg_store):
            w, h = self.get_size()
            pmap = Pixmap(None, w, h)
            self.__bg_store[(self.__class__, self.__canvas)] = pmap
            
            pmap.draw_frame(bg, 0, 0, w, h, True)
        #end if
            

    def set_canvas(self, canvas):
    
        self.__canvas = canvas
        self.__canvas.set_renderer(self, self.render)
        if (self.__background):
            self.set_background(self.__background)



    def set_selection_frame(self, pbuf):
    
        self.__selection_frame = pbuf
        
        
    def invalidate(self):
    
        if (self.__canvas):
            self.__canvas.invalidate_cache(self)
        

    def render(self):
    
        if (self.__canvas):
            self.__canvas.invalidate_cache(self)
            self.render_this(self.__canvas)
        
        
    def render_bg(self, canvas):

        pmap = self.__bg_store.get((self.__class__, self.__canvas))
        if (pmap):    
            canvas.draw_pixmap(pmap, 0, 0)
        
        
    def render_selection_frame(self, canvas):
    
        if (self.__is_hilighted and self.__selection_frame):
            canvas.draw_frame(self.__selection_frame, 0, 0,
                              self.__width, self.__height, True)


    def render_this(self, canvas):
    
        raise NotImplementedError
        
        
    def is_hilighted(self):
    
        return self.__is_hilighted
        
        
    def set_hilighted(self, value):
    
        if (value != self.__is_hilighted):
            self.__is_hilighted = value
            self.invalidate()

