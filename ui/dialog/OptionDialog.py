from ui import Window
from ui.itemview import ThumbableGridView
from ui.itemview import ButtonItem

import gtk


class OptionDialog(Window):

    def __init__(self, title):
    
        self.__num_of_options = 0
        self.__choice = -1
    
        Window.__init__(self, Window.TYPE_DIALOG)
        self.connect_closed(self.__on_close)
        self.set_visible(False)
        self.set_title(title)
        
        self.__list = ThumbableGridView()
        self.add(self.__list)
       
       
    def __on_close(self):
    
        self.set_visible(False)
       
       
    def render_this(self):
    
        w, h = self.get_size()
        self.__list.set_geometry(0, 0, w, h)
        

    def add_option(self, icon, label):
    
        def on_choice(i):
            self.__choice = i
    
        btn = ButtonItem(label)
        btn.connect_clicked(on_choice, self.__num_of_options)
        self.__list.append_item(btn)
        
        self.__num_of_options += 1       


    def get_choice(self):
    
        return self.__choice


    def run(self):
    
        w = gtk.gdk.screen_width()
        h = min(gtk.gdk.screen_height() - 120, self.__num_of_options * 80)
        self.set_window_size(w, h)
        self.set_visible(True)
        
        self.__choice = -1
        while (self.is_visible() and self.__choice == -1):
            gtk.main_iteration(True)
        self.destroy()
        return 0

