import gtk


class ImageButton(gtk.EventBox):

    def __init__(self, img1, img2, background = None):

        self.__background = background
    
        gtk.EventBox.__init__(self)
        self.connect("button-press-event", self.__on_click, True)
        self.connect("button-release-event", self.__on_click, False)               
    

        
        hbox = gtk.HBox()
        hbox.show()
        self.add(hbox)
        
        self.__img1 = gtk.Image()
        self.__img1.set_from_pixbuf(self.__merge_with_bg(img1))
        self.__img1.show()
        hbox.add(self.__img1)
        
        self.__img2 = gtk.Image()
        self.__img2.set_from_pixbuf(self.__merge_with_bg(img2))        
        hbox.add(self.__img2)
        
        
    def __merge_with_bg(self, pbuf):    
    
        if (not self.__background):
            return pbuf
        else:
            w, h = pbuf.get_width(), pbuf.get_height()
            bg_w = self.__background.get_width()
            bg_h = self.__background.get_height()
            pbuf2 = self.__background.copy()
            pbuf3 = pbuf2.subpixbuf((bg_w - w) / 2, 
                                    (bg_h - h) / 2,
                                    w, h)
            pbuf.composite(pbuf3, 0, 0, w, h,
                           0, 0, 1, 1, gtk.gdk.INTERP_NEAREST, 0xff)
            return pbuf2
        
        

    def __on_click(self, src, ev, clicked):
    
        if (clicked):
            self.__img1.hide()
            self.__img2.show()
        else:
            self.__img2.hide()
            self.__img1.show()
            
