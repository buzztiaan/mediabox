from Widget import Widget
from Pixmap import TEMPORARY_PIXMAP
from theme import theme


class TitleBar(Widget):
    """
    Title bar widget for Maemo4.
    """

    def __init__(self):
    
        self.__title = ""
    
        Widget.__init__(self)
        
        
    def _reload(self):
    
        self.render()
        
        
    def set_title(self, title):
    
        self.__title = title
        if (self.may_render()):
            self.render_buffered(TEMPORARY_PIXMAP)
        
        
    def render_this(self):
    
        x, y = 0, 0
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, theme.color_mb_background)
        screen.draw_frame(theme.mb_panel, x, y, w, h, True,
                          screen.BOTTOM)
        screen.draw_pixbuf(theme.mb_btn_dir_up_1, w - 64, 0)

        screen.draw_text(self.__title,
                         theme.font_mb_headline,
                         10, 10,
                         theme.color_mb_text)

