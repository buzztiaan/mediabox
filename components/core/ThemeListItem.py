from ui.ListItem import ListItem
import theme


class ThemeListItem(ListItem):
    """
    List item for media root folders.
    """

    def __init__(self, w, h, preview, label):
    
        self.__preview = preview
        self.__label = label
           
        ListItem.__init__(self)
        self.set_size(w, h)
        
        
    def render_this(self, canvas):
    
        ListItem.render_this(self, canvas)
    
        w, h = canvas.get_size()
        icon_y = (h - self.__preview.get_height()) / 2
        canvas.draw_pixbuf(self.__preview, 8, icon_y)

        canvas.draw_text(self.__label, theme.font_plain, 128, 8, theme.color_fg_item)

        if (not self.is_hilighted()):
            canvas.draw_pixbuf(theme.mb_btn_load, 540, 24)

