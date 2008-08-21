from com import Configurator, msgs
import theme


class HeadsetControlPrefs(Configurator):

    TITLE = "Headset Control"


    def __init__(self):
        
        Configurator.__init__(self)

        # TODO: implement
        
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, theme.color_bg)
                
