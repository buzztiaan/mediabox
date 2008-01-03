from Widget import Widget
from Label import Label

import gtk
import pango
import theme


class ProgressBar(Widget):
    """
    Class for a progress bar with a text label.
    """
    
    def __init__(self, esens):

        self.__progress = 0
        self.__progress_width = 0        
        w, h = (theme.progress.get_width(), theme.progress.get_height())
        
        Widget.__init__(self, esens)
        self.set_size(w, 80)
        
        self.__label = Label(esens, "", theme.font_tiny,
                             theme.color_fg_panel_text)
        self.add(self.__label)
        self.__label.set_pos(0, 0)
        self.__label.set_size(w, 0)
        
        self.__pos_label = Label(esens, "", theme.font_tiny,
                                 theme.color_fg_panel_text)
        self.add(self.__pos_label)
        self.__pos_label.set_pos(0, 24 + h)
        self.__pos_label.set_size(50, 0)
        
        self.__total_label = Label(esens, "", theme.font_tiny,
                                   theme.color_fg_panel_text)
        self.add(self.__total_label)
        self.__total_label.set_pos(w - 100, 24 + h)
        self.__total_label.set_size(100, 0)
        self.__total_label.set_alignment(self.__total_label.RIGHT)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y + 24, w, 32, "#000000")
        screen.draw_subpixbuf(theme.progress, 0, 0, x, y + 24,
                              self.__progress_width, 32)

        

    def set_position(self, pos, total):

        if (not self.may_render()):
            return

        self.__progress = pos
        if (total == 0): return

        pos_m = pos / 60
        pos_s = pos % 60
        total_m = total / 60
        total_s = total % 60      
        
        w, h = self.get_size()
        percent = min(pos / float(total), 1.0)
        width = int(w * percent)
        
        x1 = min(width, self.__progress_width)
        x2 = max(width, self.__progress_width)

        x, y = self.get_screen_pos()
        w, h = self.get_size()        
        screen = self.get_screen()

        screen.draw_subpixbuf(theme.progress, 0, 0, x, y + 24,
                              width, 32)
        screen.fill_area(x + width, y + 24, w - width, 32, "#000000")

        self.__pos_label.set_text("%d:%02d" % (pos_m, pos_s))
        self.__total_label.set_text("%d:%02d" % (total_m, total_s))

        self.__progress_width = width
        
        


    def set_value(self, value, unit):
    
        self.__total_label.set_text("%03.2f %s" % (value, unit))



    def set_title(self, title):
        
        self.__label.set_text(title)
        
