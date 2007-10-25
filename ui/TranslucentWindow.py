import gtk


class TranslucentWindow(gtk.Layout):
    """
    Class for a translucent window.
    """

    def __init__(self):
    
        gtk.Layout.__init__(self)
        
        self.__bg = gtk.Image()
        self.__bg.show()
        self.put(self.__bg, 0, 0)   
        
        
    def grab_screen(self, window, tint = 0x00000000L):
        """
        Grabs the contents of the given window, dims it and uses it as
        background image.
        """
    
        w, h = window.window.get_size()
        pmap = window.window
        cmap = window.get_colormap()
        
        pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, w, h)
        pbuf.get_from_drawable(pmap, cmap, 0, 0, 0, 0, w, h)
        
        pbuf = pbuf.composite_color_simple(w, h, gtk.gdk.INTERP_NEAREST,
                                           70, 256, tint, tint)
        self.__bg.set_from_pixbuf(pbuf)
        del pbuf
        
