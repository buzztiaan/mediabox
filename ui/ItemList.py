from ImageStrip import ImageStrip
from Item import Item

import pango


_NORMAL = 0
_HILIGHTED = 1


class ItemList(ImageStrip):
    """
    This class is a item list view based on the ImageStrip for smooth scrolling.
    """

    def __init__(self, esens, width, itemsize):
    
        self.__width = width
        self.__height = itemsize
        
        self.__normal_bg = None
        self.__hilighted_bg = None
               
        self.__items = []        
        self.__hilighted_item = -1
                
        ImageStrip.__init__(self, esens, width, itemsize, 10)
        self.set_wrap_around(False)
        #self.set_show_slider(True)
        
    
    def set_graphics(self, normal, hilighted):
    
        self.__normal_bg = normal
        self.__hilighted_bg = hilighted
        
        
    def clear_items(self):
    
        self.__items = []
        self.__hilighted_item = -1
        self.set_images([])


    def append_custom_item(self, item):

        self.__items.append(item)        
        return self.append_image(item)
        
        
    def get_item(self, idx):
    
        return self.__items[idx]
               
        
    def remove_item(self, idx):
    
        self.__items.pop(idx)
        self.remove_image(idx)

        if (idx == self.__hilighted_item):
            self.__hilighted_item = -1
        
        
    def hilight(self, idx):

        #print "HILIGHT", idx
        if (self.__hilighted_item >= 0):
            try:
                item = self.__items[self.__hilighted_item]
                item.set_hilighted(False)
            except:
                pass
                
        if (idx >= 0):
            item = self.__items[idx]
            item.set_hilighted(True)
            self.__hilighted_item = idx            
            self.scroll_to_item(idx)

        self.render()
