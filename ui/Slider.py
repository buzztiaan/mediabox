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
        
        # background pbuf
        self.__background = None

        # offscreen buffer
        self.__buffer = None

        self.__mode = self.HORIZONTAL
        self.__value = 0.0
        self.__button_pbuf = button_pbuf
        
        self.__is_dragging = False
        self.__grab_point = 0
        self.__previous_pos = 0
        
        self.__is_active = True
        
        # time of last motion
        self.__last_motion_time = 0
        
    
        Widget.__init__(self)
        self.connect_button_pressed(self.__on_press)
        self.connect_button_released(self.__on_release)
        self.connect_pointer_moved(self.__on_motion)


    def connect_value_changed(self, cb, *args):
    
        self._connect(self.EVENT_VALUE_CHANGED, cb, *args)
        
        
    def _reload(self):
    
        w, h = self.get_size()
        self.__buffer = None


    def set_active(self, value):
    
        self.__is_active = value
        self.render()



    def set_image(self, pbuf):
    
        self.__button_pbuf = pbuf
        self.render()


    def set_background(self, pbuf):
    
        self.__background = pbuf


    def set_size(self, w, h):
    
        Widget.set_size(self, w, h)
        
        if (w == 0 or h == 0): return

        if (self.__buffer and (w, h) != self.__buffer.get_size()):
            self.__buffer = None
        
        
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
            self.move(v)


    def get_value(self):
        """
        Returns the current value within the range [0.0, 1.0].

        @return: current value
        """

        return self.__value
        
        
    def render_this(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        if (not self.__buffer):
            self.__buffer = Pixmap(None, w, h)

        if (self.__background):
            self.__buffer.draw_pixbuf(self.__background, 0, 0)
        else:
            self.__buffer.fill_area(0, 0, w, h, theme.color_mb_background)

        sw = self.__button_pbuf.get_width()
        sh = self.__button_pbuf.get_height()
        
        if (self.__is_active):
            if (self.__mode == self.HORIZONTAL):
                pos = int((w - sw) * self.__value)
                self.__buffer.draw_pixbuf(self.__button_pbuf, pos, 0)
            else:
                pos = int((h - sh) * self.__value)
                self.__buffer.draw_pixbuf(self.__button_pbuf, 0, pos)
            self.__previous_pos = pos
        #end if

        screen.copy_buffer(self.__buffer, 0, 0, x, y, w, h)
        

    def move(self, v):

        if (not self.__buffer): return

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        btn_w = self.__button_pbuf.get_width()
        btn_h = self.__button_pbuf.get_height()
        
        if (self.__mode == self.HORIZONTAL):
            new_pos = int((w - btn_w) * v)
        else:
            new_pos = int((h - btn_h) * v)
        
        pos = self.__previous_pos
        min_pos = min(new_pos, pos)
        delta = new_pos - pos
        
        if (delta == 0): return
        
        if (self.__mode == self.HORIZONTAL):
            self.__buffer.move_area(pos, 0, btn_w, btn_h, delta, 0)
            if (delta > 0):
                self.__render_background(self.__buffer,
                                         min_pos, 0,
                                         abs(delta), btn_h)
            else:
                self.__render_background(self.__buffer,
                                         min_pos + btn_w, 0,
                                         abs(delta), btn_h)
            
            if (self.may_render()):
                screen.copy_buffer(self.__buffer,
                                   min_pos, 0, x + min_pos, y,
                                   btn_w + abs(delta), btn_h)
            
        else:
            self.__buffer.move_area(0, pos, btn_w, btn_h, 0, delta)
            if (delta > 0):
                self.__render_background(self.__buffer,
                                         0, min_pos,
                                         btn_w, abs(delta))
            else:
                self.__render_background(self.__buffer,
                                         0, min_pos + btn_h,
                                         btn_w, abs(delta))

            if (self.may_render()):
                screen.copy_buffer(self.__buffer,
                                   0, min_pos, x, y + min_pos,
                                   btn_w, btn_h + abs(delta))

        self.__previous_pos = new_pos
        
        
    def __render_background(self, buf, x, y, w, h):
    
        if (self.__background):
            buf.draw_subpixbuf(self.__background, x, y, x, y, w, h)
        else:
            buf.fill_area(x, y, w, h, theme.color_mb_background)
        
        
        
    def __on_press(self, px, py):
    
        self.__is_dragging = True
        
        w, h = self.get_size()
        sw = self.__button_pbuf.get_width()
        sh = self.__button_pbuf.get_height()

        if (self.__mode == self.HORIZONTAL):
            pos = (w - sw) * self.__value
            self.__grab_point = max(0, min(px - pos, sw))
        else:
            pos = (h - sh) * self.__value
            self.__grab_point = max(0, min(py - pos, sh))
        self.__on_motion(px, py)


    def __on_release(self, px, py):
    
        self.__is_dragging = False


    def __on_motion(self, px, py):
    
        if (self.__is_dragging):
            #now = time.time()
            #if (now - self.__last_motion_time < 0.1): return
            #self.__last_motion_time = now
        
            w, h = self.get_size()
            sw = self.__button_pbuf.get_width()
            sh = self.__button_pbuf.get_height()

            if (self.__mode == self.HORIZONTAL):
                px -= self.__grab_point
                px = min(w - sw, max(0, px))
                v = px / float(w - sw)
            else:
                py -= self.__grab_point
                py = min(h - sh, max(0, py))
                v = 1.0 - py / float(h - sh)

            self.set_value(v)
            
            #self.render()
            self.send_event(self.EVENT_VALUE_CHANGED, v)
        #end if
        
        
class HSlider(Slider):

    def __init__(self, *args):
    
        Slider.__init__(self, *args)
        self.set_mode(self.HORIZONTAL)
        
        
class VSlider(Slider):

    def __init__(self, *args):
    
        Slider.__init__(self, *args)
        self.set_mode(self.VERTICAL)

