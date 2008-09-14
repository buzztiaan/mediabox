from ImageButton import ImageButton


class ToggleButton(ImageButton):

    EVENT_TOGGLED = "event-toggled"


    def __init__(self, img1, img2):
        
        self.__active = False
        
        ImageButton.__init__(self, img1, img2, True)
        self.connect_clicked(self.__on_click)
        
        
    def __on_click(self):
    
        self.__active = not self.__active
        self.set_active(self.__active)
        self.send_event(self.EVENT_TOGGLED, self.__active)


    def connect_toggled(self, cb, *args):
    
        self._connect(self.EVENT_TOGGLED, cb, *args)

