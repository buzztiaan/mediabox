from Widget import Widget


class Image(Widget):

    def __init__(self, esens, pbuf):
    
        self.__pbuf = pbuf
        self.__buffer = None
   
        Widget.__init__(self, esens)
        self.set_image(self.__pbuf)
        
        
    def set_image(self, pbuf):        
    
        self.__pbuf = pbuf
        self.set_size(pbuf.get_width(), pbuf.get_height())

        self.render()

       
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        #if (not self.__buffer):
        #    self.__buffer = screen.subpixmap(x, y, w, h)
        #else:
        #    screen.draw_pixmap(self.__buffer, x, y)

        screen.draw_pixbuf(self.__pbuf, x, y)

