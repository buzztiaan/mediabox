from mediabox.MediaWidget import MediaWidget
from ui.EventBox import EventBox
from ui.ImageButton import ImageButton
from ui.ProgressBar import ProgressBar
import mediaplayer
from utils import maemo
import theme

import gtk
import gobject


class AudioWidget(MediaWidget):
    """
    Media widget for viewing videos.
    """


    def __init__(self):
    
        self.__player = mediaplayer.get_player_for_uri("")
        mediaplayer.add_observer(self.__on_observe_player)
        self.__volume = 50

        self.__uri = ""
        self.__context_id = 0

        MediaWidget.__init__(self)


        # controls
        self.__btn_play = ImageButton(theme.btn_play_1,
                                      theme.btn_play_2)
        self.__btn_play.connect_clicked(self.__on_play_pause)

        self.__progress = ProgressBar()
        self.__progress.connect_changed(self.__on_set_position)
        
        self._set_controls(self.__btn_play, self.__progress)


    def render_this(self):

        pass


    def __on_observe_player(self, src, cmd, *args):
           
        if (cmd == src.OBS_POSITION):
            ctx, pos, total = args
            if (ctx == self.__context_id):
                pos_m = pos / 60
                pos_s = pos % 60
                total_m = total / 60
                total_s = total % 60
                info = "%d:%02d / %d:%02d" % (pos_m, pos_s, total_m, total_s)

                self.send_event(self.EVENT_MEDIA_POSITION, info)
                self.__progress.set_position(pos, total)

        elif (cmd == src.OBS_STARTED):
            print "Started Player"
            self.__btn_play.set_images(theme.btn_play_1,
                                       theme.btn_play_2)
            
        elif (cmd == src.OBS_KILLED):
            print "Killed Player"
            self.__uri = ""
            #self.set_title("")
            self.__btn_play.set_images(theme.btn_play_1,
                                       theme.btn_play_2)

        elif (cmd == src.OBS_ERROR):
            ctx, err = args
            if (ctx == self.__context_id):
                pass
                #self.__show_error(err)
                #self.set_title("")

        elif (cmd == src.OBS_PLAYING):
            ctx = args[0]
            if (ctx == self.__context_id):
                print "Playing"
                self.__btn_play.set_images(theme.btn_pause_1,
                                           theme.btn_pause_2)                
            
        elif (cmd == src.OBS_STOPPED):
            ctx = args[0]
            if (ctx == self.__context_id):
                print "Stopped"
                self.__btn_play.set_images(theme.btn_play_1,
                                           theme.btn_play_2)
            
        elif (cmd == src.OBS_EOF):
            ctx = args[0]
            if (ctx == self.__context_id):        
                self.__uri = ""

                # unfullscreen
                #if (self.__is_fullscreen): self.__on_fullscreen()
                
                self.__btn_play.set_images(theme.btn_play_1,
                                           theme.btn_play_2)                



    def __on_set_position(self, pos):
    
        self.__player.seek_percent(pos)


    def __on_play_pause(self):
    
        self.__player.pause()





    def load(self, uri):

        def f():
            if (uri == self.__uri): return
            
            # TODO: get player for MIME type
            self.__player = mediaplayer.get_player_for_uri(uri)
            
            try:
                self.__context_id = self.__player.load_video(uri)
            except:
                import traceback; traceback.print_exc()
                return
                            
            self.__player.set_volume(self.__volume)
            self.__uri = uri
            
                
        gobject.idle_add(f)

