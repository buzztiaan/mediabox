from Pixmap import Pixmap
import pixbuftools


class StripItem(object):
    """
    Base class for items for the ImageStrip.
    """

    # table for sharing the same prerendered background pixmap among instances
    __bg_store = {}
    
    # table for sharing the same prerendered selection frame pixbuf among instances
    __sel_store = {}
    

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
        
        #if (self.__canvas in self.__bg_store):
        #    del self.__bg_store[(self.__class__, self.__canvas)]
        #    del self.__sel_store[(self.__class__, self.__canvas)]


    def get_size(self):
    
        return (self.__width, self.__height)


    def set_background(self, bg):
    
        self.__background = bg
            

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
        self.__bg_store.clear()
        self.__sel_store.clear()
        

    def render(self):
    
        if (self.__canvas):
            self.__canvas.invalidate_cache(self)
            self.render_this(self.__canvas)
        
        
    def render_bg(self, canvas):

        if (not self.__background): return

        pmap = self.__bg_store.get((self.__class__, self.__canvas))
        if (not pmap or self.__width != pmap.get_size()[0]):
            # prerender the background pixmap in order to have it ready on the
            # server-side
            w, h = self.get_size()
            pmap = Pixmap(None, w, h)
            self.__bg_store[(self.__class__, self.__canvas)] = pmap
            pmap.draw_frame(self.__background, 0, 0, w, h, True)
        #end if

        canvas.draw_pixmap(pmap, 0, 0)
        
        
    def render_selection_frame(self, canvas):
    
        if (self.__is_hilighted and self.__selection_frame):
            pbuf = self.__sel_store.get((self.__class__, self.__canvas))
            if (not pbuf or self.__width != pbuf.get_width()):
                # prerender the pixbuf in order to have it ready on the
                # server-side
                w, h = self.get_size()
                pbuf = pixbuftools.make_frame(self.__selection_frame,
                                              w, h, True)
                self.__sel_store[(self.__class__, self.__canvas)] = pbuf
            #end if

            canvas.draw_pixbuf(pbuf, 0, 0)
            #canvas.draw_frame(self.__selection_frame, 0, 0,
            #                  self.__width, self.__height, True)


    def render_this(self, canvas):
    
        raise NotImplementedError
        
        
    def is_hilighted(self):
    
        return self.__is_hilighted
        
        
    def set_hilighted(self, value):
    
        if (value != self.__is_hilighted):
            self.__is_hilighted = value
            self.invalidate()

