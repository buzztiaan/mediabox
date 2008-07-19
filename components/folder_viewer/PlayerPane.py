from ui.Widget import Widget
from ui.ImageButton import ImageButton
import theme


class PlayerPane(Widget):

    EVENT_TOGGLED = "toggled"
    

    def __init__(self):
    
        self.__current_media_widget = None
    
        Widget.__init__(self)
        
        self.__toggle_btn = ImageButton(theme.item_btn_play, theme.item_btn_play)
        self.__toggle_btn.connect_clicked(lambda :self.send_event(self.EVENT_TOGGLED))
        self.add(self.__toggle_btn)
        
        
        
    def connect_toggled(self, cb, *args):
    
        self._connect(self.EVENT_TOGGLED, cb, *args)
        
        
        
    def get_controls(self):
    
        if (self.__current_media_widget):
            return self.__current_media_widget.get_controls()
        else:
            return None
        
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        if (w < 800):
            screen.fill_area(x, y, w, h, theme.color_bg)
        
            if (self.__current_media_widget):
               self.__current_media_widget.set_geometry(0, 0, w - 60, h)
               if (w < 100):
                   self.__current_media_widget.set_visible(False)
               else:
                   self.__current_media_widget.set_visible(True)
            self.__toggle_btn.set_pos(w - 60, (h - 60) / 2)
            self.__toggle_btn.set_visible(True)
            
        else:
            self.__current_media_widget.set_geometry(0, 0, w, h)
            self.__toggle_btn.set_visible(False)
        
        
    def set_media_widget(self, mw):
    
        if (self.__current_media_widget):
            self.remove(self.__current_media_widget)

        self.add(mw)       
        self.__current_media_widget = mw

