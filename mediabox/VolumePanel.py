from Panel import Panel
import theme

import gtk


class VolumePanel(Panel):

    def __init__(self, esens):
       
        self.__volume_level = 0
       
        Panel.__init__(self, esens, False)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.draw_pixbuf(theme.panel, x, y)
        #self.set_volume(self.__volume_level)

        width = 64 + int(636 * (self.__volume_level / 100.0))
        screen.draw_subpixbuf(theme.speaker_volume, 0, 0, x + 50, y + 8, width, 64)
        screen.draw_subpixbuf(theme.panel, width, 0, x + 50 + width, y, w - width, h)        



    def set_volume(self, percent):
    
        self.__volume_level = percent

