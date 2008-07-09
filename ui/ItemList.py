from ImageStrip import ImageStrip


class ItemList(ImageStrip):
    """
    This class is a item list view based on the ImageStrip for smooth scrolling.
    """

    def __init__(self, itemsize, gapsize = 32):
    
        self.__height = itemsize
                      
        # TODO: maintaining this list is apparently not necessary anymore...
        #self.__items = []
        
        self.__hilighted_item = -1
                
        ImageStrip.__init__(self, gapsize)
        self.set_wrap_around(False)

        
    def clear_items(self):
        """
        Clears this list.
        """
    
        #self.__items = []
        self.__hilighted_item = -1
        self.set_images([])
        #self.__canvas = None


    def append_item(self, item):
        """
        Appends the given list item.
        """
    
        w, h = self.get_size()
        w -= 20
        item.set_size(w, self.__height)

        #self.__items.append(item)
        idx = self.append_image(item)

        #if (len(self.__items) < 30): self.__canvas.prepare(item)
        
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

        #self.__items[idx] = item
        self.replace_image(idx, item)


    def get_item(self, idx):
        """
        Returns the list item at the given position.
        """
    
        try:
            #return self.__items[idx]
            return self.get_image(idx)
        except:
            return None
               
        
    def remove_item(self, idx):
        """
        Removes the list item at the given position.
        """
    
        #self.__items.pop(idx)
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
        #temp = self.__items[idx1]
        #self.__items[idx1] = self.__items[idx2]
        #self.__items[idx2] = temp
        if (self.__hilighted_item == idx1):
            self.__hilighted_item = idx2
        elif (self.__hilighted_item == idx2):
            self.__hilighted_item = idx1


        
    def hilight(self, idx):
        """
        Sets the given item as hilighted. Only one item is hilighted at a time.
        """

        if (self.__hilighted_item >= 0):
            try:
                item = self.get_image(self.__hilighted_item) #self.__items[self.__hilighted_item]
                item.set_hilighted(False)
            except:
                pass
                
        if (idx >= 0):
            item = self.get_image(idx) #self.__items[idx]
            item.set_hilighted(True)
            self.__hilighted_item = idx
            self.render()

