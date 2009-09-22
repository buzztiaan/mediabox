from com import Player, msgs
from ui.Toolbar import Toolbar
from ui.ImageButton import ImageButton
from ui.ProgressBar import ProgressBar
import mediaplayer
from utils import logging
from theme import theme


class AudioPlayer(Player):

    def __init__(self):
    
        self.__player = None
        self.__context_id = 0
        
        self.__cover = None
        
    
        Player.__init__(self)
        

        # toolbar
        self.__toolbar = Toolbar()
        self.add(self.__toolbar)
        
        self.__btn_play = ImageButton(theme.mb_btn_play_1,
                                      theme.mb_btn_play_2)
        self.__btn_play.connect_clicked(self.__on_btn_play)

        self.__progress = ProgressBar()
        self.add(self.__progress)
        self.__progress.connect_changed(self.__on_seek)

        self.__toolbar.set_toolbar(self.__btn_play)

        
    def get_mime_types(self):
    
        return ["application/ogg", "audio/*"]


    def __on_btn_play(self):
    
        if (self.__player):
            self.__player.pause()
            
            
    def __on_change_player_status(self, ctx_id, status):
    
        if (ctx_id == self.__context_id):
            if (status == self.__player.STATUS_PLAYING):
                self.__btn_play.set_images(theme.mb_btn_pause_1,
                                           theme.mb_btn_pause_2)
            elif (status == self.__player.STATUS_STOPPED):
                self.__btn_play.set_images(theme.mb_btn_play_1,
                                           theme.mb_btn_play_2)


    def __on_seek(self, progress):
    
        if (self.__player):
            self.__player.seek_percent(progress)


    def __on_update_position(self, ctx_id, pos, total):
    
        if (ctx_id == self.__context_id):
            self.__progress.set_position(pos, total)


    def __on_loaded_cover(self, pbuf, ctx_id):
   
        if (pbuf and ctx_id == self.__context_id):
            if (self.__cover):
                del self.__cover

            self.__cover = pbuf
        #end if
        

    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        self.__toolbar.set_geometry(0, h - 70, w, 70)

        if (w < h):
            # portrait mode
            cover_size = w - 20
        else:
            # landscape mode
            cover_size = h - (70 + 20 + 42)

        if (self.__cover):
            screen.fit_pixbuf(self.__cover,
                              x + 10, y + 10,
                              cover_size, cover_size)
        else:
            screen.draw_rect(x + 10, y + 10, cover_size, cover_size,
                             "#000000")
            screen.fill_area(x + 12, y + 12, cover_size - 4, cover_size - 4,
                             "#aaaaaa")

        self.__progress.set_geometry(10, 10 + cover_size,
                                     cover_size, 42)

        
        
    def load(self, f):
    
        self.__player = mediaplayer.get_player_for_mimetype(f.mimetype)
        self.__player.connect_status_changed(self.__on_change_player_status)
        self.__player.connect_position_changed(self.__on_update_position)

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
            self.__context_id = self.__player.load_audio(uri)
        except:
            logging.error("error loading media file: %s\n%s",
                          uri, logging.stacktrace())

        # load cover art
        self.call_service(msgs.COVERSTORE_SVC_GET_COVER,
                          f, self.__on_loaded_cover, self.__context_id)

