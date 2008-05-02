from ui.Widget import Widget
from ui.Label import Label
from ui.Pixmap import Pixmap, TEMPORARY_PIXMAP
import theme

import gtk
import gobject
import threading


_COVER_SIZE = 304


class TrackInfo(Widget):

    def __init__(self, esens):
    
        self.__cover = None
        self.__buffer = TEMPORARY_PIXMAP #Pixmap(None, 758, 400)
    
        Widget.__init__(self, esens)
        
        self.__title = Label(esens, "-", theme.font_headline,
                             theme.color_fg_trackinfo)
        self.add(self.__title)
        self.__title.set_geometry(400, 34, 400 - 48, 0)

        self.__album = Label(esens, "-", theme.font_plain,
                             theme.color_fg_trackinfo)
        self.add(self.__album)
        self.__album.set_geometry(448, 94, 400 - 96, 0)

        self.__artist = Label(esens, "-", theme.font_plain,
                              theme.color_fg_trackinfo)
        self.add(self.__artist)
        self.__artist.set_geometry(448, 134, 400 - 96, 0)
        

    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        #self.__buffer.draw_subpixbuf(theme.background, 0, 0, 0, 0, w, h)
        self.__buffer.fill_area(x, y, w, h, theme.color_bg)
        self.__buffer.draw_frame(theme.viewer_music_frame,
                                 x + 45, y + 29,
                                 _COVER_SIZE + 11, _COVER_SIZE + 11,
                                 True)
 
        if (self.__cover):
            self.__buffer.draw_pixbuf(self.__cover, x + 48, y + 32)
        #else:
            #self.__buffer.fill_area(x + 48, y + 28, _COVER_SIZE, _COVER_SIZE,
            #                        "#000000")
        
        self.__buffer.draw_pixbuf(theme.viewer_music_album, x + 400, y + 92)
        self.__buffer.draw_pixbuf(theme.viewer_music_artist, x + 400, y + 132)
        
        screen.copy_pixmap(self.__buffer, x, y, x, y, w, h)

               

    def set_cover(self, cover):

        if (not cover): cover = theme.viewer_music_unknown
        
        scaled = cover.scale_simple(_COVER_SIZE, _COVER_SIZE, gtk.gdk.INTERP_BILINEAR)
        self.__cover = scaled
        
        del cover
        del scaled
        #self.render()
        
        
    def set_title(self, title):
    
        self.__title.set_text(title)
        
        
    def set_info(self, album, artist):
    
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
        
