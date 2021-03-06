"""
B{Used internally}
"""

import gtk


class Pixbuf(gtk.gdk.Pixbuf):
    """
    Wrapper class for pixbuf theme elements.
    @since: 0.96.3
    """

    def __init__(self, path):
    
        self.__path = path
        self.__needs_reload = False
        
    
        pbuf = gtk.gdk.pixbuf_new_from_file(path)
    
        gtk.gdk.Pixbuf.__init__(self, gtk.gdk.COLORSPACE_RGB, True, 8,
                                pbuf.get_width(), pbuf.get_height())
        self.fill(0x00000000)
        pbuf.scale(self, 0, 0,
                   pbuf.get_width(), pbuf.get_height(), 0, 0, 1, 1,
                   gtk.gdk.INTERP_NEAREST)
        del pbuf


    def set_objdef(self, path):
    
        self.__path = path
        self.__needs_reload = True


    def get_path(self):
    
        return self.__path


    def reload(self):
    
        if (self.__needs_reload):
            pbuf = gtk.gdk.pixbuf_new_from_file(self.__path)
    
            self.fill(0x00000000)
            pbuf.scale(self, 0, 0,
                       pbuf.get_width(), pbuf.get_height(), 0, 0, 1, 1,
                       gtk.gdk.INTERP_NEAREST)
            del pbuf
            self.__needs_reload = False
