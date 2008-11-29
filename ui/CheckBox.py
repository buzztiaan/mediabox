"""
A checkbox widget.
"""

from Widget import Widget
import theme


_CHECK_WIDTH = theme.mb_checked.get_width() + 8
_CHECK_HEIGHT = theme.mb_checked.get_height()

class CheckBox(Widget):
    """
    Widget for checking items.
    """

    EVENT_CHECKED = "event-checked"
    

    def __init__(self, is_checked = False):
    
        self.__is_checked = is_checked
        self.__user_may_uncheck = True
    
        Widget.__init__(self)
        self.connect_clicked(self.__on_click)
        
        
    def __on_click(self):
    
        if (not self.__is_checked or self.__user_may_uncheck):
            self.set_checked(not self.__is_checked)


    def get_size(self):
    
        children = self.get_children()
        if (not children):
            return (0, 0)
        else:
            child = children[0]
            c_w, c_h = child.get_physical_size()
            return (c_w + _CHECK_WIDTH,
                    max(c_h, _CHECK_HEIGHT))
       
        
    def render_this(self):
    
        children = self.get_children()
        if (not children):
            return
        
        if (self.__is_checked):
            offx = _CHECK_WIDTH
        else:
            offx = 0
            
        child = children[0]
        child.set_pos(offx, 0)

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, theme.color_mb_background)
        if (self.__is_checked):
            screen.draw_pixbuf(theme.mb_checked, x, y)
        
        
    def lock_unchecking(self):
    
        self.__user_may_uncheck = False
        

    def set_checked(self, value):
    
        if (value != self.__is_checked):
            self.__is_checked = value
            self.render()
            self.send_event(self.EVENT_CHECKED, value)
        
        
    def is_checked(self):
    
        return self.__is_checked


    def connect_checked(self, cb, *args):
    
        self._connect(self.EVENT_CHECKED, cb, *args)

