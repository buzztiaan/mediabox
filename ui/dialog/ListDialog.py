from ui import Window
from ui import windowflags
from ui.itemview import ThumbableGridView
from theme import theme

import gtk


class ListDialog(Window):

    def __init__(self, title):
    
        self.__choice = None
        
    
        Window.__init__(self, Window.TYPE_DIALOG)
        self.set_flag(windowflags.EXCLUSIVE, True)
        self.connect_closed(self.__on_close)
        self.set_title(title)

        self.__list = ThumbableGridView()
        self.add(self.__list)
        

    def render_this(self):
    
        w, h = self.get_size()
        screen = self.get_screen()

        self.__list.set_geometry(0, 0, w, h)


    def __on_close(self):
    
        self.set_visible(False)


    def __on_click_item(self, item):
    
        self.__choice = item
        self.set_visible(False)


    def add_item(self, item):
    
        item.connect_clicked(self.__on_click_item, item)
        self.__list.append_item(item)


    def get_choice(self):
    
        return self.__choice

