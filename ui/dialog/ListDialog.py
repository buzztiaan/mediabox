from ui.Window import Window
from ui.itemview import ThumbableGridView
from ui.Slider import VSlider
from theme import theme

import gtk


class ListDialog(Window):

    def __init__(self, title):
    
        self.__choice = None
        
    
        Window.__init__(self, Window.TYPE_DIALOG)
        self.set_title(title)

        self.__list = ThumbableGridView()
        self.add(self.__list)
        
        self.__slider = VSlider(theme.mb_list_slider)
        self.add(self.__slider)
        self.__list.associate_with_slider(self.__slider)


    def render_this(self):
    
        w, h = self.get_size()
        screen = self.get_screen()

        self.__slider.set_geometry(0, 0, 40, h)
        self.__list.set_geometry(40, 0, w - 40, h)


    def __on_click_item(self, item):
    
        self.__choice = item
        self.set_visible(False)


    def add_item(self, item):
    
        item.connect_clicked(self.__on_click_item, item)
        self.__list.append_item(item)


    def get_choice(self):
    
        return self.__choice

