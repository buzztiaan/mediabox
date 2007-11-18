import gtk
import gobject
import pango


class Item(gtk.gdk.Pixbuf):
    """
    Class for rendering a list item.
    """

    __defer_list = []   # this is a static variable shared by all instances


    def __init__(self, widget, width, height, icon, label, font, background = None):

        self.__initialized = False
        self.__args = (widget, width, height, icon, label, font, background)
    
        gtk.gdk.Pixbuf.__init__(self, gtk.gdk.COLORSPACE_RGB, False, 8,
                                width, height)

        #if (not self.__defer_list):
        #    gobject.idle_add(self.__defer_handler)            
        #self.__defer_list.append(self)
        
        
    def __defer_handler(self):
    
        i = self.__defer_list.pop(0)
        i.get_width()
        if (self.__defer_list):
            return True
        else:
            return False


    def get_width(self):
    
        if (not self.__initialized): self.__initialize()
        return gtk.gdk.Pixbuf.get_width(self)


    def subpixbuf(self, *args):
    
        if (not self.__initialized): self.__initialize()
        return gtk.gdk.Pixbuf.subpixbuf(self, *args)


    def __initialize(self):
    
        self.__initialized = True
        
        widget, width, height, icon, label, font, background = self.__args
    
        pmap = gtk.gdk.Pixmap(None, width, height,
                              gtk.gdk.get_default_root_window().get_depth())
        cmap = widget.get_colormap()
        gc = pmap.new_gc()

        gc.set_foreground(cmap.alloc_color("#ffffff"))
        pmap.draw_rectangle(gc, True, 0, 0, width, height)
                          
        x = 4

        if (background):
            pmap.draw_pixbuf(gc, background, 0, 0, 0, 0,
                             background.get_width(), background.get_height())
            
        if (icon):
            pmap.draw_pixbuf(gc, icon, 0, 0, 4, 16,
                             icon.get_width(), icon.get_height())
            x += icon.get_width()

        gc.set_foreground(cmap.alloc_color("#000000"))

        pc = widget.get_pango_context()
        layout = pango.Layout(pc)
        layout.set_font_description(font)
        layout.set_text(label)
        layout.set_width(width * pango.SCALE)        
        pmap.draw_layout(gc, x, 24, layout)
        
        self.get_from_drawable(pmap, cmap, 0, 0, 0, 0, width, height)
        
        #import gc; gc.collect()
