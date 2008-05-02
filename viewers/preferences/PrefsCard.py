from ui.Widget import Widget
from utils.Observable import Observable
import theme


class PrefsCard(Widget, Observable):
    
    OBS_SCAN_MEDIA = 0
    

    def __init__(self, esens, title):
    
        self.__title = title
    
        Widget.__init__(self, esens)
        self.set_pos(0, 40)
        self.set_size(630, 370)
        

    def get_title(self):
    
        return self.__title
        
