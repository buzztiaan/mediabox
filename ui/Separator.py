from Widget import Widget


class Separator(Widget):
    """
    Separator widget to put space between widgets.
    """

    def __init__(self):
    
        self.__bg = None
    
        Widget.__init__(self)
        

    def set_background(self, bg):
    
        self.__bg = bg        
       
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        if (self.__bg):
            screen.draw_pixbuf(self.__bg, x, y)

