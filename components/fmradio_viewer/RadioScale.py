from ui.Widget import Widget
from ui.Pixmap import Pixmap, TEMPORARY_PIXMAP
from theme import theme


class RadioScale(Widget):

    EVENT_TUNED = "event-tuned"
    

    def __init__(self):
        
        self.__range = (0.0, 1.0)
        self.__scala_pmap = None
        self.__needle_pos = 0

        # whether the user is currently dragging
        self.__is_dragging = False
        
        
        Widget.__init__(self)
        self.connect_button_pressed(self.__on_button_press)
        self.connect_button_released(self.__on_button_release)
        self.connect_pointer_moved(self.__on_motion)        
        
        
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        if (self.__scala_pmap):
            TEMPORARY_PIXMAP.draw_pixmap(self.__scala_pmap, 0, 0)
            TEMPORARY_PIXMAP.draw_pixbuf(theme.fmradio_tuner_needle,
                                         0, self.__needle_pos - 24)
            screen.copy_pixmap(TEMPORARY_PIXMAP, 0, 0, x, y, w, h)
        
        
    def __prepare_scala(self):
    
        w, h = self.get_size()
        #h -= 20
        self.__scala_pmap = Pixmap(None, w, h)
        self.__scala_pmap.fill_area(0, 0, w, h, theme.color_mb_background)
        
        a, b = self.__range
        step_size = h / (b - a)
        
        i = 0
        j = a
        while (j < b + 0.1):
            y = int(i + 0.5)   # because floor(x + 0.5) = round(x)
            if (int(j - 0.4) != int(j)):
                self.__scala_pmap.draw_line(0, y, 55, y, "#666666")
                if (int(j) % 5 == 0):
                    self.__scala_pmap.draw_text("%3.1f" % (j + 0.5),
                                                theme.font_mb_micro, 
                                                2, y, "#666666")
            else:
                self.__scala_pmap.draw_line(40, y, 55, y, "#666666")
            i += step_size / 2
            j += 0.5
        
        
    def set_range(self, a, b):
    
        self.__range = (a, b)
        self.__prepare_scala()
        self.render()
        
    
    def tune(self, freq):

        w, h = self.get_size()
        #h -= 20
        a, b = self.__range
        
        percents = (freq - a) / (b - a)
        self.__needle_pos = int(percents * h)
        self.render()
        
        
    def __on_button_press(self, px, py):
    
        self.__is_dragging = True
        self.__on_motion(px, py)


    def __on_button_release(self, px, py):
                   
        self.__is_dragging = False



    def __on_motion(self, px, py):
            
        if (self.__is_dragging):
            w, h = self.get_size()
            #h -= 20
            a, b = self.__range
            
            freq = a + ((b - a) * (py / float(h)))
            freq = max(a, min(b, freq))
            freq = int(freq * 10) / 10.0
            print freq
            self.tune(freq)
            self.send_event(self.EVENT_TUNED, freq)
        #end if
        
        
    def connect_tuned(self, cb, *args):
    
        self._connect(self.EVENT_TUNED, cb, *args)

