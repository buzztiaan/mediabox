from Pixmap import Pixmap
import theme

import gtk
import gobject
import pango


class Item(gtk.gdk.Pixbuf):
    """
    Class for rendering a list item.
    """

    __defer_list = []   # this is a static variable shared by all instances


    def __init__(self, width, height):

        self.__normal_bg = None
        self.__hilighted_bg = None
        self.__is_hilighted = False
        
        self.__width = width
        self.__height = height
        
        self.__canvas = Pixmap(None, width, height)
        
        self.__initialized = False
    
        gtk.gdk.Pixbuf.__init__(self, gtk.gdk.COLORSPACE_RGB, False, 8,
                                width, height)

        #if (not self.__defer_list):
        #    gobject.idle_add(self.__defer_handler)            
        #self.__defer_list.append(self)
        
        
    def __defer_handler(self):
    
        i = self.__defer_list.pop(0)
        i.get_width()
        if (self.__defer_list):
            return True
        else:
            return False


    def set_graphics(self, normal, hilighted):
    
        self.__normal_bg = normal
        self.__hilighted_bg = hilighted



    def set_hilighted(self, value):
    
        if (value != self.__is_hilighted):
            self.__is_hilighted = value
            self._render_item()
            
            
    def is_hilighted(self):
    
        return self.__is_hilighted


    def get_width(self):
    
        if (not self.__initialized): self.__initialize()
        return gtk.gdk.Pixbuf.get_width(self)


    def subpixbuf(self, *args):
    
        if (not self.__initialized): self.__initialize()
        return gtk.gdk.Pixbuf.subpixbuf(self, *args)


    def _render_item(self):

        self._render(self.__canvas)
        self.__canvas.render_on_pixbuf(self)
        
        
    def _render(self, canvas):
        
        canvas.fill_area(0, 0, self.__width, self.__height, "#ffffff")        

        background = self.__is_hilighted and self.__hilighted_bg \
                                          or self.__normal_bg

        if (background):
            self.__canvas.draw_subpixbuf(background, 0, 0, 0, 0,
                                         self.__width, self.__height)



    def __initialize(self):
    
        self.__initialized = True
        self._render_item()

