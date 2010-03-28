from Widget import Widget
from native import TextInput as _TextInput

from Pixmap import text_extents
from theme import theme


class TextInput(Widget):

    def __init__(self):
    
        Widget.__init__(self)
        
        self.__native_input = _TextInput()
        
        
    def _visibility_changed(self):
    
        if (self.is_visible()):
            self.__native_input.set_visible(True)
        else:
            self.__native_input.set_visible(False)


    def render_this(self):

        window = self.get_window()
        self.__native_input.set_window(window)
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        
        self.__native_input.set_geometry(x, y, w, h)


    def set_text(self, text):

        self.__native_input.set_text(text)
        

    def get_text(self):

        return self.__native_input.get_text()


class xTextInput(Widget):

    def __init__(self):
    
        self.__text = ""
        self.__cursor_pos = 0
    
        Widget.__init__(self)
        
        self.__native_input = _TextInput()
        
        self.connect_clicked(self.__on_activate_entry)
        self.connect_key_pressed(self.__on_key_pressed)
        
        
    def __on_activate_entry(self):
    
        self.grab_focus()


    def __on_key_pressed(self, key):
    
        left = self.__text[:self.__cursor_pos]
        right = self.__text[self.__cursor_pos:]
        
        if (key == "Left"):
            self.__cursor_pos = max(0, self.__cursor_pos - 1)
        elif (key == "Right"):
            self.__cursor_pos = min(len(left + right), self.__cursor_pos + 1)
        elif (key == "BackSpace"):
            left = left[:-1]
            self.__cursor_pos = max(0, self.__cursor_pos - 1)
        elif (key == "space"):
            left += " "
            self.__cursor_pos = min(len(left + right), self.__cursor_pos + 1)
        elif (len(key) == 1):
            left += key
            self.__cursor_pos = min(len(left + right), self.__cursor_pos + 1)
        else:
            return

        self.__text = left + right
        self.render()


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, "#ffffff")
        screen.set_clip_rect(x, y, w, h)
        if (self.__text):
            self.__render_text()
        self.__render_cursor()
        screen.set_clip_rect()


    def __render_text(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        tw, th = text_extents(self.__text[0], theme.font_mb_plain)
        screen.draw_text(self.__text, theme.font_mb_plain,
                         x, y + (h - th) / 2, "#000000")


    def __render_cursor(self):
    
        # find position of cursor
        text = self.__text
        p = text[:self.__cursor_pos]
        tw, th = text_extents(p, theme.font_mb_plain)

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        screen.fill_area(x + tw, y + 2, 4, h - 4, "#000000a0")
        


    def set_text(self, text):

        self.__text = text
        self.render()
        

    def get_text(self):

        return self.__text

