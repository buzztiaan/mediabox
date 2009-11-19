from ui.Widget import Widget
from ui.Label import Label
from theme import theme

import gtk


class NowPlaying(Widget):

    def __init__(self):
    
        # the file that is currently playing
        self.__current_file = None
        
        # the currently displayed icon pixbuf
        self.__icon = None
        
    
        Widget.__init__(self)
        
        self.__lbl_action = Label("", theme.font_mb_tiny, theme.color_mb_text)
        #self.add(self.__lbl_action)
        
        self.__lbl_title = Label("", theme.font_mb_plain, theme.color_mb_text)
        #self.add(self.__lbl_title)
        
        
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, theme.color_mb_background)
        
        icon_size = min(w, h)
        if (self.__icon):
            screen.fit_pixbuf(self.__icon, x, y + 80, icon_size, icon_size)
        
        screen.draw_pixbuf(theme.mb_btn_previous_1, x, y)
        screen.draw_pixbuf(theme.mb_btn_next_1, x, y + h - 80)
        
        #self.__lbl_action.set_pos(icon_size + 10, 12)
        #self.__lbl_title.set_pos(icon_size + 10, 40)



    def set_playing(self, icon, f):
    
        if (icon):
            if (self.__icon):
                del self.__icon
            try:
                self.__icon = gtk.gdk.pixbuf_new_from_file(icon)
            except:
                self.__icon = None
        #end if
    
        self.__lbl_title.set_text(f.name)
        self.render()


    def set_action(self, action):
    
        self.__lbl_action.set_text(action)

