from ui.Thumbnail import Thumbnail
from ui import pixbuftools
from mediabox import thumbnail

import gtk


class PlaylistThumbnail(Thumbnail):
    """
    Thumbnail for representing a playlist.
    """

    def __init__(self, pl):

        Thumbnail.__init__(self)
        self.set_caption(pl.get_name())


    def set_thumbnails(self, tns):
    
        tns.reverse()
        w, h = self.get_size()
        pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, w, h)
        pbuf.fill(0x00000000)        

        pos = [(10, 0), (30, 20), (50, 40), (70, 60)]
        for tn, mimetype in tns[:4]:
            tn_pbuf = thumbnail.render_on_pixbuf(tn, mimetype)

            x, y = pos.pop(0)            
            pixbuftools.draw_pbuf(pbuf, tn_pbuf, x, y, 70, 50)
        #end for
        
        self.set_thumbnail_pbuf(pbuf)
        del pbuf
        self.invalidate()
