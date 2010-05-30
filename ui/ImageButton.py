from Widget import Widget
from Pixmap import Pixmap
from utils import logging


class ImageButton(Widget):

    def __init__(self, img1, img2, manual = False):
    
        self.__bg = None
        self.__buffer = None
        self.__state = 0
        
        self.__img1 = img1
        self.__img2 = img2
    
        Widget.__init__(self)
        self.set_size(64, 64)
        
        if (not manual):
            self.connect_button_pressed(self.__on_click, True)
            self.connect_button_released(self.__on_click, False)               
    
    
    def _reload(self):
    
        self.set_images(self.__img1, self.__img2)
    
    
    def set_size(self, w, h):
    
        Widget.set_size(self, w ,h)
        self.__bg = None
        self.__buffer = None
    
        
    def render_this(self):
        
        if (not self.may_render()): return
        
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        # save background
        if (not self.__bg):
            self.__bg = Pixmap(None, w, h)
        self.__bg.copy_buffer(screen, x, y, 0, 0, w, h)

        self.__render_button()
                     
        
    def __on_click(self, px, py, clicked):
    
        if (clicked):
            self.__state = 1
        else:
            self.__state = 0
        self.__render_button()
            
        
        
    def _render_content(self, cnv):
        
        pass
    


    def __render_button(self):

        #self.__state = state
        if (not self.may_render() or not self.__bg): return

        x, y = self.get_screen_pos()
        w, h = self.get_size()    
        screen = self.get_screen()

        if (self.__state == 0):
            img = self.__img1
        else:
            img = self.__img2

        if (not self.__buffer):
            self.__buffer = Pixmap(None, w, h)

        self.__buffer.copy_pixmap(self.__bg, 0, 0, 0, 0, w, h)
        
        if ((w, h) != (img.get_width(), img.get_height())):
            self.__buffer.draw_frame(img, 0, 0, w, h, True)
        else:
            self.__buffer.draw_pixbuf(img, 0, 0)
        
        self._render_content(self.__buffer)
        
        screen.copy_pixmap(self.__buffer, 0, 0, x, y, w, h)

       
        
    def set_images(self, img1, img2):
    
        self.__img1 = img1
        self.__img2 = img2
        self.__render_button()


    def set_active(self, active):
    
        if (active):
            self.__state = 1
        else:
            self.__state = 0
        self.__render_button()

