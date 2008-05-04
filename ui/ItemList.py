from ImageStrip import ImageStrip
from SharedPixmap import SharedPixmap


class ItemList(ImageStrip):
    """
    This class is a item list view based on the ImageStrip for smooth scrolling.
    """

    def __init__(self, esens, itemsize):
    
        self.__canvas = None
        self.__height = itemsize
                      
        self.__items = []        
        self.__hilighted_item = -1
                
        ImageStrip.__init__(self, esens, 20)
        self.set_wrap_around(False)
       
        
    def clear_items(self):
    
        self.__items = []
        self.__hilighted_item = -1
        self.set_images([])
        self.__canvas = None


    def append_item(self, item):
    
        w, h = self.get_size()
        w -= 20
        if (not self.__canvas):
            self.__canvas = SharedPixmap(w, self.__height)

        canvas = self.__canvas
        item.set_canvas(canvas)
        canvas.set_renderer(item, lambda x:item.render())
        self.__items.append(item)
        idx = self.append_image(item)
        
        if (len(self.__items) < 30): self.__canvas.prepare(item)
        
        return idx


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
        elif (idx < self.__hilighted_item):
            self.__hilighted_item -= 1


    def swap(self, idx1, idx2):
   
        ImageStrip.swap(self, idx1, idx2)
        temp = self.__items[idx1]
        self.__items[idx1] = self.__items[idx2]
        self.__items[idx2] = temp
        if (self.__hilighted_item == idx1):
            self.__hilighted_item = idx2
        elif (self.__hilighted_item == idx2):
            self.__hilighted_item = idx1


        
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
            #self.render()
            #self.scroll_to_item(idx)

