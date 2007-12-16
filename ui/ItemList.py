from ImageStrip import ImageStrip
from Item import Item

import gtk
import pango


_NORMAL = 0
_HILIGHTED = 1


class ItemList(ImageStrip):

    def __init__(self, width, itemsize):
    
        self.__width = width
        self.__height = itemsize
        
        self.__normal_bg = None
        self.__hilighted_bg = None
        
        self.__font = pango.FontDescription("Sans 8")
        
        self.__items = []        
        self.__hilighted_item = -1
                
        ImageStrip.__init__(self, width, itemsize, 10)
        self.set_wrap_around(False)
        #self.set_show_slider(True)
        
    
    def set_graphics(self, normal, hilighted):
    
        self.__normal_bg = normal
        self.__hilighted_bg = hilighted
    
    
    def set_font(self, font):
    
        self.__font = font    
        
        
    def clear_items(self):
    
        self.__items = []
        self.__hilighted_item = -1
        self.set_images([])
        
        
    def append_item(self, label, icon = None):
    
        normal_item    = Item(self, self.__width, self.__height, icon, label,
                              self.__font, self.__normal_bg)
        hilighted_item = Item(self, self.__width, self.__height, icon, label,
                              self.__font, self.__hilighted_bg)

        self.__items.append((normal_item, hilighted_item))
        return self.append_image(normal_item)
        
        
    def remove_item(self, idx):
    
        self.__items.pop(idx)
        self.remove_image(idx)

        if (idx == self.__hilighted_item):
            self.__hilighted_item = -1
        
        
    def hilight(self, idx):

        if (self.__hilighted_item >= 0):
            try:
                self.replace_image(self.__hilighted_item,
                                   self.__items[self.__hilighted_item][_NORMAL])
            except:
                pass
        if (idx >= 0):                                 
            self.replace_image(idx, self.__items[idx][_HILIGHTED])
            self.__hilighted_item = idx
            
            self.scroll_to_item(idx)

