from ui.Widget import Widget

from utils.Observable import Observable
from ui.ImageButton import ImageButton
import theme



class Panel(Widget, Observable):

    OBS_NEXT_PANEL = 0
    

    def __init__(self, esens, with_next_button = True):
    
        self.__event_sensor = esens
        self.__has_next_button = with_next_button
        self.__button_pos = 10
    
        Widget.__init__(self, esens)
        self.set_size(800, 80)
        
        if (with_next_button):
            self.__btn_next_panel = ImageButton(esens,
                                            theme.btn_turn_1, theme.btn_turn_2)
            self.add(self.__btn_next_panel)
            self.__btn_next_panel.set_pos(10, 0)
            self.__btn_next_panel.connect(self.EVENT_BUTTON_RELEASE,
                                          lambda x,y:self._next_panel())
        

    def render_this(self):
    
        x, y = self.get_screen_pos()
        screen = self.get_screen()
    
        screen.draw_pixbuf(theme.panel, x, y)        
      


    def has_next_button(self):
    
        return self.__has_next_button
        
        
    def _next_panel(self):
    
        self.update_observer(self.OBS_NEXT_PANEL)
        
