from ui.Window import Window
from ui import windowflags
from ui.layout import HBox
from ui.layout import VBox
from ui.Button import Button
from ui.Label import Label
from theme import theme
import platforms

import gtk



# TODO: are these unicode chars supported on pre-Diablo maemo OS?
#_UP_ARROW = u"\u21e7"
#_DOWN_ARROW = u"\u21e9"

# oh well, unicode support degraded from Diablo to Fremantle. let's use ASCII
_UP_ARROW = "+"
_DOWN_ARROW = "-"


class ClockSetter(Window):

    def __init__(self):
    
        self.__labels = []
        self.__values = [0] * 4
        
    
        Window.__init__(self, Window.TYPE_DIALOG)
        self.set_flag(windowflags.EXCLUSIVE, True)
        self.connect_closed(self.__on_close)

        self.__hbox = HBox()
        self.__hbox.set_spacing(12)
        self.add(self.__hbox)
        
        for item in ["h1", "h2", ":", "m1", "m2"]:
            if (item == ":"):
                lbl = Label(":", theme.font_sleeptimer_clocksetter,
                                 theme.color_mb_text)
                lbl.set_alignment(lbl.CENTERED)
                self.__hbox.add(lbl, True)
                
            else:
                vbox = VBox()
                vbox.set_spacing(12)
                vbox.set_halign(VBox.HALIGN_CENTER)
                self.__hbox.add(vbox, True)

                btn = Button(_UP_ARROW)
                btn.set_size(80, 80)
                btn.connect_clicked(self.__on_btn_down, item)
                vbox.add(btn, False)

                lbl = Label("0", theme.font_sleeptimer_clocksetter,
                                 theme.color_mb_text)
                lbl.set_alignment(lbl.CENTERED)
                vbox.add(lbl, True)
                self.__labels.append(lbl)
                
                btn = Button(_DOWN_ARROW)
                btn.set_size(80, 80)
                btn.connect_clicked(self.__on_btn_up, item)
                vbox.add(btn, False)
            #end if
        #end for


    def render_this(self):
    
        w, h = self.get_size()
        screen = self.get_screen()
        screen.fill_area(0, 0, w, h, theme.color_mb_background)
        Window.render_this(self)


    def __on_close(self):
    
        self.set_visible(False)


    def __on_btn_up(self, item):
    
        idx = ["h1", "h2", "m1", "m2"].index(item)
        lbl = self.__labels[idx]
        
        value = self.__values[idx]
        value = max(0, value - 1)
        self.__values[idx] = value
        lbl.set_text(`value`)



    def __on_btn_down(self, item):
    
        idx = ["h1", "h2", "m1", "m2"].index(item)
        lbl = self.__labels[idx]

        value = self.__values[idx]
        prev_value = value
        value = min(9, value + 1)
        self.__values[idx] = value
        
        if (self.__is_time_valid()):
            lbl.set_text(`value`)
        else:
            self.__values[idx] = prev_value



    def __is_time_valid(self):
    
        h1, h2, m1, m2 = self.__values
        h = int(`h1` + `h2`)
        m = int(`m1` + `m2`)
        
        return ((0 <= h <= 23) and (0 <= m <= 59))


    def set_time(self, h, m):
    
        h2 = h % 10
        h /= 10
        h1 = h % 10
        
        m2 = m % 10
        m /= 10
        m1 = m % 10
        
        self.__values = [h1, h2, m1, m2]
        for i in range(4):
            self.__labels[i].set_text(`self.__values[i]`)
        

    def get_time(self):
    
        h1, h2, m1, m2 = self.__values
        h = int(`h1` + `h2`)
        m = int(`m1` + `m2`)

        return (h, m)


    def run(self):

        w = gtk.gdk.screen_width()
        h = 300
        if (platforms.MAEMO4):
            w -= 80
        self.set_window_size(w, h)
        
        Window.run(self)


