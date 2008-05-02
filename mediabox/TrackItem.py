from ui.Item import Item
import theme


_CLOSED = 0
_OPEN = 1

_GAP_SIZE = 120



def _to_utf8(s):

    return s.decode("utf-8", "replace").encode("utf-8")
    
def _xml_escape(s):

    return s.replace("<", "&lt;") \
            .replace(">", "&gt;") \
            .replace("&", "&amp;")
            

class TrackItem(Item):
    """
    List item for track items.
    """

    # override these by your subclass
    _ITEMS_OPEN = []
    _ITEMS_CLOSED = []
    
    _BUTTONS = []


    def __init__(self, icon, label, sublabel):

        self.__state = _CLOSED
        self.__button_pos = []
    
        self.__icon = icon
        self.__color_1 = "#000000"
        self.__color_2 = "#666666"
        self.__font = None

        self.__grip = None
    
        label = label.decode("utf-8", "replace").encode("utf-8")
        sublabel = sublabel.decode("utf-8", "replace").encode("utf-8")
        self.__label = _xml_escape(_to_utf8(label))
        self.__sublabel = _xml_escape(_to_utf8(sublabel))
           
        Item.__init__(self)
        
        
    def set_colors(self, col1, col2):
    
        self.__color_1 = col1
        self.__color_2 = col2
        
        
    def set_font(self, font):
    
        self.__font = font


    def set_grip(self, pbuf):
    
        self.__grip = pbuf
        
        
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
        
        
    def render_this(self, canvas):
    
        w, h = canvas.get_size()
        
        x = 0
        if (self.__grip):
            x += 4
            canvas.draw_pixbuf(self.__grip, x, 0)
            x += 24
            

        x += 8        
        if (self.__icon):
            canvas.draw_pixbuf(self.__icon,
                               x, (h - self.__icon.get_height()) / 2)
            x += self.__icon.get_width()
            x += 12
        
        canvas.draw_text("%s\n<span color='%s'>%s</span>" \
                      % (self.__label, self.__color_2, self.__sublabel),
                         self.__font, x, 8,
                         self.__color_1, use_markup = True)

        if (self.__state == _CLOSED):
            items = self._ITEMS_CLOSED
        
        elif (self.__state == _OPEN):
            items = self._ITEMS_OPEN

        else:
            items = []

        if (self.__state == _OPEN):
            menu_width = len(items) * _GAP_SIZE - 16
            canvas.draw_frame(theme.panel, w - 16 - menu_width, 8,
                              menu_width, 64, True)
                              
        self.__button_pos = []
        x = w - 8
        for i in items:
            canvas.draw_pixbuf(i, 
                               x - _GAP_SIZE + (_GAP_SIZE - i.get_width()) / 2,
                               (h - i.get_height()) / 2)
            self.__button_pos.append(x - _GAP_SIZE)
            x -= _GAP_SIZE
        #end for

