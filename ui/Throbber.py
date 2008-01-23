from Widget import Widget
from Pixmap import Pixmap

import gtk
import time


class Throbber(Widget):

    def __init__(self, esens, throbber):
    
        self.__last_rotate = 0
    
        Widget.__init__(self, esens)
        
        self.__throbber = throbber
        self.__throbber_height = throbber.get_height()
        self.__throbber_width = self.__throbber_height
        self.__current_frame = 0
        self.__number_of_frames = throbber.get_width() / self.__throbber_width
        self.__buffer = Pixmap(None,
                               self.__throbber_width, self.__throbber_height)
        self.__bg = Pixmap(None, self.__throbber_width, self.__throbber_height)
                               

        self.set_size(self.__throbber_width, self.__throbber_height)
               
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        x += (w - self.__throbber_width) / 2
        y += (h - self.__throbber_height) / 2
        
        self.__bg.copy_buffer(screen, x, y, 0, 0,
                              self.__throbber_width, self.__throbber_height)
        
        self.__render_current()
        
        
    def __render_current(self):

        tx = self.__current_frame * self.__throbber_width
        self.__buffer.copy_pixmap(self.__bg, 0, 0, 0, 0,
                                  self.__throbber_width, self.__throbber_height)
        self.__buffer.draw_subpixbuf(self.__throbber, tx, 0, 0, 0,
                                self.__throbber_width, self.__throbber_height)

        if (self.may_render()):
            x, y = self.get_screen_pos()
            w, h = self.get_size()
            screen = self.get_screen()

            x += (w - self.__throbber_width) / 2
            y += (h - self.__throbber_height) / 2
            screen.copy_pixmap(self.__buffer, 0, 0, x, y,
                               self.__throbber_width, self.__throbber_height)
                               
                               
    def rotate(self):
    
        now = time.time()
        if (now - self.__last_rotate > 0.05):    
            self.__render_current()
            self.__current_frame += 1
            self.__current_frame %= self.__number_of_frames
            while(gtk.events_pending()): gtk.main_iteration()
        
            self.__last_rotate = now
        #end if
