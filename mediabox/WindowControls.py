from utils.Observable import Observable
from ui.Pixmap import Pixmap
from ui.Widget import Widget
from ui.ImageButton import ImageButton
import theme


class WindowControls(Widget, Observable):

    OBS_MINIMIZE_WINDOW = 0
    OBS_MAXIMIZE_WINDOW = 1
    OBS_CLOSE_WINDOW = 2


    def __init__(self):        
    
        self.__buffer = None
        
    
        Widget.__init__(self)
        
        x = 10
        for icon1, icon2, cmd in [(theme.window_minimize_1,
                                   theme.window_minimize_2,
                                   self.OBS_MINIMIZE_WINDOW),
                                  #(theme.window_minimize_1,
                                  # theme.window_minimize_2,
                                  # self.OBS_MAXIMIZE_WINDOW),                                   
                                  (theme.window_close_1,
                                   theme.window_close_2,
                                   self.OBS_CLOSE_WINDOW)]:
            btn = ImageButton(icon1, icon2)
            btn.set_geometry(x, 0, 80, 80)
            self.add(btn)
            btn.connect_clicked(self.update_observer, cmd)
            x += 100
        self.set_size(x, 80)
            
        

        

    def set_size(self, w, h):
    
        self.__buffer = Pixmap(None, w, h)
        Widget.set_size(self, w, h)        
        
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.draw_frame(theme.mb_panel, x, y, w, h, True,
                          screen.LEFT | screen.BOTTOM)
        
        
    def fx_slide_in(self, wait = True):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()        
        screen = self.get_screen()
        
        self.__buffer.copy_buffer(screen, x, y, 0, 0, w, h)
        self.render()
        
        
    def fx_slide_out(self, wait = True):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()        
        screen = self.get_screen()
        
        screen.copy_buffer(self.__buffer, 0, 0, x, y, w, h)
        
