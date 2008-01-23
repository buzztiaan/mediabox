from Widget import Widget
from Pixmap import Pixmap


class Button(Widget):

    def __init__(self, esens, img1, img2):
    
        self.__bg = None
        self.__buffer = None
        
        self.__state = 0
        self.__img1 = img1
        self.__img2 = img2
    
        Widget.__init__(self, esens)
        self.set_size(80, 80)
        self.connect(self.EVENT_BUTTON_PRESS, self.__on_click, True)
        self.connect(self.EVENT_BUTTON_RELEASE, self.__on_click, False)
    
    
    
    def set_size(self, w, h):
    
        Widget.set_size(self, w ,h)
        self.__bg = Pixmap(None, w, h)
        self.__buffer = Pixmap(None, w, h)
    
    
    def __split_graphics(self, img):
    
        w, h = img.get_width(), img.get_height()
        w3 = w / 3
        h3 = h / 3
        tl = img.subpixbuf(0, 0, w3, h3)
        t = img.subpixbuf(w3, 0, w3, h3)
        tr = img.subpixbuf(w - w3, 0, w3, h3)
        r = img.subpixbuf(w - w3, h3, w3, h3)
        br = img.subpixbuf(w - w3, h - h3, w3, h3)
        b = img.subpixbuf(w3, h - h3, w3, h3)
        bl = img.subpixbuf(0, h - h3, w3, h3)
        l = img.subpixbuf(0, h3, w3, h3)
        c = img.subpixbuf(w3, h3, w3, h3)

        return (tl, t, tr, r, br, b, bl, l, c) 
    
        
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
            self.__state = 1
        else:
            self.__state = 0

        self.render()
        


    def __render_button(self, state):

        if (not self.may_render()): return

        x, y = self.get_screen_pos()
        w, h = self.get_size()    
        screen = self.get_screen()

        if (state == 0):
            img = self.__img1
        else:
            img = self.__img2

        tl, t, tr, r, br, b, bl, l, c = self.__split_graphics(img)
        w1, h1 = tl.get_width(), tl.get_height()
        
        self.__buffer.copy_pixmap(self.__bg, 0, 0, 0, 0, w, h)

        self.__buffer.draw_pixbuf(tl, 0, 0)
        self.__buffer.draw_pixbuf(tr, w - w1, 0)
        self.__buffer.draw_pixbuf(bl, 0, h - h1)        
        self.__buffer.draw_pixbuf(br, w - w1, h - h1)
        
        self.__buffer.draw_pixbuf(t, w1, 0, w - 2 * w1, h1, True)
        self.__buffer.draw_pixbuf(b, w1, h - h1, w - 2 * w1, h1, True)
        self.__buffer.draw_pixbuf(l, 0, h1, w1, h - 2 * h1, True)
        self.__buffer.draw_pixbuf(r, w - w1, h1, w1, h - 2 * h1, True)

        self.__buffer.draw_pixbuf(c, w1, h1, w - 2 * w1, h - 2 * h1, True)
        
        screen.copy_pixmap(self.__buffer, 0, 0, x, y, w, h)

       
        
    def set_images(self, img1, img2):
    
        self.__img1 = img1
        self.__img2 = img2
        
        self.__render_button(self.__state)

