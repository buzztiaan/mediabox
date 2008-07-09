from Widget import Widget
#from Label import Label
import theme

import gtk


class ProgressBar(Widget):
    """
    Class for a progress bar.
    """
    
    def __init__(self, show_time = True):

        self.__show_time = show_time
        
        self.__is_dragging = False
        
        self.__progress = 0
        self.__progress_width = 0        
        w, h = (theme.progress.get_width(), theme.progress.get_height())
        
        Widget.__init__(self)
        self.set_size(w, 80)
        
        self.connect_button_pressed(self.__on_button_press)
        self.connect_button_released(self.__on_button_release)
        self.connect_pointer_moved(self.__on_motion)
        
        
    def __on_button_press(self, px, py):
    
        self.__is_dragging = True


    def __on_button_release(self, px, py):
    
        self.__is_dragging = False


    def __on_motion(self, px, py):
            
        if (self.__is_dragging):
            px = max(0, px)
            w, h = self.get_size()
            self.set_position(px, w, dragged = True)


    def connect_changed(self, cb, *args):
      
        def f(px, py, *args):
            w, h = self.get_size()
            pos = max(0, min(99.9, px / float(w) * 100))
            cb(pos, *args)
      
        self.connect_button_released(f, *args)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y + 24, w, 32, "#000000")
        screen.draw_subpixbuf(theme.progress, 0, 0, x, y + 24,
                              self.__progress_width, 32)

        

    def set_position(self, pos, total, dragged = False):

        if (self.__is_dragging and not dragged): return
        if (pos == self.__progress): return
        if (not self.may_render()): return
        if (total == 0): return

        self.__progress = pos
        
        w, h = self.get_size()
        percent = min(pos / float(total), 1.0)
        width = int(w * percent)
        
        x1 = min(width, self.__progress_width)
        x2 = max(width, self.__progress_width)

        x, y = self.get_screen_pos()
        w, h = self.get_size()        
        screen = self.get_screen()

        if (self.__progress_width < width):
            screen.draw_subpixbuf(theme.progress, self.__progress_width, 0,
                                  x + self.__progress_width, y + 24,
                                  width - self.__progress_width, 32)
        else:
            screen.fill_area(x + width, y + 24,
                             self.__progress_width - width, 32, "#000000")
        #end if
        
        #if (self.__show_time):
        #    pos_m = pos / 60
        #    pos_s = pos % 60
        #    total_m = total / 60
        #    total_s = total % 60      
        #    self.__pos_label.set_text("%d:%02d" % (pos_m, pos_s))
        #    self.__total_label.set_text("%d:%02d" % (total_m, total_s))
        ##end if

        self.__progress_width = width
        
        


    #def set_value(self, value, unit):
    #
    #    self.__total_label.set_text("%03.2f %s" % (value, unit))



    #def set_title(self, title):
    #    
    #    self.__label.set_text(title)
        
