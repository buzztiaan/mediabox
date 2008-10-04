from ImageButton import ImageButton


class SequenceButton(ImageButton):

    EVENT_CHANGED = "event-changed"
    

    def __init__(self, sequence):
        
        self.__sequence = sequence
        self.__index = 0
        
        img = sequence[0][0]
        ImageButton.__init__(self, img, img)
        self.connect_clicked(self.__on_click)
        
        
    def set_index(self, idx):
    
        self.__index = idx
        img = self.__sequence[self.__index][0]
        self.set_images(img, img)
        
        
    def set_value(self, v):
    
        idx = 0
        for img, value in self.__sequence:
            if (value == v):
                self.set_index(idx)
                break
            idx += 1
        #end for
        
        
    def __on_click(self):

        self.__index += 1
        self.__index %= len(self.__sequence)
        
        img, value = self.__sequence[self.__index]
        self.set_images(img, img)

        self.send_event(self.EVENT_CHANGED, value)

        
    def connect_changed(self, cb, *args):
    
        self._connect(self.EVENT_CHANGED, cb, *args)

