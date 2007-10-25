import gtk
import theme


class ProgressBar(gtk.DrawingArea):

    def __init__(self):
    
        self.__progress_width = 0
    
        gtk.DrawingArea.__init__(self)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.BUTTON_RELEASE_MASK)
        self.set_size_request(-1, 24)

        self.connect("expose-event", self.__on_expose)
        
        
        
    def __on_expose(self, src, ev):

        area = ev.area
        win = src.window
        w, h = win.get_size()
        
        x1 = area.x
        x2 = self.__progress_width
        x3 = area.x + area.width
        
        if (x1 < x2 < x3):
            win.draw_pixbuf(win.new_gc(), theme.progress,
                            x1, area.y, x1, area.y,
                            x2 - x1, area.height)
                
            win.draw_rectangle(win.new_gc(), True, x2, area.y,
                               x3 - x2, area.height)
        elif (x2 <= x1):
            win.draw_rectangle(win.new_gc(), True, area.x, area.y,
                               area.width, area.height)
        elif (x2 >= x3):
            win.draw_pixbuf(win.new_gc(), theme.progress,
                            area.x, area.y, area.x, area.y,
                            area.width, area.height)
                    


    def set_position(self, pos, total):

        if (not self.window or total == 0): return
        
        w, h = self.window.get_size()
        percent = pos / float(total)
        width = int(w * percent)
        
        x1 = min(width, self.__progress_width)
        x2 = max(width, self.__progress_width)
                        
        self.__progress_width = width
        self.queue_draw_area(x1, 0, x2, 24)

