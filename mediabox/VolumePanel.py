from Panel import Panel
from ui.Pixmap import Pixmap
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
        
        buf = Pixmap(None, w, h)
        
        buf.draw_pixbuf(theme.panel, 0, 0)
        #self.set_volume(self.__volume_level)

        width = 64 + int(636 * (self.__volume_level / 100.0))
        buf.draw_subpixbuf(theme.speaker_volume, 0, 0, 50, 8, width, 64)
        buf.draw_subpixbuf(theme.panel, width, 0, 50 + width, 0, w - width, h)
        screen.copy_pixmap(buf, 0, 0, x, y, w, h)



    def set_volume(self, percent):
    
        self.__volume_level = percent
        self.render()

