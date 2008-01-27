from ui.Widget import Widget
from ui.Label import Label
from ui.Pixmap import Pixmap
import values
import theme

import gtk


class Thumbnailer(Widget):

    def __init__(self, esens):
    
        self.__buffer = Pixmap(None, 160, 120)
        self.__bg = Pixmap(None, 160, 120)
    
        Widget.__init__(self, esens)
        self.set_size(800, 400)
       
        self.__label = Label(esens, "", theme.font_tiny, theme.color_fg_item)
        self.add(self.__label)
        self.__label.set_alignment(self.__label.RIGHT)
        self.__label.set_size(780, 0)
        self.__label.set_pos(10, 10)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
                
        screen.draw_pixbuf(theme.background, x, y)

        # save background
        self.__bg.copy_buffer(screen, 400 - 80, 200 - 60, 0, 0, 160, 120)
        
        
    def clear(self):
    
        self.__label.set_text("")

      
               
    def show_thumbnail(self, thumburi, uri):

        self.__label.set_text(uri)
        
        screen = self.get_screen()
        try:
            pbuf = gtk.gdk.pixbuf_new_from_file(thumburi)
        except:
            return

        w, h = pbuf.get_width(), pbuf.get_height()
        self.__buffer.copy_pixmap(self.__bg, 0, 0, 0, 0, 160, 120)
        self.__buffer.draw_pixbuf(pbuf, (160 - w) / 2, (120 - h) / 2)
        screen.copy_pixmap(self.__buffer, 0, 0, 400 - 80, 200 - 60, 160, 120)

        del pbuf
        while (gtk.events_pending()): gtk.main_iteration()

