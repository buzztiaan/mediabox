from Widget import Widget


class Separator(Widget):

    def __init__(self, esens):
    
        self.__bg = None
    
        Widget.__init__(self, esens)
        

    def set_background(self, bg):
    
        self.__bg = bg        
       
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        if (self.__bg):
            screen.draw_pixbuf(self.__bg, x, y)

