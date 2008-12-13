from ImageButton import ImageButton
from Pixmap import text_extents
import theme


class Button(ImageButton):

    def __init__(self, label):
    
        self.__label = label
        
        ImageButton.__init__(self, theme.mb_button_1, theme.mb_button_2)
        w, h = text_extents(label, theme.font_mb_plain)
        self.set_size(w + 24, h + 24)


    def _render_content(self, cnv):

        w, h = self.get_size()

        cnv.draw_centered_text(self.__label, theme.font_mb_plain,
                               0, 0, w, h, "#000000")

