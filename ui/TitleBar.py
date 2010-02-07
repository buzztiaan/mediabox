from Widget import Widget
from ImageButton import ImageButton
from Pixmap import TEMPORARY_PIXMAP
from theme import theme


class TitleBar(Widget):
    """
    Title bar widget for Maemo4.
    """


    EVENT_SWITCH = "event-switch"
    EVENT_CLOSE = "event-close"
    EVENT_MENU = "event-menu"
    

    def __init__(self):
    
        self.__title = ""
    
        Widget.__init__(self)
        self.connect_clicked(lambda *a:self.emit_event(self.EVENT_MENU))
        
        self.__btn_switch = ImageButton(theme.btn_window_switch_1,
                                        theme.btn_window_switch_2)
        self.add(self.__btn_switch)

        self.__btn_close = ImageButton(theme.btn_window_close_1,
                                       theme.btn_window_close_2)
        self.__btn_close.connect_clicked(
                                   lambda *a:self.emit_event(self.EVENT_CLOSE))
        self.add(self.__btn_close)


    def connect_switch(self, cb, *args):
    
        self._connect(self.EVENT_SWITCH, cb, *args)
        
        
    def connect_close(self, cb, *args):
    
        self._connect(self.EVENT_CLOSE, cb, *args)
        
        
    def connect_menu(self, cb, *args):
    
        self._connect(self.EVENT_MENU, cb, *args)
        
        
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
        
        screen.draw_frame(theme.titlebar_bg, x, y, w, h, True,
                          screen.BOTTOM)
        screen.draw_pixbuf(theme.window_menu, x + 80, 7)
        self.__btn_switch.set_geometry(0, 0, 80, 57)
        self.__btn_close.set_geometry(w - 80, 0, 80, 57)

        screen.draw_text(self.__title,
                         theme.font_ui_titlebar,
                         x+ 80 + 50, y + 10,
                         theme.color_ui_titlebar)

