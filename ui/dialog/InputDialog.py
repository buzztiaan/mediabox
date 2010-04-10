from ui import Window
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
        self.connect_closed(self.__on_close, self.RETURN_CANCEL)
        self.set_title(title)
        
        self.__button_ok = Button(label_ok)
        self.__button_ok.connect_clicked(self.__on_close,
                                         self.RETURN_OK)
        self.add(self.__button_ok)

        if (not platforms.MAEMO5):
            self.__button_cancel = Button(label_cancel)
            self.__button_cancel.connect_clicked(self.__on_close,
                                                 self.RETURN_CANCEL)
            self.add(self.__button_cancel)

        
        self.__vbox = VBox()
        self.add(self.__vbox)
            

    def __on_close(self, return_code):
    
        self.__return_code = return_code
        self.set_visible(False)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, theme.color_mb_background)

        if (not platforms.MAEMO5):
            self.__vbox.set_geometry(6, 0, w - 32, h - 80)
            self.__button_ok.set_geometry(w - 280, h - 60, 120, 60)
            self.__button_cancel.set_geometry(w - 150, h - 60, 120, 60)

        else:
            self.__vbox.set_geometry(6, 5, w - 165 - 12, h)
            self.__button_ok.set_geometry(w - 120, 5, 115, 60)
            
            


    def add_input(self, label, default):
      
        hbox = HBox()
        hbox.set_spacing(12)
        hbox.set_valign(hbox.VALIGN_CENTER)
        self.__vbox.add(hbox, True)
      
        lbl = Label(label, theme.font_mb_plain, theme.color_mb_text)
        hbox.add(lbl)
        
        entry = TextInput()
        hbox.add(entry, True)

        self.__retrievers.append(lambda :entry.get_text())


    def add_range(self, label, min_value, max_value, preset):

        def update_label(v):
            value = min_value + v * total
            lbl.set_text(label + " %d" % value)

        hbox = HBox()
        hbox.set_spacing(12)
        hbox.set_valign(hbox.VALIGN_CENTER)
        self.__vbox.add(hbox, True)

        total = max_value - min_value

        lbl = Label(label + " %d" % preset,
                    theme.font_mb_plain,
                    theme.color_mb_text)
        hbox.add(lbl)

        slider = HSlider(theme.mb_slider_gauge)
        slider.connect_value_changed(update_label)
        slider.set_value((preset - min_value) / float(total))
        hbox.add(slider, True)

        self.__retrievers.append(lambda :min_value + 
                                         slider.get_value() *
                                         (max_value - min_value))

        
    def get_values(self):
    
        return [ r() for r in self.__retrievers ]


    def run(self):
    
        w = gtk.gdk.screen_width()
        h = min(gtk.gdk.screen_height() - 120, len(self.__retrievers) * 70)

        # add space for dialog buttons
        if (not platforms.MAEMO5):
            h += 80
            
        self.set_window_size(w, h)
        Window.run(self)

        return self.__return_code

