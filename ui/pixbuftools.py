import gtk


TOP = 1
BOTTOM = 2
LEFT = 4
RIGHT = 8



def _split_frame(img):

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


def draw_pbuf(pbuf1, pbuf2, x, y, w = -1, h = -1):

    if (w > 0 and h > 0):
        pbuf2 = pbuf2.scale_simple(w, h, gtk.gdk.INTERP_BILINEAR)
    else:
        w = pbuf2.get_width()
        h = pbuf2.get_height()
        
    subpbuf = pbuf1.subpixbuf(x, y, w, h)
    pbuf2.composite(subpbuf, 0, 0, w, h, 0, 0, 1, 1,
                    gtk.gdk.INTERP_NEAREST, 0xff)
    del subpbuf
    

def make_frame(pbuf, w, h, filled, parts = 0xf):

    """
    Draws a frame by stretching and tiling the given pixbuf.
    """

    tl, t, tr, r, br, b, bl, l, c = _split_frame(pbuf)
    w1, h1 = tl.get_width(), tl.get_height()
    w1 = min(w1, w / 3)
    h1 = min(h1, h / 3)
    w2 = w1
    h2 = h1

    if (not parts & TOP):
        h1 = 0
    if (not parts & BOTTOM):
        h2 = 0
    if (not parts & LEFT):
        w1 = 0
    if (not parts & RIGHT):
        w2 = 0

    new_pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, w, h)
    new_pbuf.fill(0x00000000)

    if (parts & TOP):        
        if (parts & LEFT):
            draw_pbuf(new_pbuf, tl, 0, 0)
        if (parts & RIGHT):
            draw_pbuf(new_pbuf, tr, w - w2, 0)
    if (parts & BOTTOM):
        if (parts & LEFT):
            draw_pbuf(new_pbuf, bl, 0, h - h2)
        if (parts & RIGHT):
            draw_pbuf(new_pbuf, br, w - w2, h - h2)
    
    if (parts & TOP):
        draw_pbuf(new_pbuf, t, w1, 0, w - w1 - w2, h1)
        #self.draw_pixbuf(t, x + w1, y, w - w1 - w2, h1, True)
    if (parts & BOTTOM):
        draw_pbuf(new_pbuf, b, w1, h - h2, w - w1 - w2, h2)
        #self.draw_pixbuf(b, x + w1, y + h - h2, w - w1 - w2, h2, True)
    if (parts & LEFT):
        draw_pbuf(new_pbuf, l, 0, h1, w1, h - h1 - h2)
        #self.draw_pixbuf(l, x, y + h1, w1, h - h1 - h2, True)
    if (parts & RIGHT):
        draw_pbuf(new_pbuf, r, w - w2, h1, w2, h - h1 - h2)
        #self.draw_pixbuf(r, x + w - w2, y + h1, w2, h - h1 - h2, True)

    if (filled):
        draw_pbuf(new_pbuf, c, w1, h1, w - w1 - w2, h - h1 - h2)
        #self.draw_pixbuf(c, x + w1, y + h1, w - w1 - w2, h - h1 - h2, True)  

    return new_pbuf
