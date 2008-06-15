from viewers.Thumbnail import Thumbnail
from mediabox import values
import theme

import os

_PATH = os.path.dirname(__file__)

_WIDTH = 600
_HEIGHT = 380


class LogoScreen(Thumbnail):

    def __init__(self):

        Thumbnail.__init__(self, _WIDTH, _HEIGHT)
        
        self.add_image(theme.logo_big)
        
        self.add_text("v %s - %s - http://mediabox.garage.maemo.org" \
                      % (values.VERSION, values.COPYRIGHT),
                      3, 336, theme.font_tiny, "#a0a0a0")    
