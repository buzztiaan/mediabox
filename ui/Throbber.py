from Widget import Widget
from Pixmap import Pixmap
from Label import Label

import gtk
import time
from theme import theme


class Throbber(Widget):

    def __init__(self, throbber):
    
        self.__last_rotate = 0
    
        Widget.__init__(self)
        
        self.__throbber = throbber
        self.__throbber_height = throbber.get_height()
        self.__throbber_width = self.__throbber_height
        self.__current_frame = 0
        self.__number_of_frames = throbber.get_width() / self.__throbber_width
        self.__buffer = None #Pixmap(None,
                              # self.__throbber_width, self.__throbber_height)
        self.__bg = None #Pixmap(None, self.__throbber_width, self.__throbber_height)
                               

        self.set_size(self.__throbber_width, self.__throbber_height)
        
        
        self.__label = Label(esens, "", theme.font_mb_plain, "#000000")
        self.__label.set_alignment(self.__label.CENTERED)
        self.__label.set_pos(10, self.__throbber_height + 20)
        self.__label.set_size(self.__throbber_width - 20, 0)
        self.add(self.__label)
      

    def __prepare_throbber(self):

        w, h = self.get_size()

        from theme import theme
        self.__bg.draw_frame(theme.mb_frame_image, 0, 0, w, h, True)
        self.__bg.draw_text("Loading...", theme.font_mb_plain,
                            10, self.__throbber_height + 20,
                            "#000000")
    
        
               
        
    def render_this(self):
        
        parent = self.get_parent()
        px, py = parent.get_screen_pos()
        pw, ph = parent.get_size()
        
        w, h = self.get_size()
        screen = self.get_screen()
        
        x = px + (pw - w) / 2
        y = py + (ph - h) / 2
                
        if (not self.__buffer):
            self.__buffer = Pixmap(None, w, h)
            self.__bg = Pixmap(None, w, h)
        
        self.__bg.copy_buffer(screen, x, y, 0, 0, w, h)
        self.__prepare_throbber()

        self.__render_current()
        
        
    def __render_current(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        tx = self.__current_frame * self.__throbber_width
        self.__buffer.copy_pixmap(self.__bg, 0, 0, 0, 0, w, h)

        self.__buffer.draw_subpixbuf(self.__throbber, tx, 0, 10, 10,
                                self.__throbber_width, self.__throbber_height)

        if (self.may_render()):
            #x += (w - self.__throbber_width) / 2
            #y += 10 #(h - self.__throbber_height) / 2
            screen.copy_pixmap(self.__buffer, 0, 0, x, y, w, h)
                               
                               
    def rotate(self):
    
        now = time.time()
        if (now - self.__last_rotate > 0.05):    
            self.__render_current()
            self.__current_frame += 1
            self.__current_frame %= self.__number_of_frames
            while(gtk.events_pending()): gtk.main_iteration()
        
            self.__last_rotate = now
        #end if
