from Widget import Widget
from ImageButton import ImageButton
from Pixmap import TEMPORARY_PIXMAP
from theme import theme
import platforms


class TitleBar(Widget):
    """
    Title bar widget for Maemo4.
    """


    EVENT_SWITCH = "event-switch"
    EVENT_CLOSE = "event-close"
    EVENT_MENU = "event-menu"
    
    MODE_NORMAL = 0
    MODE_SUBWINDOW = 1
    

    def __init__(self):
    
        self.__title = ""
        self.__mode = self.MODE_NORMAL
    
        Widget.__init__(self)
        self.connect_clicked(lambda *a:self.emit_event(self.EVENT_MENU))
        
        self.__btn_switch = ImageButton(theme.btn_window_switch_1,
                                        theme.btn_window_switch_2)
        self.__btn_switch.connect_clicked(
                                  lambda *a:self.emit_event(self.EVENT_SWITCH))
        self.add(self.__btn_switch)

        self.__btn_close = ImageButton(theme.btn_window_close_1,
                                       theme.btn_window_close_2)
        self.__btn_close.connect_clicked(
                                   lambda *a:self.emit_event(self.EVENT_CLOSE))
        self.add(self.__btn_close)

        self.__btn_back = ImageButton(theme.btn_window_back_1,
                                      theme.btn_window_back_2)
        self.__btn_back.connect_clicked(
                                   lambda *a:self.emit_event(self.EVENT_CLOSE))
        self.add(self.__btn_back)
        self.__btn_back.set_visible(False)


    def connect_switch(self, cb, *args):
    
        self._connect(self.EVENT_SWITCH, cb, *args)
        
        
    def connect_close(self, cb, *args):
    
        self._connect(self.EVENT_CLOSE, cb, *args)
        
        
    def connect_menu(self, cb, *args):
    
        self._connect(self.EVENT_MENU, cb, *args)
        
        
    def _reload(self):
    
        self.render()


    def set_mode(self, mode):
    
        self.__mode = mode
        self.render()

        
    def set_title(self, title):
    
        self.__title = title
        if (self.may_render()):
            self.render_buffered(TEMPORARY_PIXMAP)
        
        
    def render_this(self):
    
        x, y = 0, 0
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.draw_frame(theme.titlebar_bg, x, y, w, h, True)

        if (self.__mode == self.MODE_NORMAL):
            if (platforms.MEEGO_NETBOOK or platforms.MEEGO_WETAB):
                screen.draw_pixbuf(theme.window_menu, x, 7)
                self.__btn_close.set_geometry(w - 80, 0, 80, 57)
                self.__btn_switch.set_visible(False)
                self.__btn_back.set_visible(False)
                self.__btn_close.set_visible(True)

                screen.set_clip_rect(x + 50, y + 14, w - 80 - 50, 57)
                screen.draw_text(self.__title,
                                 theme.font_ui_titlebar,
                                 x + 50, y + 14,
                                 theme.color_ui_titlebar)
                screen.set_clip_rect()
                
            else:
                screen.draw_pixbuf(theme.window_menu, x + 80, 7)
                self.__btn_switch.set_geometry(0, 0, 80, 57)
                self.__btn_close.set_geometry(w - 80, 0, 80, 57)
                self.__btn_switch.set_visible(True)
                self.__btn_back.set_visible(False)
                self.__btn_close.set_visible(True)

                screen.set_clip_rect(x + 80 + 50, y + 14, w - 80 - 80 - 50, 57)
                screen.draw_text(self.__title,
                                 theme.font_ui_titlebar,
                                 x + 80 + 50, y + 14,
                                 theme.color_ui_titlebar)
                screen.set_clip_rect()
                
        elif (self.__mode == self.MODE_SUBWINDOW):
            if (platforms.MEEGO_NETBOOK or platforms.MEEGO_WETAB):
                screen.draw_pixbuf(theme.window_menu, x, 7)
                self.__btn_back.set_geometry(w - 80, 0, 80, 57)
                self.__btn_switch.set_visible(False)
                self.__btn_back.set_visible(True)
                self.__btn_close.set_visible(False)

                screen.set_clip_rect(x + 50, y + 14, w - 80 - 50, 57)
                screen.draw_text(self.__title,
                                 theme.font_ui_titlebar,
                                 x + 50, y + 14,
                                 theme.color_ui_titlebar)
                screen.set_clip_rect()
            
            else:
                screen.draw_pixbuf(theme.window_menu, x + 80, 7)
                self.__btn_switch.set_geometry(0, 0, 80, 57)
                self.__btn_back.set_geometry(w - 80, 0, 80, 57)
                self.__btn_switch.set_visible(True)
                self.__btn_back.set_visible(True)
                self.__btn_close.set_visible(False)

                screen.set_clip_rect(x + 80 + 50, y + 14, w - 80 - 80 - 50, 57)
                screen.draw_text(self.__title,
                                 theme.font_ui_titlebar,
                                 x + 80 + 50, y + 14,
                                 theme.color_ui_titlebar)
                screen.set_clip_rect()
