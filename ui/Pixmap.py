"""
Class for on-screen and off-screen drawables.
"""

import gtk
import pango

try:
    import cairo
except:
    _HAVE_CAIRO = False
else:
    _HAVE_CAIRO = True



#_PANGO_CTX = gtk.HBox().get_pango_context()
#_PANGO_LAYOUT = pango.Layout(_PANGO_CTX)

# table: bpp -> layout
_pango_layouts = {}


def _get_colormap_and_depth():

    screen = gtk.gdk.screen_get_default()
    try:
        have_rgba = screen.is_composited()
    except:
        have_rgba = False
    if (have_rgba):
        cmap = screen.get_rgba_colormap()        
    else:
        cmap = screen.get_rgb_colormap()

    depth = cmap.get_visual().depth

    return (cmap, depth)


def _get_pango_layout():
       
    if (not _DEPTH in _pango_layouts):
        w = gtk.HBox()
        w.set_colormap(_CMAP)        
        ctx = gtk.HBox().get_pango_context()
        layout = pango.Layout(ctx)
        _pango_layouts[_DEPTH] = layout
        
    return _pango_layouts[_DEPTH]
    


def _reload(*items):
    """
    Attempts reloading the given items.
    """

    for item in items:
        try:
            item.reload()
        except:
            pass


def text_extents(text, font):
    """
    Returns the width and height required for the given text with the given
    font.
    """

    _reload(font)
    layout = _get_pango_layout()
    layout.set_font_description(font)
    layout.set_text(text)
        
    rect_a, rect_b = layout.get_extents()
    nil, nil, w, h = rect_b
    w /= pango.SCALE
    h /= pango.SCALE

    return (w, h)


def pixmap_for_text(text, font):
    """
    Creates and returns a new Pixmap object fitting the given text with the
    given font. The text is not rendered on the Pixmap.
    """

    _reload(font)
    w, h = text_extents(text, font)
    return Pixmap(None, w, h)


_CMAP, _DEPTH = _get_colormap_and_depth()    


class Pixmap(object):
    """
    Class for on-screen and off-screen server-side drawables.
    All rendering operations should be performed using this class.
    """

    TOP = 1
    BOTTOM = 2
    LEFT = 4
    RIGHT = 8
    

    def __init__(self, pmap, w = 0, h = 0):
        """
        Creates a new Pixmap object. If C{pmap} is C{None}, the pixmap will
        be off-screen, otherwise it will be on-screen.
        
        @param pmap: GDK drawable to render on
        @param w: width
        @param h: height
        """
        self.__layout = _get_pango_layout()

        self.__pixmap = None
        self.__cmap = None
        self.__gc = None
        self.__cairo_ctx = None

        self.__buffer = None
        self.__buffer_cmap = None
        self.__buffer_gc = None


        if (pmap):
            self.__pixmap = pmap
            self.__buffered = True
            self.__create_buffer()
        else:
            self.__pixmap = gtk.gdk.Pixmap(None, w, h, _DEPTH)
            self.__buffered = False
            
        self.__width = w
        self.__height = h
        
        self.__cmap = self.__pixmap.get_colormap() or _CMAP
        self.__pixmap.set_colormap(self.__cmap)
        self.__gc = self.__pixmap.new_gc()
        
        if (_HAVE_CAIRO):
            self.__cairo_ctx = self.__pixmap.cairo_create()
                
                        
    def _get_pixmap(self):
    
        return self.__pixmap
        
        
    def _get_cairo_context(self):
    
        return self.__cairo_ctx
        
    
    def _get_buffer(self):
    
        return self.__buffer
        
        
    def __create_buffer(self):
    
        w, h = self.__pixmap.get_size()
        self.__buffer = gtk.gdk.Pixmap(None, w, h, _DEPTH)
        self.__buffer_cmap = self.__buffer.get_colormap() or _CMAP
        self.__buffer.set_colormap(self.__buffer_cmap)
        self.__buffer_gc = self.__buffer.new_gc()

        

    def __to_buffer(self, x, y, w, h):
        """
        Copies the given area to the buffer.
        """
    
        if (not self.__buffer): return
        
        self.__buffer.draw_drawable(self.__buffer_gc, self.__pixmap,
                                    x, y, x, y, w, h)
            
            
        
    def clone(self):
        """
        Returns an exact clone of this pixmap.
        
        @return: clone of this pixmap
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
        
        @param x y w h: coordinates of subpixmap
        """
        
        new_pmap = Pixmap(None, w, h)
        new_pmap.copy_buffer(self, x, y, 0, 0, w, h)
        
        return new_pmap
              
        
    def resize(self, w, h):
        """
        Resizes this pixmap and discards its contents.
        
        @param w: width
        @param h: height
        """
        
        cmap, depth = _get_colormap_and_depth()
        
        new_pmap = gtk.gdk.Pixmap(None, w, h, depth)
        self.__gc = new_pmap.new_gc()
        self.__cmap = new_pmap.get_colormap() or cmap
        new_pmap.set_colormap(self.__cmap)
        del self.__pixmap
        self.__pixmap = new_pmap
        if (_HAVE_CAIRO):
            self.__cairo_ctx = self.__pixmap.cairo_create()

        self.__width = w
        self.__height = h        
        
        
    def rotate(self, angle):
        """
        Rotates this pixmap by the given angle. Angle must be one of
        0, 90, 180, 270.
        
        @param angle: angle in degrees
        """
        assert angle in (0, 90, 180, 270)
        
        if (angle == 0):
            method = gtk.gdk.PIXBUF_ROTATE_NONE
        elif (angle == 90):
            method = gtk.gdk.PIXBUF_ROTATE_COUNTERCLOCKWISE
        elif (angle == 180):
            method = gtk.gdk.PIXBUF_ROTATE_UPSIDEDOWN
        else:
            method = gtk.gdk.PIXBUF_ROTATE_CLOCKWISE
        pbuf = self.render_on_pixbuf()
        
        rpbuf = pbuf.rotate_simple(method)
        self.resize(rpbuf.get_width(), rpbuf.get_height())
        del pbuf
        self.draw_pixbuf(rpbuf, 0, 0)
        del rpbuf
        
        
        
        
        
    def is_buffered(self):
        """
        Returns whether this pixmap is buffered. Offscreen pixmaps are never
        buffered.
        
        @return: whether this pixmap is buffered
        """
    
        return (self.__buffer != None)
        
        
    def is_offscreen(self):
        """
        @return: whether this pixmap is offscreen
        """
        
        return (self.__pixmap == None)


    def get_color_depth(self):
        """
        Returns the color depth in bits per pixel.
        
        @return: color depth
        """
        
        return _DEPTH
        
        
    def render_on_pixbuf(self, target = None):
        """
        Renders this pixmap to a pixbuf and returns the pixbuf. If target is
        given, it does not create a new pixbuf.
        
        @param target: target pixbuf to use
        @return: pixbuf
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


    def set_clip_rect(self, *args):
        """
        Sets the clipping rectangle.
        Pass None to disable clipping.
        """
    
        if (len(args) == 4):
            cx, cy, cw, ch = args
            rect = gtk.gdk.Rectangle(cx, cy, cw, ch)
            
        else:
            rect = gtk.gdk.Rectangle(0, 0, self.__width, self.__height)

        self.__gc.set_clip_rectangle(rect)
        #if (self.__buffered):
        #    self.__buffer_gc.set_clip_rectangle(rect)


    def set_clip_mask(self, mask = None):
        """
        @todo: DEPRECATED
        """
     
        if (mask):
            self.__gc.set_clip_mask(mask)
            if (self.__buffered):
                self.__buffer_gc.set_clip_mask(mask)
        else:
            rect = gtk.gdk.Rectangle(0, 0, self.__width, self.__height)
            self.__gc.set_clip_rectangle(rect)
            #if (self.__buffered):
            #    self.__buffer_gc.set_clip_rectangle(rect)


              
        
    def get_size(self):
        """
        Returns the width and height of this pixmap.
        
        @return: a tuple (width, height) holding the size
        """

        return (self.__width, self.__height)


    def __parse_color(self, color):
        """
        Parses a color string and returns the RGBA values as quadruple.
        """
        
        color = str(color)
        if (len(color) < 9):
            color += "ff"

        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        a = int(color[7:9], 16)
        
        return (r, g, b, a)
        


    def clear_translucent(self):

        if (_HAVE_CAIRO):
            self.__cairo_ctx.save()
            self.__cairo_ctx.set_source_rgba(1, 1, 1, 0)
            self.__cairo_ctx.set_operator(cairo.OPERATOR_SOURCE)
            self.__cairo_ctx.paint()
            self.__cairo_ctx.restore()
            
            w, h = self.get_size()
            self.__to_buffer(0, 0, w, h)
        #end if


    def fill_area(self, x, y, w, h, color):
        """
        Fills the given area with the given color (opaquely).
        
        @param x y w h: area to fill
        @param color: fill color
        """
        assert (w > 0 and h > 0)

        _reload(color)
        
        if (_HAVE_CAIRO):
            r, g, b, a = self.__parse_color(color)
            r /= 255.0
            g /= 255.0
            b /= 255.0
            a /= 255.0
            self.__cairo_ctx.save()
            if (a < 0.999):
                self.__cairo_ctx.set_source_rgba(r, g, b, a)
            else:
                self.__cairo_ctx.set_source_rgb(r, g, b)
            self.__cairo_ctx.rectangle(x, y, w, h)
            self.__cairo_ctx.fill()
            self.__cairo_ctx.restore()
        
        else:
            if (len(str(color)) == 9):
                # RGBA
                pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, w, h)
                pbuf.fill(long(str(color)[1:], 16))
                self.draw_pixbuf(pbuf, x, y)
                del pbuf
            
            else:
                # RGB
                col = self.__cmap.alloc_color(str(color))
                self.__gc.set_foreground(col)
                self.__pixmap.draw_rectangle(self.__gc, True, x, y, w, h)
    
        self.__to_buffer(x, y, w, h)
        
        
    def move_area(self, x, y, w, h, dx, dy):
        """
        Moves the given area on this pixmap by the given amount.
        
        @param x y w h: area to move
        @param dx dy: amount
        """

        self.copy_buffer(self, x, y, x + dx, y + dy, w, h)



    def draw_line(self, x1, y1, x2, y2, color):
        """
        Draws a line of the given color.
        
        @param x1 y1: start point
        @param x2 y2: end point
        @param color: color
        """
    
        _reload(color)
        col = self.__cmap.alloc_color(str(color))
        self.__gc.set_foreground(col)
        self.__pixmap.draw_line(self.__gc, x1, y1, x2, y2)

        self.__to_buffer(min(x1, x2), min(y1, y2),
                         abs(x1 - x2), abs(y1 - y2))


    def draw_rect(self, x, y, w, h, color):
        """
        Draws a rectangle of the given color.
        
        @param x y w h: rectangle
        @param color: border color
        """
    
        _reload(color)
        w -= 1
        h -= 1
        col = self.__cmap.alloc_color(str(color))
        self.__gc.set_foreground(col)
        self.__pixmap.draw_rectangle(self.__gc, False, x, y, w, h)

        self.__to_buffer(x, y, w, h)


    def draw_centered_text(self, text, font, x, y, w, h, color,
                           use_markup = False):
        """
        Centers the given text string within the given area.

        @param text: text string
        @param font: font
        @param x y w h: area
        @param color: text color
        @param use_markup: whether text contains Pango markup
        """                        
   
        _reload(font, color)
        tw, th = text_extents(text, font)
        tx = x + (w - tw) / 2
        ty = y + (h - th) / 2
        self.draw_text(text, font, tx, ty, color, use_markup)

                                    

    def draw_text(self, text, font, x, y, color, use_markup = False):
        """
        Renders the given text string.
        
        @param text: text string
        @param font: font
        @param x y: coordinates of top-left corner
        @param color: text color
        @param use_markup: whether text contains Pango markup
        """

        _reload(font, color)
        self.__layout.set_font_description(font)
        self.__layout.set_text("")
        self.__layout.set_markup("")
        if (use_markup):
            self.__layout.set_markup(text)
        else:
            self.__layout.set_text(text)
        self.__gc.set_foreground(self.__cmap.alloc_color(str(color)))
        
        rect_a, rect_b = self.__layout.get_extents()
        nil, nil, w, h = rect_b
        w /= pango.SCALE
        h /= pango.SCALE
        w = min(w, self.__width - x)
        h = min(h, self.__height - y)
        
        self.__pixmap.draw_layout(self.__gc, x, y, self.__layout)

        self.__to_buffer(x, y, w, h)
        
        
    def draw_pixbuf(self, pbuf, x, y, w = -1, h = -1, scale = False):
        """
        Renders the given pixbuf.
        
        @param pbuf: pixbuf image
        @param x y: coordinates
        @param w h: size
        @param scale: scale to given size or simply crop to size
        """

        _reload(pbuf)
        if (scale):
            pbuf = pbuf.scale_simple(w, h, gtk.gdk.INTERP_BILINEAR)
        self.__pixmap.draw_pixbuf(self.__gc, pbuf,
                                  0, 0, x, y, w, h)

        if (w == -1): w = pbuf.get_width()
        if (h == -1): h = pbuf.get_height()
        self.__to_buffer(x, y, w, h)

        del pbuf


    def draw_subpixbuf(self, pbuf, srcx, srcy, dstx, dsty, w, h):
        """
        Renders a part of the pixbuf.
        
        @param pbuf: pixbuf image
        @param srcx srcy: offset on pixbuf image
        @param dstx dsty: position on this pixmap
        @param w h: size of subpixbuf
        """

        _reload(pbuf)
        if (srcx < 0 or srcy < 0 or dstx < 0 or dsty < 0):
            return

        self.__pixmap.draw_pixbuf(self.__gc, pbuf, srcx, srcy, dstx, dsty, w, h)
        
        self.__to_buffer(dstx, dsty, w, h)
                                      

    def fit_pixbuf(self, pbuf, x, y, w, h):
        """
        Renders the given pixbuf so that it fits the given area. The pixbuf
        is scaled while retaining the original aspect ratio.
        
        @param pbuf: pixbuf image
        @param x y w h: constraining area to fit pixbuf into
        """

        _reload(pbuf)
        pbuf_width = pbuf.get_width()
        pbuf_height = pbuf.get_height()

        sx = w / float(pbuf_width)
        sy = h / float(pbuf_height)

        scale = min(sx, sy)
        offx = (w - pbuf_width * scale) / 2
        offy = (h - pbuf_height * scale) / 2
        
        if (_HAVE_CAIRO):
            fmt = pbuf.get_has_alpha() and cairo.FORMAT_ARGB32 \
                                        or cairo.FORMAT_RGB24
            surface = cairo.ImageSurface(fmt, pbuf_width, pbuf_height)
            gdkctx = gtk.gdk.CairoContext(self.__cairo_ctx)
            gdkctx.save()
            gdkctx.translate(int(x + offx), int(y + offy))
            gdkctx.scale(scale, scale)
            gdkctx.set_source_pixbuf(pbuf, 0, 0)
            gdkctx.paint()
            gdkctx.restore()
        
        else:
            self.draw_pixbuf(pbuf, int(x + offx), int(y + offy),
                             int(pbuf_width * scale), int(pbuf_height * scale),
                             scale = True)

        self.__to_buffer(x, y, w, h)



    def draw_pixmap(self, pmap, x, y):
        """
        Draws the given pixmap.
        
        @param pmap: pixmap
        @param x y: coordinates
        """
    
        w, h = pmap.get_size()
        self.copy_pixmap(pmap, 0, 0, x, y, w, h)


    def __split_frame(self, img):
    
        w, h = img.get_width(), img.get_height()
        w3 = w / 3
        h3 = h / 3

        tl = img.subpixbuf(0, 0, 10, 10)
        t = img.subpixbuf(10, 0, w - 20, 10)
        tr = img.subpixbuf(w - 10, 0, 10, 10)
        r = img.subpixbuf(w - 10, 10, 10, h - 20)
        br = img.subpixbuf(w - 10, h - 10, 10, 10)
        b = img.subpixbuf(10, h - 10, w - 20, 10)
        bl = img.subpixbuf(0, h - 10, 10, 10)
        l = img.subpixbuf(0, 10, 10, h - 20)
        c = img.subpixbuf(10, 10, w - 20, h - 20)

        #tl = img.subpixbuf(0, 0, w3, h3)
        #t = img.subpixbuf(w3, 0, w3, h3)
        #tr = img.subpixbuf(w - w3, 0, w3, h3)
        #r = img.subpixbuf(w - w3, h3, w3, h3)
        #br = img.subpixbuf(w - w3, h - h3, w3, h3)
        #b = img.subpixbuf(w3, h - h3, w3, h3)
        #bl = img.subpixbuf(0, h - h3, w3, h3)
        #l = img.subpixbuf(0, h3, w3, h3)
        #c = img.subpixbuf(w3, h3, w3, h3)

        return (tl, t, tr, r, br, b, bl, l, c) 


    def draw_frame(self, framepbuf, x, y, w, h, filled, parts = 0xf):
        """
        Draws a frame by stretching and tiling the given pixbuf.
        
        @param framepbuf: pixbuf to use for the frame
        @param x y w h: frame position and size
        @param filled: whether to fill the frame or only draw the border
        @param parts: bit composition of parts to draw (C{Pixbuf.TOP | Pixbuf.BOTTOM | Pixbuf.LEFT | Pixbuf.RIGHT})
        """

        _reload(framepbuf)
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
        
        @param pmap: source pixmap
        @param srcx srcy: offset on source pixmap
        @param dstx dsty: position on this pixmap
        @param w h: size of area to copy
        """
    
        self.__pixmap.draw_drawable(self.__gc, pmap._get_pixmap(),
                                    srcx, srcy, dstx, dsty, w, h)

        
        if (self.__buffer):
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

        @param pmap: source pixmap
        @param srcx srcy: offset on source pixmap
        @param dstx dsty: position on this pixmap
        @param w h: size of area to copy        
        """
    
        if (pmap.is_buffered()):
            self.__pixmap.draw_drawable(self.__gc, pmap._get_buffer(),
                                        srcx, srcy, dstx, dsty, w, h)
            if (self.__buffer):
                self.__buffer.draw_drawable(self.__buffer_gc, pmap._get_buffer(),
                                            srcx, srcy, dstx, dsty, w, h)
        else:
            self.copy_pixmap(pmap, srcx, srcy, dstx, dsty, w, h)
            


    def restore(self, x, y, w, h):
        """
        Restores the given area from buffer, if this pixmap is buffered.
        Otherwise, it does nothing.
        
        @param x y w h: area to restore
        """
    
        if (not self.__buffer): return
        
        self.__pixmap.draw_drawable(self.__gc, self.__buffer,
                                    x, y, x, y, w, h)


screen_size = max(gtk.gdk.screen_width(), gtk.gdk.screen_height())
TEMPORARY_PIXMAP = Pixmap(None, screen_size, screen_size)
"""
The temporary pixmap can be used for temporary drawing operations without
having to create a new pixmap.
When using it, make sure that no other code can interfere.
"""

