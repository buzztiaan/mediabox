from com import Dialog
from mediabox import values
from theme import theme

import gtk


class AboutDialog(Dialog):

    def __init__(self):
    
        Dialog.__init__(self)

        w = gtk.gdk.screen_width()
        h = 200
        self.set_window_size(w, h)
        
        
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, theme.color_mb_background)
        screen.draw_centered_text(values.NAME + " " + values.VERSION,
                                  theme.font_mb_headline,
                                  x, h / 2 - 30, w, 30, theme.color_mb_text)
        screen.draw_centered_text(values.COPYRIGHT,
                                  theme.font_mb_plain,
                                  x, h / 2, w, 30, theme.color_mb_text)
        #screen.draw_centered_text("Tap here to access your media",
        #                          theme.font_mb_plain,
        #                          x, h - 80, w, 20, theme.color_mb_text)
        screen.fit_pixbuf(theme.mb_logo,
                          w - 120, h - 120, 120, 120)

