from ui.Item import Item
import theme


class MediaListItem(Item):
    """
    List item for media root folders.
    """

    def __init__(self, width, height, label):
    
        self.__mediatypes = 0
        self.__label = label
           
        Item.__init__(self, width, height)
        self.set_graphics(theme.item, theme.item_active)
        
        
    def set_mediatypes(self, mtypes):
    
        self.__mediatypes = mtypes
        self._render_item()
              
        
    def _render(self, canvas):
    
        Item._render(self, canvas)

        x = 8
        for icon_on, icon_off, t in [
                (theme.prefs_video_on, theme.prefs_video_off, 1),
                (theme.prefs_music_on, theme.prefs_music_off, 2),
                (theme.prefs_image_on, theme.prefs_image_off, 4)]:
            icon = (self.__mediatypes & t) and icon_on or icon_off
            icon_y = (self.get_height() - icon.get_height()) / 2
            canvas.draw_pixbuf(icon, x + (64 - icon.get_width()) / 2, icon_y)
            x += 64
        x += 8

        canvas.draw_text(self.__label, theme.font_tiny, x, 8,
                         theme.color_fg_item)
        canvas.draw_pixbuf(theme.remove, 540, 24)
