from Pixmap import Pixmap, TEMPORARY_PIXMAP
import theme

import gtk
import gobject
import pango



class Item(object):

    def __init__(self):

        self.__normal_bg = None
        self.__hilighted_bg = None
        self.__is_hilighted = False
        
        self.__canvas = None
      
        
    def set_canvas(self, canvas):
    
        self.__canvas = canvas


    def set_graphics(self, normal, hilighted):
    
        self.__normal_bg = normal
        self.__hilighted_bg = hilighted


    def get_size(self):
    
        return self.__canvas.get_size()


    def set_hilighted(self, value):
    
        if (value != self.__is_hilighted):
            self.__is_hilighted = value
            self.render()
            
           
    def is_hilighted(self):
    
        return self.__is_hilighted
        
        
    def render(self):

        if (not self.__canvas): return
        
        self.__canvas.invalidate_cache(self)
        w, h = self.__canvas.get_size()    
        self.__canvas.fill_area(0, 0, w, h, "#ffffff")        

        background = self.__is_hilighted and self.__hilighted_bg \
                                          or self.__normal_bg

        if (background):
            self.__canvas.draw_frame(background, 0, 0, w, h, True)
        
        self.render_this(self.__canvas)
        
        
    def render_this(self, canvas):
    
        pass


    def get_pixmap(self):
    
        self.__canvas.prepare(self)
        return self.__canvas
        
