from ui.Item import Item
import theme


class ListItem(Item):
    """
    List item for music tracks.
    """

    def __init__(self, width, height, label):
    
        self.__label = label
           
        Item.__init__(self,width, height)
        self.set_graphics(theme.item, theme.item_active)
        
        
    def _render(self, canvas):
    
        Item._render(self, canvas)
        canvas.draw_text(self.__label, theme.font_plain, 8, 8,
                         theme.color_fg_item)

        if (not self.is_hilighted()):
            canvas.draw_pixbuf(theme.btn_load, 540, 24)

