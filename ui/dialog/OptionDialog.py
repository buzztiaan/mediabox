from ui import Window
from ui import windowflags
from ui.itemview import ThumbableGridView
from ui.itemview import ButtonItem
import platforms

import gtk


class OptionDialog(Window):

    def __init__(self, title):
    
        self.__num_of_options = 0
        self.__choice = -1
    
        Window.__init__(self, Window.TYPE_DIALOG)
        self.set_flag(windowflags.EXCLUSIVE, True)
        self.connect_closed(self.__on_close)
        self.set_visible(False)
        self.set_title(title)
        
        self.__list = ThumbableGridView()
        self.add(self.__list)
       
       
    def __on_close(self):
    
        self.set_visible(False)
        

    def add_option(self, icon, label):
    
        def on_choice(i):
            self.__choice = i
            self.set_visible(False)
    
        btn = ButtonItem(label)
        btn.connect_clicked(on_choice, self.__num_of_options)
        self.__list.append_item(btn)
        
        self.__num_of_options += 1       


    def get_choice(self):
    
        return self.__choice


    def run(self):

        w = gtk.gdk.screen_width()
        h = min(gtk.gdk.screen_height() - 120, self.__num_of_options * 80)
        if (platforms.MAEMO4):
            w -= 80
        self.set_window_size(w, h)
    
        Window.run(self)
        
        if (self.__choice == -1):
            return self.RETURN_CANCEL
        else:
            return self.RETURN_OK

