from Widget import Widget

import gtk


class VideoScreen(Widget):
    """
    Video screen widget with a XID to be used by video backends.
    @since: 0.97
    """

    def __init__(self):
    
        self.__layout = None
        
    
        Widget.__init__(self)
        
        # video screen
        self.__screen = gtk.DrawingArea()
        self.__screen.set_double_buffered(False)
        self.__screen.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#000000"))
        self.__screen.connect("expose-event", self.__on_expose)
        self.__screen.set_events(gtk.gdk.BUTTON_PRESS_MASK |
                                 gtk.gdk.BUTTON_RELEASE_MASK |
                                 gtk.gdk.POINTER_MOTION_MASK |
                                 gtk.gdk.KEY_PRESS_MASK |
                                 gtk.gdk.KEY_RELEASE_MASK)

        scr = self.__screen.get_screen()
        cmap = scr.get_rgb_colormap()
        self.__screen.set_colormap(cmap)
  

    def __on_expose(self, src, ev):

        win = self.__screen.window
        gc = win.new_gc()
        cmap = win.get_colormap()
        gc.set_foreground(cmap.alloc_color("#000000"))
        x, y, w, h = ev.area

        
    def get_xid(self):
        """
        Returns the XID of the video screen.
        
        @return: XID of the video screen X-window
        """
    
        if (not self.__screen.window):
            self.__layout = self.get_window().get_native_window() \
                            .get_gtk_layout()
            self.__layout.put(self.__screen, 0, 0)
            self.__screen.realize()
            
        return self.__screen.window.xid


    def _visibility_changed(self):
    
        if (self.may_render()):
            self.__screen.show()
        else:
            self.__screen.hide()
        #end if
        

    def render_this(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        self.__screen.set_size_request(w, h)
        self.__screen.show()
        print "VIDEO", x, y, w, h

        if (self.__layout):
            self.__layout.move(self.__screen, x, y)

