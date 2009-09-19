from ui.Widget import Widget
from ui.layout import VBox
from ui.Button import Button
from ui.Label import Label
from ui.TextInput import TextInput
from ui.Pixmap import text_extents
from theme import theme


class Dialog(Widget):

    def __init__(self):
    
        self.__buttons = []
        self.__button_callbacks = []
        
        self.__icon = None
        self.__header_text = ""
        self.__body_text = ""
        self.__custom_widget = None
        
        Widget.__init__(self)
        
        y = 10
        for i in range(3):
            btn = Button("")
            btn.set_size(140, 80)
            btn.set_visible(False)
            btn.connect_clicked(self.__on_btn_click, i)
            self.add(btn)
            self.__buttons.append(btn)
            self.__button_callbacks.append(None)
        #end for

        self.__header_lbl = Label("", theme.font_mb_dialog_title,
                                  theme.color_mb_dialog_text)
        self.add(self.__header_lbl)
        
        self.__vbox = VBox()
        self.__vbox.set_spacing(12)
        self.add(self.__vbox)

        self.__body_lbl = Label("", theme.font_mb_dialog_body,
                                theme.color_mb_dialog_text)
        self.__vbox.add(self.__body_lbl, False)

        
        self.__text_input = TextInput()
        self.__vbox.add(self.__text_input, False)
               
        
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        #screen.fill_area(x, y, w - 162, h, "#ffffffa0")
        screen.fill_area(x + w - 160, y, 160, h, theme.color_mb_dialog_side)

        self.__header_lbl.set_geometry(20, 20, w - 160 - 40, 0)

        self.__vbox.set_geometry(20, 20 + 80,
                                 w - 160 - 40, h - 80 - 40)

        self.__body_lbl.set_size(w - 160 - 40, 0)

        if (self.__text_input.is_visible()):
            self.__text_input.set_size(w - 160 - 40, 60)
            #self.__text_input.set_geometry(10, th + 10,
            #                               w - 160 - 20, h - th - 20)

        #if (self.__custom_widget):
        #    self.__custom_widget.set_geometry(10, th + 10,
        #                                      w - 160 - 20, h - th - 20)


        btn_y = 10
        for btn in self.__buttons:
            if (btn.is_visible()):
                btn.set_pos(w - 150, btn_y)
                btn_y += 90
        #end for

        if (self.__icon):
            iw = self.__icon.get_width()
            ih = self.__icon.get_height()
            screen.fit_pixbuf(self.__icon, w - 150, h - 150, 140, 140)

        
    def reset(self):
    
        self.__icon = None
    
        self.__body_lbl.set_visible(False)
        if (self.__custom_widget):
            self.__vbox.remove(self.__custom_widget)
            self.__custom_widget = None
        
        self.__text_input.set_visible(False)
        self.__text_input.set_text("")


    def set_icon(self, pbuf):
    
        self.__icon = pbuf

        
    def set_header(self, text):
    
        self.__header_text = text
        self.__header_lbl.set_text(text)
        
        
    def set_body(self, text):
    
        self.__body_text = text
        self.__body_lbl.set_text(text)
        self.__body_lbl.set_visible(True)


    def set_text_input(self, text):
    
        self.set_body(text)
        self.__text_input.set_visible(True)
        self.__text_input.grab_focus()


    def get_text_input(self):
    
        return self.__text_input.get_text()


    def set_custom_widget(self, w):
    
        if (self.__custom_widget):
            self.__vbox.remove(self.__custom_widget)
            self.__custom_widget = None
    
        if (w):
            self.__custom_widget = w
            self.__custom_widget.set_visible(True)
            self.__vbox.add(self.__custom_widget, True)
        

    def set_buttons(self, *buttons):
    
        for btn in self.__buttons:
            btn.set_visible(False)
    
        i = 0
        for label, cb in buttons:
            btn = self.__buttons[i]
            btn.set_text(label)
            btn.set_visible(True)
            self.__button_callbacks[i] = cb
            i += 1
        #end for
        

    def __on_btn_click(self, i):

        self.trigger_button(i)    


    def trigger_button(self, idx):
    
        cb = self.__button_callbacks[idx]
        if (cb):
            cb()

