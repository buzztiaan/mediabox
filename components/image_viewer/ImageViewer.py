from com import Player, msgs
from Image import Image
from ui.KineticScroller import KineticScroller
from ui.Toolbar import Toolbar
from ui.ImageButton import ImageButton
from theme import theme
from utils import logging


class ImageViewer(Player):

    def __init__(self):      

        Player.__init__(self)
        
        self.__image = Image()
        self.add(self.__image)
        
        kscr = KineticScroller(self.__image)
        
        # toolbar elements
        self.__btn_play = ImageButton(theme.mb_btn_play_1,
                                      theme.mb_btn_play_2)
        self.__btn_play.connect_clicked(self.__on_btn_play)
        
        # toolbar
        self.__toolbar = Toolbar()
        self.add(self.__toolbar)

        btn_previous = ImageButton(theme.mb_btn_previous_1,
                                   theme.mb_btn_previous_2)
        btn_previous.connect_clicked(self.__on_btn_previous)

        btn_next = ImageButton(theme.mb_btn_next_1,
                               theme.mb_btn_next_2)
        btn_next.connect_clicked(self.__on_btn_next)

        self.__toolbar.set_toolbar(btn_previous,
                                   self.__btn_play,
                                   btn_next)


    def __on_btn_play(self):
    
        if (self.__player):
            self.__player.pause()


    def __on_btn_previous(self):
        
        self.__image.slide_from_left()
        self.emit_message(msgs.MEDIA_ACT_PREVIOUS)


    def __on_btn_next(self):
        
        self.__image.slide_from_right()
        self.emit_message(msgs.MEDIA_ACT_NEXT)


    def render_this(self):
    
        w, h = self.get_size()
        if (w < h):
            # portrait mode
            self.__image.set_geometry(0, 0, w, h - 70)
            self.__toolbar.set_geometry(0, h - 70, w, 70)

        else:
            # landscape mode
            self.__image.set_geometry(0, 0, w - 70, h)
            self.__toolbar.set_geometry(w - 70, 0, 70, h)        
        
        
    def get_mime_types(self):
    
        return ["image/*"]        

        
    def load(self, f):

        self.__image.load(f)
        self.render()
