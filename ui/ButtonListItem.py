from ListItem import ListItem
from Pixmap import Pixmap, TEMPORARY_PIXMAP
import theme



_CLOSED = 0
_OPEN = 1

_GAP_SIZE = 120


class ButtonListItem(ListItem):
    """
    Base class for list items with buttons.
    """

    BUTTON_MENU = "menu"

    # override these by your subclass
    _ITEMS_OPEN = []
    _ITEMS_CLOSED = []
    
    _BUTTONS = []


    def __init__(self):

        self.__state = _CLOSED
        self.__button_pos = []
                
        ListItem.__init__(self)


    def open_menu(self):
    
        self.__state = _OPEN
        self.render()
        
        
    def close_menu(self):
    
        self.__state = _CLOSED
        self.render()
        
        
    def get_button_at(self, px):
    
        if (self.__state == _CLOSED):
            idx = 0
        else:
            idx = len(self._ITEMS_CLOSED)
            
        for pos in self.__button_pos:
            if (px > pos): return self._BUTTONS[idx]
            idx += 1
        #end for
        
        return ""


    def render_buttons(self, canvas):
        """
        Renders the buttons.
        """

        w, h = canvas.get_size()
        
        if (self.__state == _CLOSED):
            items = self._ITEMS_CLOSED
        
        elif (self.__state == _OPEN):
            items = self._ITEMS_OPEN

        else:
            items = []

        if (self.__state == _OPEN):
            menu_width = len(items) * _GAP_SIZE - 16
            canvas.draw_frame(theme.mb_panel, w - 16 - menu_width, 8,
                              menu_width, h - 16, True)
                              
        self.__button_pos = []
        x = w - 8
        for i in items:
            canvas.draw_pixbuf(i, 
                               x - _GAP_SIZE + (_GAP_SIZE - i.get_width()) / 2,
                               (h - i.get_height()) / 2)
            self.__button_pos.append(x - _GAP_SIZE)
            x -= _GAP_SIZE
        #end for

