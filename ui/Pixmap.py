import gtk
import pango


_DEPTH = gtk.gdk.get_default_root_window().get_depth()
_PANGO_CTX = gtk.HBox().get_pango_context()
_PANGO_LAYOUT = pango.Layout(_PANGO_CTX)


def pixmap_for_text(text, font):
    """
    Creates and returns a new Pixmap object fitting the given text with the
    given font. The text is not rendered on the Pixmap.
    """

    _PANGO_LAYOUT.set_font_description(font)
    _PANGO_LAYOUT.set_text(text)
        
    rect_a, rect_b = _PANGO_LAYOUT.get_extents()
    nil, nil, w, h = rect_b
    w /= pango.SCALE
    h /= pango.SCALE

    return Pixmap(None, w, h)
    


class Pixmap(object):
    """
    Class for on-screen and off-screen server-side drawables.
    """

    def __init__(self, pmap, w = 0, h = 0):
        
        if (pmap):
            self.__pixmap = pmap
            w, h = pmap.get_size()
            self.__buffered = True
            self.__buffer = gtk.gdk.Pixmap(None, w, h, _DEPTH)
            self.__buffer_gc = self.__buffer.new_gc()
            self.__buffer_cmap = self.__buffer.get_colormap()
        else:
            self.__pixmap = gtk.gdk.Pixmap(None, w, h, _DEPTH)
            self.__buffered = False
            
        self.__width = w
        self.__height = h
        
        self.__gc = self.__pixmap.new_gc()
        self.__cmap = self.__pixmap.get_colormap()
        
        
    def _get_pixmap(self):
    
        return self.__pixmap
        
    
    def _get_buffer(self):
    
        return self.__buffer
        
        
    def is_buffered(self):
    
        return self.__buffered
        
        
    def render_on_pixbuf(self, target = None):
    
        if (not target):
            target = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8,
                                    self.__width, self.__height)
                                    
        pbuf = target.get_from_drawable(self.__pixmap, self.__cmap, 0, 0, 0, 0,
                                 self.__width, self.__height)
        #del pbuf

        return target
        
        
    def set_clip_mask(self, mask = None):
    
        if (mask):
            self.__gc.set_clip_mask(mask)
            if (self.__buffered):
                self.__buffer_gc.set_clip_mask(mask)
        else:
            rect = gtk.gdk.Rectangle(0, 0, self.__width, self.__height)
            self.__gc.set_clip_rectangle(rect)
            if (self.__buffered):
                self.__buffer_gc.set_clip_rectangle(rect)
        
        
    def get_size(self):
    
        return (self.__width, self.__height)


    def fill_area(self, x, y, w, h, color):
    
        col = self.__cmap.alloc_color(color)
        self.__gc.set_foreground(col)
        self.__pixmap.draw_rectangle(self.__gc, True, x, y, w, h)

        if (self.__buffered):
            self.__buffer_gc.set_foreground(col)
            self.__buffer.draw_rectangle(self.__buffer_gc, True, x, y, w, h)
        
        
    def move_area(self, x, y, w, h, dx, dy):
            
        self.__pixmap.draw_drawable(self.__gc, self.__pixmap,
                                    x, y, x + dx, y + dy, w, h)

        if (self.__buffered):
            self.__buffer.draw_drawable(self.__buffer_gc, self.__buffer,
                                        x, y, x + dx, y + dy, w, h)


    def draw_line(self, x1, y1, x2, y2, color):
    
        col = self.__cmap.alloc_color(color)
        self.__gc.set_foreground(col)
        self.__pixmap.draw_line(self.__gc, x1, y1, x2, y2)

        if (self.__buffered):
            self.__buffer_gc.set_foreground(col)
            self.__buffer.draw_line(self.__buffer_gc, x1, y1, x2, y2)


    def draw_rect(self, x, y, w, h, color):
    
        w -= 1
        h -= 1
        col = self.__cmap.alloc_color(color)
        self.__gc.set_foreground(col)
        self.__pixmap.draw_rectangle(self.__gc, False, x, y, w, h)

        if (self.__buffered):
            self.__buffer_gc.set_foreground(col)
            self.__buffer.draw_rectangle(self.__buffer_gc, False, x, y, w, h)


                                    

    def draw_text(self, text, font, x, y, color, use_markup = False):

        _PANGO_LAYOUT.set_font_description(font)
        _PANGO_LAYOUT.set_text("")
        _PANGO_LAYOUT.set_markup("")
        if (use_markup):
            _PANGO_LAYOUT.set_markup(text)
        else:
            _PANGO_LAYOUT.set_text(text)
        self.__gc.set_foreground(self.__cmap.alloc_color(color))
        
        rect_a, rect_b = _PANGO_LAYOUT.get_extents()
        nil, nil, w, h = rect_b
        w /= pango.SCALE
        h /= pango.SCALE
        w = min(w, self.__width - x)
        h = min(h, self.__height - y)
        
        self.__pixmap.draw_layout(self.__gc, x, y, _PANGO_LAYOUT)

        if (self.__buffered):        
            self.__buffer_gc.set_foreground(self.__buffer_cmap.alloc_color(color))
            self.__buffer.draw_layout(self.__buffer_gc, x, y, _PANGO_LAYOUT)
        
        
    def draw_pixbuf(self, pbuf, x, y, w = -1, h = -1, scale = False):
    
        if (scale):
            pbuf = pbuf.scale_simple(w, h, gtk.gdk.INTERP_BILINEAR)
    
        self.__pixmap.draw_pixbuf(self.__gc, pbuf,
                                  0, 0, x, y, w, h)

        if (self.__buffered):
            if (w == -1): w = pbuf.get_width()
            if (h == -1): h = pbuf.get_height()
            
            self.__buffer.draw_pixbuf(self.__buffer_gc, pbuf,
                                      0, 0, x, y, w, h)

                                       
        del pbuf


    def draw_subpixbuf(self, pbuf, srcx, srcy, dstx,dsty, w, h):
    
        self.__pixmap.draw_pixbuf(self.__gc, pbuf, srcx, srcy, dstx, dsty, w, h)
        
        if (self.__buffered):
            self.__buffer.draw_pixbuf(self.__buffer_gc, pbuf, srcx, srcy,
                                      dstx, dsty, w, h)


    def __split_frame(self, img):
    
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


    def draw_frame(self, framepbuf, x, y, w, h, filled):
    
        tl, t, tr, r, br, b, bl, l, c = self.__split_frame(framepbuf)
        w1, h1 = tl.get_width(), tl.get_height()
        
        self.draw_pixbuf(tl, x, y)
        self.draw_pixbuf(tr, x + w - w1, y)
        self.draw_pixbuf(bl, x, y + h - h1)        
        self.draw_pixbuf(br, x + w - w1, y + h - h1)
        
        self.draw_pixbuf(t, x + w1, y, w - 2 * w1, h1, True)
        self.draw_pixbuf(b, x + w1, y + h - h1, w - 2 * w1, h1, True)
        self.draw_pixbuf(l, x, y + h1, w1, h - 2 * h1, True)
        self.draw_pixbuf(r, x + w - w1, y + h1, w1, h - 2 * h1, True)

        if (filled):
            self.draw_pixbuf(c, x + w1, y + h1, w - 2 * w1, h - 2 * h1, True)        
                                                
        
    def copy_pixmap(self, pmap, srcx, srcy, dstx, dsty, w, h):
    
        self.__pixmap.draw_drawable(self.__gc, pmap._get_pixmap(),
                                    srcx, srcy, dstx, dsty, w, h)

        if (self.__buffered):
            if (pmap == self):                
                self.__buffer.draw_drawable(self.__buffer_gc, self.__buffer,
                                            srcx, srcy, dstx, dsty, w, h)
            else:    
                self.__buffer.draw_drawable(self.__buffer_gc, pmap._get_pixmap(),
                                            srcx, srcy, dstx, dsty, w, h)


    def copy_buffer(self, pmap, srcx, srcy, dstx, dsty, w, h):
    
        if (pmap.is_buffered()):
            self.__pixmap.draw_drawable(self.__gc, pmap._get_buffer(),
                                        srcx, srcy, dstx, dsty, w, h)
            if (self.__buffered):            
                self.__buffer.draw_drawable(self.__buffer_gc, pmap._get_buffer(),
                                            srcx, srcy, dstx, dsty, w, h)
        else:
            self.copy_pixmap(pmap, srcx, srcy, dstx, dsty, w, h)
            


    def restore(self, x, y, w, h):
    
        if (not self.__buffered): return
        
        self.__pixmap.draw_drawable(self.__gc, self.__buffer,
                                    x, y, x, y, w, h)
        
