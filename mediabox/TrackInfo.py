from ui.Widget import Widget
from ui.Label import Label
from ui.Pixmap import Pixmap
import theme

import gtk
import gobject
import threading


_COVER_SIZE = 304


class TrackInfo(Widget):

    def __init__(self, esens):
    
        self.__cover = None
    
        Widget.__init__(self, esens)
        self.set_size(800, 400)
        
        self.__title = Label(esens, "-", theme.font_headline, "#000000")
        self.add(self.__title)
        self.__title.set_pos(400, 48)
        self.__title.set_size(400 - 48, 0)

        self.__album = Label(esens, "-", theme.font_plain, "#000000")
        self.add(self.__album)
        self.__album.set_pos(448, 108)
        self.__album.set_size(400 - 96, 0)

        self.__artist = Label(esens, "-", theme.font_plain, "#000000")
        self.add(self.__artist)
        self.__artist.set_pos(448, 148)
        self.__artist.set_size(400 - 96, 0)
        

    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.draw_subpixbuf(theme.background, 0, 0, 0, 0, w, h)
        screen.draw_rect(x + 46, y + 46, _COVER_SIZE + 4, _COVER_SIZE + 4,
                        "#000000")

        if (self.__cover):
            screen.draw_pixbuf(self.__cover, x + 48, y + 48)
        else:
            screen.fill_area(x + 48, y + 48, _COVER_SIZE, _COVER_SIZE,
                             "#aaaaaa")
        
        screen.draw_pixbuf(theme.viewer_music_album, 400, 108)
        screen.draw_pixbuf(theme.viewer_music_artist, 400, 148) 

               
    def __escape_entities(self, s):
    
        return s.replace("<", "&lt;") \
                .replace(">", "&gt;") \
                .replace("&", "&amp;")


    def set_cover(self, cover):

        try:
            pbuf = gtk.gdk.pixbuf_new_from_file(cover)    
        except:
            pbuf = theme.viewer_music_unknown
            
        scaled = pbuf.scale_simple(_COVER_SIZE, _COVER_SIZE, gtk.gdk.INTERP_BILINEAR)
        self.__cover = scaled
        
        del pbuf
        del scaled
        self.render()
        
        
    def set_title(self, title):
    
        self.__title.set_text(title)
        
        
    def set_info(self, album, artist):
    
        album = self.__escape_entities(album)
        artist = self.__escape_entities(artist)
        self.__album.set_text(album or "-")
        self.__artist.set_text(artist or "-")


    def fx_uncover(self, wait = True):
    
        STEP = 20
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        buf = Pixmap(None, w, h)
        self.render_at(buf)
        finished = threading.Event()

        def f(i):
            if (i < 180):
                screen.copy_pixmap(screen, STEP, 0, 0, 0, 180 - i - STEP, h)
                screen.copy_pixmap(buf, 180 - i - STEP, 0, 180 - i - STEP, 0, STEP, h)

            screen.copy_pixmap(screen, 180 + i, 0, 180 + i + STEP, 0, 620 - i, h)
            screen.copy_pixmap(buf, 180 + i, 0, 180 + i, 0, STEP, h)

            if (i < 620 - STEP):
                gobject.timeout_add(5, f, i + STEP)
            else:
                finished.set()    

        f(0)
        while (wait and not finished.isSet()): gtk.main_iteration()



    def fx_fade_in(self, wait = True):
    
        STEP = 16
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        buf = Pixmap(None, w, h)
        self.render_at(buf)
        dst_pbuf = screen.render_on_pixbuf()
        pbuf = buf.render_on_pixbuf()
        finished = threading.Event()
        
        def f(i, pbuf, dst_pbuf):
            i = min(255, i)
            pbuf.composite(dst_pbuf, 0, 0, w, h, 0, 0, 1, 1,
                           gtk.gdk.INTERP_NEAREST, i)
            screen.draw_subpixbuf(dst_pbuf, 0, 0, 0, 0, w, h)
            if (i < 255):
                gobject.timeout_add(50, f, i + STEP, pbuf, dst_pbuf)
            else:
                finished.set()
                del pbuf
                del dst_pbuf
                
        f(32, pbuf, dst_pbuf)
        while (wait and not finished.isSet()): gtk.main_iteration()
        
