from utils.Observable import Observable
from ui.Pixmap import Pixmap
from ui.Widget import Widget
from ui.ImageButton import ImageButton
import theme


class WindowControls(Widget, Observable):

    OBS_MINIMIZE_WINDOW = 0
    OBS_CLOSE_WINDOW = 1


    def __init__(self):        
    
        self.__buffer = None
        
    
        Widget.__init__(self)
        
        btn_minimize = ImageButton(theme.window_minimize_1,
                                   theme.window_minimize_2)
        btn_minimize.set_size(80, 80)
        btn_minimize.set_pos(10, 0)
        self.add(btn_minimize)
        btn_minimize.connect(btn_minimize.EVENT_BUTTON_RELEASE,
                     lambda x,y:self.update_observer(self.OBS_MINIMIZE_WINDOW))

        btn_close = ImageButton(theme.window_close_1,
                                theme.window_close_2)
        btn_close.set_size(80, 80)
        btn_close.set_pos(110, 0)
        self.add(btn_close)
        btn_close.connect(btn_minimize.EVENT_BUTTON_RELEASE,
                     lambda x,y:self.update_observer(self.OBS_CLOSE_WINDOW))

        

    def set_size(self, w, h):
    
        self.__buffer = Pixmap(None, w, h)
        Widget.set_size(self, w, h)        
        
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.draw_frame(theme.panel, x, y, w, h, True,
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
        
