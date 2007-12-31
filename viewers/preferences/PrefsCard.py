from ui.Widget import Widget
import theme


class PrefsCard(Widget):

    def __init__(self, esens, title):
    
        self.__title = title
    
        Widget.__init__(self, esens)
        self.set_pos(0, 50)
        self.set_size(620, 350)
        

    def get_title(self):
    
        return self.__title
        
