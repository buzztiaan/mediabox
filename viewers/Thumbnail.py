import gtk
import gobject
import pango


_BPP = gtk.gdk.get_default_root_window().get_depth()
_TEXT_PMAP = gtk.gdk.Pixmap(None, 800, 200, _BPP)
_TEXT_GC = _TEXT_PMAP.new_gc()
_TEXT_CMAP = _TEXT_PMAP.get_colormap()
_PANGO_CTX = gtk.HBox().get_pango_context()
_PANGO_LAYOUT = pango.Layout(_PANGO_CTX)



class Thumbnail(gtk.gdk.Pixbuf):

    __defer_list = []   # this is a static variable shared by all instances
    

    def __init__(self, width = 160, height = 120):

        self.__defer_queue = []
        self.__deferred = True
    
        gtk.gdk.Pixbuf.__init__(self, gtk.gdk.COLORSPACE_RGB, False,
                                8, width, height)
        #gtk.gdk.Pixbuf.fill(self, 0x00000000L)


        #if (not self.__defer_list):
        #    gobject.idle_add(self.__defer_handler)
        #self.__defer_list.append(self)
        #self.__initialize()
        
        
    def __defer_handler(self):
    
        i = self.__defer_list.pop(0)
        i.get_width()
        if (self.__defer_list):
            return True
        else:
            return False


    def __defer(self, f, *args):
    
        self.__defer_queue.append((f, args))


    def __initialize(self):
    
        self.__deferred = False

        for f, args in self.__defer_queue:
            f(*args)
        self.__defer_queue = []
            
            
    def get_width(self):
    
        if (self.__deferred):
            self.__initialize()
        return gtk.gdk.Pixbuf.get_width(self)


    def save(self, uri):
                    
        if (self.__deferred):
            self.__defer(self.save, uri)
            return
            
        gtk.gdk.Pixbuf.save(self, uri, "jpeg")


    def fill_color(self, color):
                
        r = color.red >> 8
        g = color.green >> 8
        b = color.blue >> 8
        self.fill(r, g, b)


    def fill(self, r, g, b):
    
        if (self.__deferred):
            self.__defer(self.fill, r, g, b)
            return

        color = (r << 24) + (g << 16) + (b << 8) + 0xff
        gtk.gdk.Pixbuf.fill(self, color)
            

    def add_rect(self, x, y, w, h, color, a = 0xff):    

        if (self.__deferred):
            self.__defer(self.add_rect, x, y, w, h, color, a)
            return

        r = color.red >> 8
        g = color.green >> 8
        b = color.blue >> 8

        color = (r << 24) + (g << 16) + (b << 8) + a
        subpbuf = self.subpixbuf(x, y, w, h)
        
        rect = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, w, h)
        rect.fill(color)
        rect.composite(subpbuf, 0, 0, w, h, x, y, 1, 1,
                       gtk.gdk.INTERP_NEAREST, 0xff)
        del rect
        #import gc; gc.collect()
                
    
    def add_text(self, text, x, y, font, color):

        if (self.__deferred):
            self.__defer(self.add_text, text, x, y, font, color)
            return
    
        _PANGO_LAYOUT.set_font_description(font)
        _PANGO_LAYOUT.set_text(text)
        _TEXT_GC.set_foreground(_TEXT_CMAP.alloc_color(color))
        
        rect_a, rect_b = _PANGO_LAYOUT.get_extents()
        nil, nil, w, h = rect_b
        w /= pango.SCALE
        h /= pango.SCALE
        w = min(w, self.get_width() - x)
        h = min(h, self.get_height() - y)
        
        
        _TEXT_PMAP.draw_pixbuf(_TEXT_GC, self, x, y, 0, 0, w, h)
        _TEXT_PMAP.draw_layout(_TEXT_GC, 0, 0, _PANGO_LAYOUT)
        
        pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, 400, 100)
        self.get_from_drawable(_TEXT_PMAP, _TEXT_CMAP,
                               0, 0, x, y, w, h)
        
                    

    def add_image(self, img, x = 0, y = 0, width = -1, height = -1):

        if (self.__deferred):
            self.__defer(self.add_image, img, x, y, width, height)
            return
        
        if (hasattr(img, "fill")):
            pbuf = img
        else:
            try:
                pbuf = gtk.gdk.pixbuf_new_from_file(img)
            except:
                return
            
        pbuf_width = pbuf.get_width()
        pbuf_height = pbuf.get_height()

        if (width == height == -1):
            pbuf.composite(self, x, y,
                           pbuf_width, pbuf_height,
                           x, y, 1, 1,
                           gtk.gdk.INTERP_BILINEAR, 0xff)                        
        else:
            sx = width / float(pbuf_width)
            sy = height / float(pbuf_height)

            scale = min(sx, sy)
            offx = (width - pbuf_width * scale) / 2
            offy = (height - pbuf_height * scale) / 2

            pbuf.composite(self, int(x + offx), int(y + offy),
                           int(pbuf_width * scale), int(pbuf_height * scale),
                           int(x + offx), int(y + offy), scale, scale,
                           gtk.gdk.INTERP_BILINEAR, 0xff)
        del pbuf
        #import gc; gc.collect()
        
