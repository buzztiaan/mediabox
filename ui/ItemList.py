"""
A basic list derived from L{ImageStrip}.
"""


from ImageStrip import ImageStrip
import theme


class ItemList(ImageStrip):
    """
    This class is a item list view based on the ImageStrip for smooth scrolling.
    """

    def __init__(self, itemsize, gapsize = 32):
    
        self.__height = itemsize
        self.__hilighted_item = -1
                
        ImageStrip.__init__(self, gapsize)
        self.set_wrap_around(False)
        self.set_scrollbar(theme.mb_list_scrollbar)


    def set_size(self, w, h):
    
        for item in self.get_items():
            item.set_size(w - 10, self.__height)
            
        ImageStrip.set_size(self, w, h)

        
    def clear_items(self):
        """
        Clears this list.
        """
    
        self.__hilighted_item = -1
        self.set_images([])


    def append_item(self, item):
        """
        Appends the given list item.
        """
    
        w, h = self.get_size()
        w -= 20
        item.set_size(w, self.__height)

        idx = self.append_image(item)
        
        return idx
        
        
    def replace_item(self, idx, item):
        """
        Replaces the item at the given position with the given item.
        """

        w, h = self.get_size()
        w -= 20
        item.set_size(w, self.__height)
        
        if (self.__hilighted_item == idx):
            item.set_hilighted(True)

        self.replace_image(idx, item)


    def get_items(self):
        """
        Returns the list of the items.
        """
        
        return self.get_images()


    def get_item(self, idx):
        """
        Returns the list item at the given position.
        """
    
        try:
            return self.get_image(idx)
        except:
            return None
               
        
    def remove_item(self, idx):
        """
        Removes the list item at the given position.
        """
    
        self.remove_image(idx)

        if (idx == self.__hilighted_item):
            self.__hilighted_item = -1
        elif (idx < self.__hilighted_item):
            self.__hilighted_item -= 1


    def swap(self, idx1, idx2):
        """
        Swaps the items at the given positions in the list.
        """
   
        ImageStrip.swap(self, idx1, idx2)

        if (self.__hilighted_item == idx1):
            self.__hilighted_item = idx2
        elif (self.__hilighted_item == idx2):
            self.__hilighted_item = idx1


        
    def hilight(self, idx):
        """
        Sets the given item as hilighted. Only one item is hilighted at a time.
        """

        self.invalidate_buffer()
        if (self.__hilighted_item >= 0):
            try:
                item = self.get_image(self.__hilighted_item)
                item.set_hilighted(False)
            except:
                pass
                
        if (idx >= 0):
            item = self.get_image(idx)
            item.set_hilighted(True)
            self.__hilighted_item = idx
            self.render()

