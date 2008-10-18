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



    def __init__(self):

        self.__state = _CLOSED
        self.__button_pos = []
        self.__buttons = []
                
        ListItem.__init__(self)

    
    def set_buttons(self, *buttons):
    
        self.__buttons = buttons


    def open_menu(self):
    
        self.__state = _OPEN
        self.invalidate()
        
        
    def close_menu(self):
    
        self.__state = _CLOSED
        self.invalidate()
        
        
    def get_button_at(self, px):
        """
        Returns the button at the given position or None if there's no button
        at that position.
        """
    
        if (self.__state == _CLOSED and len(self.__buttons) > 1):
            if (px > self.__button_pos[0]):
                return self.BUTTON_MENU
        else:
            idx = 0
            for pos in self.__button_pos:
                if (px > pos):
                    btn, img = self.__buttons[idx]
                    return btn
                idx += 1
            #end for
        
        return None


    def render_buttons(self, canvas):
        """
        Renders the buttons.
        """

        w, h = canvas.get_size()
        
        if (self.__state == _OPEN or len(self.__buttons) <= 1):
            items = self.__buttons

        else:
            items = [(self.BUTTON_MENU, theme.mb_item_btn_menu)]
        

        if (self.__state == _OPEN):
            menu_width = len(items) * _GAP_SIZE - 16
            canvas.draw_frame(theme.mb_panel, w - 16 - menu_width, 8,
                              menu_width, h - 16, True)
                              
        self.__button_pos = []
        x = w - 8
        for btn, img in items:
            canvas.draw_pixbuf(img, 
                               x - _GAP_SIZE + (_GAP_SIZE - img.get_width()) / 2,
                               (h - img.get_height()) / 2)
            self.__button_pos.append(x - _GAP_SIZE)
            x -= _GAP_SIZE
        #end for

