from Panel import Panel
import theme

import gtk


class VolumePanel(Panel):

    def __init__(self):
       
        Panel.__init__(self, False)
        
        self.__volume = gtk.Image()
        self.__volume.set_from_pixbuf(theme.speaker_volume)
        self.__volume.set_alignment(0.0, 0.5)        
        self.__volume.show()
        self.box.pack_start(self.__volume, False, False, 50)


    def set_volume(self, percent):
    
        width = 64 + int(636 * (percent / 100.0))
        self.__volume.set_from_pixbuf(theme.speaker_volume.subpixbuf(0, 0, width, 64))

