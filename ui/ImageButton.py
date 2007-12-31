from Widget import Widget
from Pixmap import Pixmap


class ImageButton(Widget):

    def __init__(self, esens, img1, img2):
    
        self.__bg = None
        
        self.__img1 = img1
        self.__img2 = img2
    
        Widget.__init__(self, esens)
        self.set_size(80, 80)
        self.connect(self.EVENT_BUTTON_PRESS, self.__on_click, True)
        self.connect(self.EVENT_BUTTON_RELEASE, self.__on_click, False)               
    
    
    
    def set_size(self, w, h):
    
        Widget.set_size(self, w ,h)
        self.__bg = Pixmap(None, w, h)
    
        
    def render_this(self):
        
        if (not self.may_render()): return
        
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        # save background
        self.__bg.copy_buffer(screen, x, y, 0, 0, w, h)
            
        screen.draw_pixbuf(self.__img1,
                           x + (w - self.__img1.get_width()) / 2,
                           y + (h - self.__img1.get_height()) / 2)
                     
        
    def __on_click(self, px, py, clicked):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()    
        screen = self.get_screen()

        screen.copy_pixmap(self.__bg, 0, 0, x, y, w, h)    
        if (clicked):
            screen.draw_pixbuf(self.__img2,
                               x + (w - self.__img2.get_width()) / 2,
                               y + (h - self.__img2.get_height()) / 2)
        else:
            screen.draw_pixbuf(self.__img1,
                               x + (w - self.__img1.get_width()) / 2,
                               y + (h - self.__img1.get_height()) / 2)

