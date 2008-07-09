from ui.Widget import Widget
import theme


class PlayerPane(Widget):

    def __init__(self):
    
        self.__current_media_widget = None
    
        Widget.__init__(self)
        
        
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, theme.color_bg)
        
        if (self.__current_media_widget):
           self.__current_media_widget.set_geometry(0, 0, w - 40, h)
           if (w < 100):
               self.__current_media_widget.set_visible(False)
           else:
               self.__current_media_widget.set_visible(True)
        
        screen.draw_pixbuf(theme.item_btn_play, x + w - 50, y + (h - 48) / 2)
        
        
    def set_media_widget(self, mw):
    
        if (self.__current_media_widget):
            self.remove(self.__current_media_widget)
    
        w, h = self.get_size()
    
        self.add(mw)
        
        self.__current_media_widget = mw

