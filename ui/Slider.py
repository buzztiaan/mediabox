from Widget import Widget
from ui.Pixmap import Pixmap
from theme import theme


class Slider(Widget):
    """
    A horizontal or vertical slider widget.
    @since: 0.96.5
    """

    HORIZONTAL = 0
    VERTICAL = 1

    EVENT_VALUE_CHANGED = "value-changed"


    def __init__(self, button_pbuf):
        """
        Creates a new slider with the given pixbuf for the slider.
        
        @param button_pbuf: pixbuf for the slider
        """

        self.__buffer = None

        self.__mode = self.HORIZONTAL
        self.__value = 0.0
        self.__button_pbuf = button_pbuf
        
        self.__is_dragging = False
        self.__grab_point = 0
        self.__previous_pos = 0
        
    
        Widget.__init__(self)
        self.connect_button_pressed(self.__on_press)
        self.connect_button_released(self.__on_release)
        self.connect_pointer_moved(self.__on_motion)


    def connect_value_changed(self, cb, *args):
    
        self._connect(self.EVENT_VALUE_CHANGED, cb, *args)
        
        
    def _reload(self):
    
        w, h = self.get_size()
        if (self.__buffer):
            self.__buffer.fill_area(0, 0, w, h,
                                    theme.color_mb_background)

        

    def set_size(self, w, h):
    
        Widget.set_size(self, w, h)
        
        if (not self.__buffer or (w, h) != self.__buffer.get_size()):
            self.__buffer = Pixmap(None, w, h)
            self.__buffer.fill_area(0, 0, w, h, theme.color_mb_background)
        
        
    def set_mode(self, mode):
        """
        Switches the orientation mode.
        
        @param mode: one of C{HORIZONTAL} or C{VERTICAL}
        """
    
        self.__mode = mode


    def set_value(self, v):
        """
        Sets the slider value within the range [0.0, 1.0].
        This action does not emit a "value-changed" event.
        
        @param v: value
        """
        
        v = min(1.0, max(0.0, v))
        if (self.__mode == self.VERTICAL):
            v = 1.0 - v
        if (abs(v - self.__value) > 0.01):
            self.__value = v
            self.render()
        
        
    def render_this(self):

        if (not self.__buffer): return
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        
        sw = self.__button_pbuf.get_width()
        sh = self.__button_pbuf.get_height()
        
        if (self.__mode == self.HORIZONTAL):
            pos = (w - sw) * self.__value
            sx = pos
            sy = 0
            render_from = min(pos, self.__previous_pos)
            render_to = min(w, max(pos + sw, self.__previous_pos + sw))
        
            self.__buffer.fill_area(render_from, 0, render_to - render_from + 1, h,
                                    theme.color_mb_background)
            self.__buffer.draw_pixbuf(self.__button_pbuf, sx, sy)
            
        else:
            pos = (h - sh) * self.__value
            sx = 0
            sy = pos
            render_from = min(pos, self.__previous_pos)
            render_to = min(h, max(pos + sh, self.__previous_pos + sh))

            self.__buffer.fill_area(0, render_from, w, render_to - render_from + 1,
                                    theme.color_mb_background)
            self.__buffer.draw_pixbuf(self.__button_pbuf, sx, sy)

            
        screen.copy_buffer(self.__buffer, 0, 0, x, y, w, h)
        self.__previous_pos = pos

        
        
    def __on_press(self, px, py):
    
        self.__is_dragging = True
        
        w, h = self.get_size()
        if (self.__mode == self.HORIZONTAL):
            pos = (w - self.__button_pbuf.get_width()) * self.__value
            self.__grab_point = px - pos
        else:
            pos = (h - self.__button_pbuf.get_height()) * self.__value
            self.__grab_point = py - pos


    def __on_release(self, px, py):
    
        self.__is_dragging = False


    def __on_motion(self, px, py):
    
        if (self.__is_dragging):
            w, h = self.get_size()
            sw = self.__button_pbuf.get_width()
            sh = self.__button_pbuf.get_height()
            
            if (self.__mode == self.HORIZONTAL):
                px -= self.__grab_point
                px = min(w - sw, max(0, px))
                self.__value = px / float(w - sw)
                value = self.__value
            else:
                py -= self.__grab_point
                py = min(h - sh, max(0, py))
                self.__value = py / float(h - sh)
                value = 1.0 - self.__value
            
            self.render()
            self.send_event(self.EVENT_VALUE_CHANGED, value)

