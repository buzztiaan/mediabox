from com import Player, msgs
from ui.VideoScreen import VideoScreen
from ui.Toolbar import Toolbar
from ui.ImageButton import ImageButton
import mediaplayer
from theme import theme
from utils import logging


class VideoPlayer(Player):

    def __init__(self):

        self.__player = None
        self.__context_id = 0

        Player.__init__(self)
        
        # video screen
        self.__screen = VideoScreen()
        self.add(self.__screen)
        
        # toolbar elements
        self.__btn_play = ImageButton(theme.mb_btn_play_1,
                                      theme.mb_btn_play_2)
        self.__btn_play.connect_clicked(self.__on_btn_play)
        
        # toolbar
        self.__toolbar = Toolbar()
        self.__toolbar.set_toolbar(self.__btn_play)
        self.add(self.__toolbar)


    def __on_btn_play(self):
    
        if (self.__player):
            self.__player.pause()


    def __on_status_changed(self, ctx_id, status):
    
        if (ctx_id == self.__context_id):
            if (status == self.__player.STATUS_PLAYING):
                self.__btn_play.set_images(theme.mb_btn_pause_1,
                                           theme.mb_btn_pause_2)
                                           
            elif (status == self.__player.STATUS_STOPPED):
                self.__btn_play.set_images(theme.mb_btn_play_1,
                                           theme.mb_btn_play_2)


    def render_this(self):
    
        w, h = self.get_size()
        self.__screen.set_geometry(0, 0, w, h - 70)
        self.__toolbar.set_geometry(0, h - 70, w, 70)
        
        
    def get_mime_types(self):
    
        return ["video/*"]        

        
    def load(self, f):
    
        self.__player = mediaplayer.get_player_for_mimetype(f.mimetype)
        self.__player.connect_status_changed(self.__on_status_changed)
        
        self.__player.set_window(self.__screen.get_xid())
        
        """
        uri = item.get_resource()
        if (not uri.startswith("/") and
            not "://localhost" in uri and
            not "://127.0.0.1" in uri):                    
            maemo.request_connection()
        #end if
        """
        
        uri = f.get_resource()
        try:
            self.__context_id = self.__player.load_video(uri)
        except:
            logging.error("error loading media file: %s\n%s",
                          uri, logging.stacktrace())

