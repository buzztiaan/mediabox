from ui.Item import Item
import theme


class ThemeListItem(Item):
    """
    List item for media root folders.
    """

    def __init__(self, width, height, preview, label):
    
        self.__preview = preview
        self.__label = label
           
        Item.__init__(self, width, height)
        self.set_graphics(theme.item, theme.item_active)
        
        
    def _render(self, canvas):
    
        Item._render(self, canvas)

        icon_y = (self.get_height() - self.__preview.get_height()) / 2
        canvas.draw_pixbuf(self.__preview, 8, icon_y)

        canvas.draw_text(self.__label, theme.font_plain, 128, 8, theme.color_fg_item)

        if (not self.is_hilighted()):
            canvas.draw_pixbuf(theme.btn_load, 540, 24)

