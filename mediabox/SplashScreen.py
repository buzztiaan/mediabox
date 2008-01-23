from ui.Widget import Widget
from ui.Label import Label
import values
import theme

import gtk


class SplashScreen(Widget):

    def __init__(self, esens):
       
        Widget.__init__(self, esens)
        self.set_size(800, 480)

        label = Label(esens,
                      "Loading Components...",
                      theme.font_plain, theme.color_fg_splash)
        self.add(label)
        label.set_pos(10, 320)
        label.set_size(780, 0)
        label.set_alignment(label.CENTERED)

        label = Label(esens,
                      "ver %s - %s" \
                      % (values.VERSION, values.COPYRIGHT),
                      theme.font_tiny, theme.color_fg_splash)
        self.add(label)
        label.set_pos(10, 450)
        label.set_size(390, 0)
        label.set_alignment(label.LEFT)
        
        label = Label(esens,
                      "http://mediabox.garage.maemo.org",
                      theme.font_tiny, theme.color_fg_splash)
        self.add(label)
        label.set_pos(400, 450)
        label.set_size(390, 0)
        label.set_alignment(label.RIGHT)
        
      
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
      
        screen.fill_area(0, 0, w, h, theme.color_bg_splash)
        #screen.draw_pixbuf(theme.background, 0, 0)
        screen.draw_pixbuf(theme.logo,
                           (800 - theme.logo.get_width()) / 2,
                           (320 - theme.logo.get_height()) / 2)

