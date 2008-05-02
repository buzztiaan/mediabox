from ui.Widget import Widget
from ui.Pixmap import Pixmap
from ui.Label import Label

import gtk
import time
import theme


_WIDTH = 280
_HEIGHT = 40


class ThrobberDialog(Widget):

    def __init__(self, esens):

        self.__last_rotate = 0
    
        # throbber pixbuf
        self.__throbber = None
        self.__throbber_width = 0
        self.__throbber_height = 0
        
        # number of frames in throbber animation
        self.__number_of_frames = 0
        self.__current_frame = 0
        
        self.__save_under = Pixmap(None, _WIDTH, _HEIGHT)
        self.__buffer = Pixmap(None, _WIDTH, _HEIGHT)        
    
    
        Widget.__init__(self, esens)
        self.set_size(_WIDTH, _HEIGHT)

        self.__label = Label(esens, "", theme.font_plain,
                             theme.color_fg_panel_text)
        self.__label.set_alignment(self.__label.CENTERED)
        self.__label.set_pos(10, 10)
        self.__label.set_size(_WIDTH - 20, 0)
        self.add(self.__label)
        
        
    def set_throbber(self, throbber):

        self.__throbber = throbber
        self.__throbber_height = throbber.get_height()
        self.__throbber_width = self.__throbber_height
        self.__current_frame = 0
        self.__number_of_frames = throbber.get_width() / self.__throbber_width

        w, h = self.get_size()
        h = self.__throbber_height + 60
        self.set_size(w, h)

        self.__label.set_pos(10, self.__throbber_height + 20)

        self.__save_under = Pixmap(None, w, h)
        self.__buffer = Pixmap(None, w, h)


    def set_text(self, text):
    
        self.__label.set_text(text)


    def render_this(self):

        parent = self.get_parent()
        px, py = parent.get_screen_pos()
        pw, ph = parent.get_size()
        
        w, h = self.get_size()
        screen = self.get_screen()
        
        x = (pw - w) / 2
        y = (ph - h) / 2
        self.set_pos(x, y)

        x, y = self.get_screen_pos()

        screen.draw_frame(theme.panel, x, y, w, h, True)

        self.__save_under.copy_buffer(screen, x, y, 0, 0, w, h)
        self.__render_current()
            
        
        
    def __render_current(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        self.__buffer.copy_pixmap(self.__save_under, 0, 0, 0, 0, w, h)

        if (self.__throbber):
            tx = (w - self.__throbber_width) / 2
            ty = 10

            frame_offset = self.__current_frame * self.__throbber_width
            self.__buffer.draw_subpixbuf(self.__throbber, frame_offset, 0, 
                         tx, ty, self.__throbber_width, self.__throbber_height)
        
        if (self.may_render()):
            screen.copy_pixmap(self.__buffer, tx, ty, x + tx, y + ty,
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
        
        
    def set_visible(self, value):
    
        if (not value): time.sleep(0.25)
        self.set_events_blocked(value)
        Widget.set_visible(self, value)
        
