from ui import Widget
from ui import Window
from ui import windowflags
from ui.Button import Button
from ui.Label import Label
from ui.TextInput import TextInput
from ui.Slider import HSlider
from ui.layout import HBox, VBox
from theme import theme
import platforms

import gtk




class InputDialog(Window):

    def __init__(self, title, label_ok = "OK", label_cancel = "Cancel"):
    
        self.__inputs = []
        self.__return_code = self.RETURN_CANCEL

        # list of value retrieving functions
        self.__retrievers = []
    
        Window.__init__(self, Window.TYPE_DIALOG)
        self.set_flag(windowflags.EXCLUSIVE, True)
        self.connect_closed(self.__on_close, self.RETURN_CANCEL)
        self.set_title(title)
        
        self.__box = Widget()
        self.add(self.__box)
        
        self.__button_ok = Button(label_ok)
        self.__button_ok.connect_clicked(self.__on_close,
                                         self.RETURN_OK)
        self.__box.add(self.__button_ok)

        if (not platforms.MAEMO5):
            self.__button_cancel = Button(label_cancel)
            self.__button_cancel.connect_clicked(self.__on_close,
                                                 self.RETURN_CANCEL)
            self.__box.add(self.__button_cancel)

        
        self.__vbox = VBox()
        self.__box.add(self.__vbox)
            

    def __on_close(self, return_code):
    
        self.__return_code = return_code
        self.set_visible(False)


    def render_this(self):
    
        Window.render_this(self)
    
        x, y = self.__box.get_screen_pos()
        w, h = self.__box.get_size()
        screen = self.__box.get_screen()
        
        screen.fill_area(x, y, w, h, theme.color_mb_background)

        if (not platforms.MAEMO5):
            self.__vbox.set_geometry(4, 4, w - 8, h - 78)
            self.__button_ok.set_geometry(w - 260, h - 60, 120, 60)
            self.__button_cancel.set_geometry(w - 130, h - 60, 120, 60)

        else:
            self.__vbox.set_geometry(6, 5, w - 165 - 12, h - 5)
            self.__button_ok.set_geometry(w - 120, h - 80, 100, 60)
            
            


    def add_input(self, label, default):
      
        vbox = VBox()
        vbox.set_spacing(12)
        vbox.set_valign(vbox.VALIGN_CENTER)
        self.__vbox.add(vbox, True)
      
        lbl = Label(label, theme.font_mb_plain, theme.color_mb_text)
        vbox.add(lbl)
        
        entry = TextInput()
        vbox.add(entry, True)

        self.__retrievers.append(lambda :entry.get_text())


    def add_range(self, label, min_value, max_value, preset):

        def update_label(v):
            value = min_value + v * total
            lbl.set_text(label + " %d" % value)

        vbox = VBox()
        vbox.set_spacing(12)
        vbox.set_valign(vbox.VALIGN_CENTER)
        self.__vbox.add(vbox, True)

        total = max_value - min_value

        lbl = Label(label + " %d" % preset,
                    theme.font_mb_plain,
                    theme.color_mb_text)
        vbox.add(lbl)

        slider = HSlider(theme.mb_slider_gauge)
        slider.connect_value_changed(update_label)
        slider.set_value((preset - min_value) / float(total))
        vbox.add(slider, True)

        self.__retrievers.append(lambda :min_value + 
                                         slider.get_value() *
                                         (max_value - min_value))

        
    def get_values(self):
    
        return [ r() for r in self.__retrievers ]


    def run(self):
    
        w = gtk.gdk.screen_width()
        h = min(gtk.gdk.screen_height() - 120, len(self.__retrievers) * 120)

        if (not platforms.MAEMO5):
            w -= 80
            h += 70
        self.set_window_size(w, h)
        Window.run(self)

        return self.__return_code

