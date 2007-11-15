from viewers.Thumbnail import Thumbnail
import theme

import os

_PATH = os.path.dirname(__file__)

_WIDTH = 560
_HEIGHT = 360


class LogoScreen(Thumbnail):

    def __init__(self):

        Thumbnail.__init__(self, _WIDTH, _HEIGHT)
        
        self.add_text("MediaBox", 0, 0,
                      theme.font_headline, "#ffffff")
        self.add_rect(0, 35, _WIDTH, 1, 0xa0, 0xa0, 0xff)                      
        self.add_text("Entertainment in your Hands", 0, 34,
                      theme.font_tiny, "#e0e0e0")
        self.add_text("v 0.90 - (c) 2007 Martin Grimme", 0, 340,
                      theme.font_tiny, "#a0a0a0")    
        self.add_text("http://mediabox.garage.maemo.org", 142, 220,
                      theme.font_plain, "#a0a0a0")    

        self.add_image(theme.viewer_video, 156, 156)                      
        self.add_image(theme.viewer_music, 256, 156)
        self.add_image(theme.viewer_image, 356, 156)
        
