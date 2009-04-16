from Widget import Widget
from theme import theme

import gtk


class TextInput(Widget):

    def __init__(self):
    
        Widget.__init__(self)

        self.__entry = None


    def __init_entry(self):

        self.__entry = gtk.Entry()
        self.__entry.modify_font(theme.font_mb_headline)
        self.__entry.show()
        win = self.get_window()
        win.put(self.__entry, 0, 0)
        
        
    def _visibility_changed(self):
    
        if (self.__entry):
            if (self.is_visible()):
                self.__entry.show()
            else:
                self.__entry.hide()
        #end if
            
        
    def render_this(self):
    
        if (not self.__entry):
            self.__init_entry()
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        win = self.get_window()
        win.move(self.__entry, x, y)
        self.__entry.set_size_request(w, h)


    def set_text(self, text):

        if (self.__entry):    
            self.__entry.set_text(text)
        

    def get_text(self):
    
        return self.__entry.get_text()

