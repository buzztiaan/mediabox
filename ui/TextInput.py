from Widget import Widget
from Label import Label
from theme import theme


class TextInput(Widget):

    def __init__(self):
    
        self.__text = ""
    
        Widget.__init__(self)
        
        self.__label = Label("", theme.font_mb_headline, "#000000")
        self.add(self.__label)
        
        self.connect_clicked(self.__on_activate_entry)
        self.connect_key_pressed(self.__on_key_pressed)
        
        
    def __on_activate_entry(self):
    
        self.grab_focus()


    def __on_key_pressed(self, key):
    
        if (key == "BackSpace"):
            self.__text = self.__text[:-1]
        elif (key == "space"):
            self.__text += " "
        elif (len(key) == 1):
            self.__text += key
        else:
            return

        self.__label.set_text(self.__text + "|")
    


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        self.__label.set_size(w, h)
        screen.fill_area(x, y, w, h, "#ffffffa0")



    def set_text(self, text):

        self.__text = text
        self.__label.set_text(self.__text + "|")
        

    def get_text(self):

        return self.__text

