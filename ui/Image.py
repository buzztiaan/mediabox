from Widget import Widget


class Image(Widget):

    def __init__(self, pbuf = None):
    
        self.__pbuf = pbuf
           
        Widget.__init__(self)
        if (self.__pbuf):
            self.set_image(self.__pbuf)

       
    def set_image(self, pbuf):        
    
        self.__pbuf = pbuf
        #self.set_size(pbuf.get_width(), pbuf.get_height())

        #self.render()

       
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        if (self.__pbuf and w > 0 and h > 0):
            screen.fit_pixbuf(self.__pbuf, x, y, w, h)

