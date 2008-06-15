from Widget import Widget
from Pixmap import Pixmap, TEMPORARY_PIXMAP


class ImageButton(Widget):

    def __init__(self, img1, img2, manual = False):
    
        self.__bg = None
        self.__buffer = None
        self.__state = 0
        
        self.__img1 = img1
        self.__img2 = img2
    
        Widget.__init__(self)
        self.set_size(70, 60)
        
        if (not manual):
            self.connect(self.EVENT_BUTTON_PRESS, self.__on_click, True)
            self.connect(self.EVENT_BUTTON_RELEASE, self.__on_click, False)               
    
    
    def _reload(self):
    
        self.set_images(self.__img1, self.__img2)
    
    
    def set_size(self, w, h):
    
        Widget.set_size(self, w ,h)
        self.__bg = Pixmap(None, w, h)
        self.__buffer = TEMPORARY_PIXMAP #Pixmap(None, w, h)
    
        
    def render_this(self):
        
        if (not self.may_render()): return
        
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        # save background
        self.__bg.copy_buffer(screen, x, y, 0, 0, w, h)

        self.__render_button(self.__state)            
                     
        
    def __on_click(self, px, py, clicked):
    
        if (clicked):
            self.__render_button(1)
        else:
            self.__render_button(0)        
        


    def __render_button(self, state):

        self.__state = state
        if (not self.may_render()): return

        x, y = self.get_screen_pos()
        w, h = self.get_size()    
        screen = self.get_screen()

        if (state == 0):
            img = self.__img1
        else:
            img = self.__img2

        self.__buffer.copy_pixmap(self.__bg, 0, 0, 0, 0, w, h)
        self.__buffer.draw_pixbuf(img,
                                  (w - img.get_width()) / 2,
                                  (h - img.get_height()) / 2)
        screen.copy_pixmap(self.__buffer, 0, 0, x, y, w, h)

       
        
    def set_images(self, img1, img2):
    
        self.__img1 = img1
        self.__img2 = img2
        
        self.__render_button(0)


    def set_active(self, active):
    
        if (active):
            self.__render_button(1)
        else:
            self.__render_button(0)

