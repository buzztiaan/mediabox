from ui.Widget import Widget
import theme


class ContentPane(Widget):

    def __init__(self, esens):
    
        Widget.__init__(self, esens)
        self.set_size(800, 400)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.draw_subpixbuf(theme.background, 0, 0, x, y, w, h)
        
