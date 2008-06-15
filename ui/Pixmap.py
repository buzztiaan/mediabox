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

    TOP = 1
    BOTTOM = 2
    LEFT = 4
    RIGHT = 8
    

    def __init__(self, pmap, w = 0, h = 0):
        
        self.__is_hibernating = False
        
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
        
        
    def clone(self):
        """
        Returns an exact clone of this pixmap.
        """
        
        if (self.__buffered):
            new_pmap = Pixmap(self.__pixmap, self.__width, self.__height)
        else:
            new_pmap = Pixmap(None, self.__width, self.__height)
        new_pmap.draw_pixmap(self, 0, 0)

        return new_pmap


    def subpixmap(self, x, y, w, h):
        """
        Returns a new pixmap containing the given portion.
        """
        
        new_pmap = Pixmap(None, w, h)
        new_pmap.copy_buffer(self, x, y, 0, 0, w, h)
        
        return new_pmap
        


    def hibernate(self):
        """
        Hibernates this pixmap to save memory. Issue 'wakeup' before working
        with this pixmap again. Subclasses may extend this method.
        """
        
        del self.__pixmap
        self.__pixmap = None
        self.__gc = None
        self.__cmap = None
        self.__is_hibernating = True


    def wakeup(self):
        """
        Restores this pixmap after hibernating. Subclasses may extend this
        method.
        """

        if (self.is_hibernating()):
            print "wakeup"
            self.__pixmap = gtk.gdk.Pixmap(None,
                                           self.__width, self.__height, _DEPTH)
            self.__gc = self.__pixmap.new_gc()
            self.__cmap = self.__pixmap.get_colormap()
            self.__is_hibernating = False


    def is_hibernating(self):
        """
        Returns whether this pixmap is currently hibernating.
        """

        return self.__is_hibernating
        
        
    def resize(self, w, h):
        """
        Resizes this pixmap and discards its contents.
        """
        
        new_pmap = gtk.gdk.Pixmap(None, w, h, _DEPTH)
        self.__gc = new_pmap.new_gc()
        self.__cmap = new_pmap.get_colormap()
        del self.__pixmap
        self.__pixmap = new_pmap

        self.__width = w
        self.__height = h        
        
        
    def is_buffered(self):
        """
        Returns whether this pixmap is buffered. Offscreen pixmaps are never
        buffered.
        """
    
        return self.__buffered
        
        
    def render_on_pixbuf(self, target = None):
        """
        Renders this pixmap to a pixbuf and returns the pixbuf. If target is
        given, it does not create a new pixbuf.
        """
    
        if (not target):
            target = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8,
                                    self.__width, self.__height)

        w = target.get_width()
        h = target.get_height()                                    
        pbuf = target.get_from_drawable(self.__pixmap, self.__cmap, 0, 0, 0, 0,
                                 min(w, self.__width), min(h, self.__height))
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
        """
        Returns the width and height of this pixmap.
        """        

        return (self.__width, self.__height)


    def fill_area(self, x, y, w, h, color):
        """
        Fills the given area with the given color (opaquely).
        """
    
        col = self.__cmap.alloc_color(str(color))
        self.__gc.set_foreground(col)
        self.__pixmap.draw_rectangle(self.__gc, True, x, y, w, h)

        if (self.__buffered):
            self.__buffer_gc.set_foreground(col)
            self.__buffer.draw_rectangle(self.__buffer_gc, True, x, y, w, h)
        
        
    def move_area(self, x, y, w, h, dx, dy):
        """
        Moves the given area on this pixmap by the given amount.
        """
            
        self.copy_buffer(self, x, y, x + dx, y + dy, w, h)
        #self.__pixmap.draw_drawable(self.__gc, self.__pixmap,
        #                            x, y, x + dx, y + dy, w, h)

        #if (self.__buffered):
        #    self.__buffer.draw_drawable(self.__buffer_gc, self.__buffer,
        #                                x, y, x + dx, y + dy, w, h)


    def draw_line(self, x1, y1, x2, y2, color):
        """
        Draws a line of the given color.
        """
    
        col = self.__cmap.alloc_color(str(color))
        self.__gc.set_foreground(col)
        self.__pixmap.draw_line(self.__gc, x1, y1, x2, y2)

        if (self.__buffered):
            self.__buffer_gc.set_foreground(col)
            self.__buffer.draw_line(self.__buffer_gc, x1, y1, x2, y2)


    def draw_rect(self, x, y, w, h, color):
        """
        Draws a rectangle of the given color.
        """
    
        w -= 1
        h -= 1
        col = self.__cmap.alloc_color(str(color))
        self.__gc.set_foreground(col)
        self.__pixmap.draw_rectangle(self.__gc, False, x, y, w, h)

        if (self.__buffered):
            self.__buffer_gc.set_foreground(col)
            self.__buffer.draw_rectangle(self.__buffer_gc, False, x, y, w, h)


                                    

    def draw_text(self, text, font, x, y, color, use_markup = False):
        """
        Renders the given text string.
        """

        _PANGO_LAYOUT.set_font_description(font)
        _PANGO_LAYOUT.set_text("")
        _PANGO_LAYOUT.set_markup("")
        if (use_markup):
            _PANGO_LAYOUT.set_markup(text)
        else:
            _PANGO_LAYOUT.set_text(text)
        self.__gc.set_foreground(self.__cmap.alloc_color(str(color)))
        
        rect_a, rect_b = _PANGO_LAYOUT.get_extents()
        nil, nil, w, h = rect_b
        w /= pango.SCALE
        h /= pango.SCALE
        w = min(w, self.__width - x)
        h = min(h, self.__height - y)
        
        self.__pixmap.draw_layout(self.__gc, x, y, _PANGO_LAYOUT)

        if (self.__buffered):        
            self.__buffer_gc.set_foreground(
                                       self.__buffer_cmap.alloc_color(str(color)))
            self.__buffer.draw_layout(self.__buffer_gc, x, y, _PANGO_LAYOUT)
        
        
    def draw_pixbuf(self, pbuf, x, y, w = -1, h = -1, scale = False):
        """
        Renders the given pixbuf.
        """
    
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


    def draw_subpixbuf(self, pbuf, srcx, srcy, dstx, dsty, w, h):
        """
        Renders a part of the pixbuf.
        """
    
        self.__pixmap.draw_pixbuf(self.__gc, pbuf, srcx, srcy, dstx, dsty, w, h)
        
        if (self.__buffered):
            self.__buffer.draw_pixbuf(self.__buffer_gc, pbuf, srcx, srcy,
                                      dstx, dsty, w, h)
                                      

    def fit_pixbuf(self, pbuf, x, y, w, h):
        """
        Renders the given pixbuf so that it fits the given area. The pixbuf
        is scaled while retaining the original aspect ratio.
        """

        pbuf_width = pbuf.get_width()
        pbuf_height = pbuf.get_height()

        sx = w / float(pbuf_width)
        sy = h / float(pbuf_height)

        scale = min(sx, sy)
        offx = (w - pbuf_width * scale) / 2
        offy = (h - pbuf_height * scale) / 2

        self.draw_pixbuf(pbuf, int(x + offx), int(y + offy),
                         int(pbuf_width * scale), int(pbuf_height * scale),
                         scale = True)


    def draw_pixmap(self, pmap, x, y):
    
        w, h = pmap.get_size()
        self.copy_pixmap(pmap, 0, 0, x, y, w, h)


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


    def draw_frame(self, framepbuf, x, y, w, h, filled, parts = 0xf):
        """
        Draws a frame by stretching and tiling the given pixbuf.
        """

        tl, t, tr, r, br, b, bl, l, c = self.__split_frame(framepbuf)
        w1, h1 = tl.get_width(), tl.get_height()
        w1 = min(w1, w / 3)
        h1 = min(h1, h / 3)
        w2 = w1
        h2 = h1

        if (not parts & self.TOP):
            h1 = 0
        if (not parts & self.BOTTOM):
            h2 = 0
        if (not parts & self.LEFT):
            w1 = 0
        if (not parts & self.RIGHT):
            w2 = 0

        if (parts & self.TOP):        
            if (parts & self.LEFT):
                self.draw_pixbuf(tl, x, y, w1, h1)
            if (parts & self.RIGHT):
                self.draw_pixbuf(tr, x + w - w2, y, w2, h1)
        if (parts & self.BOTTOM):
            if (parts & self.LEFT):
                self.draw_pixbuf(bl, x, y + h - h2, w1, h2)
            if (parts & self.RIGHT):
                self.draw_pixbuf(br, x + w - w2, y + h - h2, w2, h2)
        
        if (parts & self.TOP):
            self.draw_pixbuf(t, x + w1, y, w - w1 - w2, h1, True)
        if (parts & self.BOTTOM):
            self.draw_pixbuf(b, x + w1, y + h - h2, w - w1 - w2, h2, True)
        if (parts & self.LEFT):
            self.draw_pixbuf(l, x, y + h1, w1, h - h1 - h2, True)
        if (parts & self.RIGHT):
            self.draw_pixbuf(r, x + w - w2, y + h1, w2, h - h1 - h2, True)

        if (filled):
            self.draw_pixbuf(c, x + w1, y + h1, w - w1 - w2, h - h1 - h2, True)        
                                                
        
    def copy_pixmap(self, pmap, srcx, srcy, dstx, dsty, w, h):
        """
        Copies content from another pixmap onto this.
        """
    
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
        """
        Copies content from another pixmap to this. If the other pixmap is
        buffered, the contents of the buffer are used. You will normally want
        to use this method instead of 'copy_pixmap' when copying from a buffered
        pixmap.
        """
    
        if (pmap.is_buffered()):
            self.__pixmap.draw_drawable(self.__gc, pmap._get_buffer(),
                                        srcx, srcy, dstx, dsty, w, h)
            if (self.__buffered):            
                self.__buffer.draw_drawable(self.__buffer_gc, pmap._get_buffer(),
                                            srcx, srcy, dstx, dsty, w, h)
        else:
            self.copy_pixmap(pmap, srcx, srcy, dstx, dsty, w, h)
            


    def restore(self, x, y, w, h):
        """
        Restores the given area from buffer, if this pixmap is buffered.
        Otherwise, it does nothing.
        """
    
        if (not self.__buffered): return
        
        self.__pixmap.draw_drawable(self.__gc, self.__buffer,
                                    x, y, x, y, w, h)


    def get_pixmap(self):
        
        print "REMOVE get_pixmap() from Pixmap"
        return self
        

"""
The temporary pixmap is a pixmap for temporary drawing operations.
"""
TEMPORARY_PIXMAP = Pixmap(None, 800, 480)

