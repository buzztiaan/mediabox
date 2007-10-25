from ImageStrip import ImageStrip
from Item import Item
import gtk


class ItemList(ImageStrip):

    def __init__(self, width, itemsize):
    
        self.__width = width
        self.__height = itemsize
        ImageStrip.__init__(self, width, itemsize, 10)
        
        
    def clear_items(self):
    
        self.set_images([])
        
        
    def append_item(self, label, icon = None, background = None):
    
        item = Item(self, self.__width, self.__height, icon, label, background)
        return self.append_image(item)
        
        
    def remove_item(self, idx):
    
        self.remove_image(idx)
