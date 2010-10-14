from Widget import Widget


class VideoScreen(Widget):
    """
    Video screen widget with a XID to be used by video backends.
    @since: 0.97
    """

    def __init__(self):
    
        self.__xid = 0
        self.__aspect_ratio = 15/9.0
    
        Widget.__init__(self)
        
        
    def get_xid(self):
        """
        Returns the XID of the video screen.
        
        @return: XID of the video screen X-window
        """
    
        if (not self.__xid):
            self.__xid = self.get_window().show_video_overlay(0, 0, 10, 10)
        
        return self.__xid


    def _visibility_changed(self):
    
        win = self.get_window()
        if (not win): return
        
        if (self.may_render()):
            pass
            #x, y = self.get_screen_pos()
            #w, h = self.get_size()
            #self.__xid = win.show_video_overlay(x, y, w, h)
            
        else:
            win.hide_video_overlay()
        #end if


    def set_aspect_ratio(self, ratio):
    
        print "setting aspect ratio", ratio
        self.__aspect_ratio = ratio
        self.render()


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        
        aspect = w / h
        w2 = self.__aspect_ratio * h
        h2 = w / self.__aspect_ratio
        
        if (w2 > w):
            y += (h - h2) / 2
            h = h2
        else:
            x += (w - w2) / 2
            w = w2
        
        self.__xid = self.get_window().show_video_overlay(x, y, w, h)

