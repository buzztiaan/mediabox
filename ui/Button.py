from ImageButton import ImageButton
from Pixmap import text_extents
from theme import theme


class Button(ImageButton):

    def __init__(self, label = "", icon = None):
    
        self.__label = label
        self.__icon = icon
        
        ImageButton.__init__(self, theme.mb_button_1, theme.mb_button_2)
        w, h = text_extents(label, theme.font_mb_plain)
        self.set_size(w + 24, h + 24)
        
        self.add_overlay(self.__icon_overlay)
        self.add_overlay(self.__text_overlay)
        
        
    def __icon_overlay(self, screen):
    
        if (self.__icon):
            w, h = self.get_size()
            i_w = self.__icon.get_width()
            i_h = self.__icon.get_height()
            screen.draw_pixbuf(self.__icon, (w - i_w) / 2, (h - i_h) / 2)
        
        
    def __text_overlay(self, screen):

        if (self.__label):
            w, h = self.get_size()
            if (self.__icon):
                i_h = self.__icon.get_height()
                y = ((h - i_h) / 2) + i_h
            else:
                y = 0
            screen.draw_centered_text(self.__label, theme.font_mb_plain,
                                      0, y, w, h - y, theme.color_mb_button_text)


    def set_text(self, text):
        """
        Changes the button label.
        @since: 0.96.5
        
        @param text: label text
        """
    
        self.__label = text
        self.render()


    def set_icon(self, icon):
        """
        Changes the button icon. Pass C{None} to disable the icon.
        @since: 2010.11.04
        
        @param icon: icon pixbuf
        """
    
        self.__icon = icon
        self.render()

