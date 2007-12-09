import gtk


class TranslucentWindow(gtk.Window):
    """
    Class for a translucent window.
    """

    def __init__(self):
    
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_decorated(False)
        self.set_size_request(800, 480)
        self.move(0, 0)
        #gtk.Layout.__init__(self)
        layout = gtk.Layout()
        layout.show()
        self.add(layout)
        
        self.__bg = gtk.Image()
        self.__bg.show()
        layout.put(self.__bg, 0, 0)   
        
        
    def grab_screen(self, window = None, tint = 0x00000000L):
        """
        Grabs the contents of the given window, dims it and uses it as
        background image.
        """
    
        #w, h = window.window.get_size()
        w, h = 800, 480
        #pmap = window.window
        pmap = gtk.gdk.get_default_root_window()
        cmap = pmap.get_colormap()        
        
        
        pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, w, h)
        pbuf.get_from_drawable(pmap, cmap, 0, 0, 0, 0, w, h)
        
        pbuf = pbuf.composite_color_simple(w, h, gtk.gdk.INTERP_NEAREST,
                                           170, 256, tint, tint)
        self.__bg.set_from_pixbuf(pbuf)
        del pbuf
        
