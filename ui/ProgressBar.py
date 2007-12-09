import gtk
import pango
import theme


class ProgressBar(gtk.Layout):
    """
    Class for a progress bar with a text label.
    """
    
    def __init__(self):

        self.__progress = 0
        self.__progress_width = 0
        self.__gc = None
        self.__size = (theme.progress.get_width(), theme.progress.get_height())
        
        w, h = self.__size
        gtk.Layout.__init__(self)
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK)
        self.set_size_request(w, 80)

        # background
        bg = gtk.Image()
        bg.set_from_pixbuf(theme.panel_bg)
        bg.show()
        self.put(bg, 0, 0)
                
        # layout boxes
        vbox = gtk.VBox()
        vbox.set_size_request(w, 80)
        vbox.show()
        self.put(vbox, 0, 0)
        
        hbox = gtk.HBox(spacing = 12)
        hbox.show()
        vbox.pack_start(hbox, False, False, 6)
        
        # labels
        self.__title = gtk.Label("")
        self.__title.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        self.__title.set_alignment(0.0, 0.0)
        self.__title.modify_font(theme.font_plain)
        self.__title.modify_fg(gtk.STATE_NORMAL, theme.color_fg_panel_text)
        self.__title.show()
        hbox.pack_start(self.__title, True, True)

        self.__time = gtk.Label("-:-- / -:--")
        self.__time.modify_font(theme.font_plain)
        self.__time.modify_fg(gtk.STATE_NORMAL, theme.color_fg_panel_text)
        self.__time.show()
        hbox.pack_start(self.__time, False, False)
        
        # progress bar
        self.__bar = gtk.DrawingArea()        
        self.__bar.set_size_request(*self.__size)
        self.__bar.connect("expose-event", self.__on_expose)
        self.__bar.show()
        vbox.pack_start(self.__bar, False, False)

        
        
    def __on_expose(self, src, ev):
    
        area = ev.area
        win = src.window
        if (not self.__gc): self.__gc = win.new_gc()
                
        w, h = self.__size
        
        x1 = area.x
        x2 = self.__progress_width
        x3 = area.x + area.width
        
        if (x1 < x2 < x3):
            win.draw_pixbuf(self.__gc, theme.progress,
                            x1, area.y, x1, area.y,
                            x2 - x1, area.height)                
            win.draw_rectangle(self.__gc, True, x2, area.y,
                               x3 - x2, area.height)
                               
        elif (x2 <= x1):
            win.draw_rectangle(self.__gc, True, area.x, area.y,
                               area.width, area.height)
        elif (x2 >= x3):
            win.draw_pixbuf(self.__gc, theme.progress,
                            area.x, area.y, area.x, area.y,
                            area.width, area.height)


    def set_position(self, pos, total):

        self.__progress = pos
        if (total == 0): return

        pos_m = pos / 60
        pos_s = pos % 60
        total_m = total / 60
        total_s = total % 60
        self.__time.set_text("%d:%02d / %d:%02d" % 
                             (pos_m, pos_s, total_m, total_s))            
        
        w, h = self.__size
        percent = pos / float(total)
        width = int(w * percent)
        
        x1 = min(width, self.__progress_width)
        x2 = max(width, self.__progress_width)
                        
        self.__progress_width = width
        self.__bar.queue_draw_area(x1, 0, x2, h)


    def set_value(self, value, unit):
    
        self.__time.set_text("%03.2f %s" % (value, unit))



    def set_title(self, title):
        
        self.__title.set_text(title)
