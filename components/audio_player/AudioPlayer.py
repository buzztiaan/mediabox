from com import Player, msgs
from CoverArt import CoverArt
from ui.ImageButton import ImageButton
from ui.ProgressBar import ProgressBar
from ui.Slider import Slider
from ui.Label import Label
from ui.Toolbar import Toolbar
from ui.layout import Arrangement
from ui.layout import HBox, VBox
from ui.Pixmap import Pixmap
from mediabox import media_bookmarks
from mediabox import tagreader
from mediabox import imageloader
from utils import logging
from theme import theme

import gobject
import time


_LANDSCAPE_ARRANGEMENT = """
  <arrangement>
    <widget name="progress" x1="80" y1="-50" x2="-90" y2="-10"/>
    <widget name="btn_star" x1="10" y1="-64" x2="74" y2="100%"/>
    <widget name="toolbar" x1="-80" y1="0" x2="100%" y2="100%"/>
    <widget name="slider" x1="0" y1="0" x2="40" y2="-64"/>
    
    <widget name="cover" x1="50" y1="10" x2="48%" y2="-64"/>
    <widget name="trackinfo" x1="50%" y1="20" x2="-90" y2="120"/>
  </arrangement>
"""


_PORTRAIT_ARRANGEMENT = """
  <arrangement>
    <widget name="progress" x1="50" y1="-170" x2="-50" y2="-130"/>
    <widget name="toolbar" x1="0" y1="-80" x2="100%" y2="100%"/>
    <widget name="slider" x1="0" y1="0" x2="40" y2="-80"/>
    
    <widget name="cover" x1="50" y1="50" x2="-50" y2="400"/>
    <widget name="trackinfo" x1="50" y1="440" x2="-50" y2="540"/>
  </arrangement>
"""



class AudioPlayer(Player):
    """
    Player component for playing audio files.
    """

    def __init__(self):
    
        self.__player = None
        self.__context_id = 0
        self.__volume = 0
        
        self.__need_slide_in = False
              
        self.__sliding_direction = self.SLIDE_LEFT

        self.__offscreen_buffer = None
        
        # the currently playing file object (e.g. used for bookmarking)
        self.__current_file = None
    
        Player.__init__(self)
        self.set_visible(False)
        
        # cover art
        self.__cover_art = CoverArt()
        self.__cover_art.connect_clicked(self.__on_btn_play)
        
        self.__trackinfo = VBox()
        
        # title label
        self.__lbl_title = Label("-", theme.font_mb_headline,
                                 theme.color_audio_player_trackinfo_title)
        #self.__lbl_title.set_alignment(Label.CENTERED)
        self.__trackinfo.add(self.__lbl_title, True)


        # artist and album labels
        self.__lbl_album = Label("-", theme.font_mb_plain,
                                 theme.color_audio_player_trackinfo_album)
        #self.__lbl_album.set_alignment(Label.CENTERED)
        self.__trackinfo.add(self.__lbl_album, True)

        self.__lbl_artist = Label("-", theme.font_mb_plain,
                                  theme.color_audio_player_trackinfo_artist)
        #self.__lbl_artist.set_alignment(Label.CENTERED)
        self.__trackinfo.add(self.__lbl_artist, True)
        
        
        # volume slider
        self.__volume_slider = Slider(theme.mb_list_slider)
        self.__volume_slider.set_mode(Slider.VERTICAL)
        self.__volume_slider.connect_value_changed(self.__on_change_volume)

        # progress bar
        self.__progress = ProgressBar()
        self.__progress.connect_changed(self.__on_seek)
        self.__progress.connect_bookmark_changed(self.__on_change_bookmark)

        # star button for bookmarks
        self.__btn_star = ImageButton(theme.mb_btn_bookmark_1,
                                      theme.mb_btn_bookmark_2)
        self.__btn_star.connect_clicked(self.__on_btn_star)


        # toolbar elements
        self.__btn_play = ImageButton(theme.mb_btn_play_1,
                                      theme.mb_btn_play_2)
        self.__btn_play.connect_clicked(self.__on_btn_play)

        btn_previous = ImageButton(theme.mb_btn_previous_1,
                                   theme.mb_btn_previous_2)
        btn_previous.connect_clicked(self.__on_btn_previous)

        btn_next = ImageButton(theme.mb_btn_next_1,
                               theme.mb_btn_next_2)
        btn_next.connect_clicked(self.__on_btn_next)
        
        # toolbar
        self.__toolbar = Toolbar()
        self.__toolbar.set_toolbar(btn_previous,
                                   self.__btn_play,
                                   btn_next)

        # arrangement
        self.__arr = Arrangement()
        self.__arr.connect_resized(self.__update_layout)
        self.__arr.add(self.__toolbar, "toolbar")
        self.__arr.add(self.__progress, "progress")
        self.__arr.add(self.__btn_star, "btn_star")
        self.__arr.add(self.__volume_slider, "slider")
        self.__arr.add(self.__cover_art, "cover")
        #self.__arr.add(self.__lbl_title, "lbl_title")
        self.__arr.add(self.__trackinfo, "trackinfo")
        self.add(self.__arr)


    def _reload(self):

        theme.color_mb_background.reload()


    def set_size(self, w, h):

        if ((w, h) != self.get_size()):
            self.__offscreen_buffer = Pixmap(None, w, h)
            
        Player.set_size(self, w, h)
        
        
    def __update_layout(self):
    
        w, h = self.get_size()
        if (w < h):
            self.__btn_star.set_visible(False)
            self.__arr.set_xml(_PORTRAIT_ARRANGEMENT)           
            self.__lbl_title.set_alignment(Label.CENTERED)
            self.__lbl_album.set_alignment(Label.CENTERED)
            self.__lbl_artist.set_alignment(Label.CENTERED)

        else:
            self.__btn_star.set_visible(True)
            self.__arr.set_xml(_LANDSCAPE_ARRANGEMENT)
            self.__lbl_title.set_alignment(Label.LEFT)
            self.__lbl_album.set_alignment(Label.LEFT)
            self.__lbl_artist.set_alignment(Label.LEFT)

        
    def get_mime_types(self):
    
        return ["application/ogg", "audio/*"]


    def __on_btn_play(self):
    
        if (self.__player):
            self.__player.pause()


    def __on_btn_previous(self):
        
        self.__sliding_direction = self.SLIDE_RIGHT
        self.emit_message(msgs.MEDIA_ACT_PREVIOUS)


    def __on_btn_star(self):
    
        print "ADDING BOOKMARK"
        self.__progress.add_bookmark()


    def __on_btn_next(self):
        
        self.__sliding_direction = self.SLIDE_LEFT
        self.emit_message(msgs.MEDIA_ACT_NEXT)
              
            
    def __on_change_player_status(self, ctx_id, status):
    
        if (ctx_id == self.__context_id):
            if (status == self.__player.STATUS_PLAYING):
                self.__btn_play.set_images(theme.mb_btn_pause_1,
                                           theme.mb_btn_pause_2)
                self.emit_message(msgs.MEDIA_EV_PLAY)

            elif (status == self.__player.STATUS_STOPPED):
                self.__btn_play.set_images(theme.mb_btn_play_1,
                                           theme.mb_btn_play_2)
                self.emit_message(msgs.MEDIA_EV_PAUSE)

            elif (status == self.__player.STATUS_EOF):
                self.__btn_play.set_images(theme.mb_btn_play_1,
                                           theme.mb_btn_play_2)
                self.emit_message(msgs.MEDIA_EV_EOF)
                self.emit_message(msgs.MEDIA_ACT_NEXT)
                
            elif (status == self.__player.STATUS_CONNECTING):
                self.__progress.set_message("Connecting")

            elif (status == self.__player.STATUS_BUFFERING):
                self.__progress.set_message("Buffering")


    def __on_change_bookmark(self):
    
        media_bookmarks.set_bookmarks(self.__current_file,
                                      self.__progress.get_bookmarks())



    def __on_error(self, ctx_id, err):
    
        if (ctx_id == self.__context_id and self.__player):
            self.emit_message(msgs.UI_ACT_SHOW_INFO, self.__player.ERRORS[err])


    def __on_seek(self, progress):
    
        if (self.__player):
            self.__player.seek_percent(progress)


    def __on_update_position(self, ctx_id, pos, total):
    
        if (ctx_id == self.__context_id):
            self.__progress.set_position(pos, total)
            self.__progress.set_message("%s / %s" \
                                        % (self.seconds_to_hms(pos),
                                           self.seconds_to_hms(total)))
            self.emit_message(msgs.MEDIA_EV_POSITION, pos, total)


    def __on_discovered_tags(self, ctx_id, tags):
    
        if (ctx_id == self.__context_id):
            title = tags.get("TITLE")
            album = tags.get("ALBUM")
            artist = tags.get("ARTIST")
            cover = tags.get("PICTURE")
            
            if (title):
                self.__lbl_title.set_text(title)
                self.emit_message(msgs.MEDIA_EV_TAG, "TITLE", title)
            if (album):
                self.__lbl_album.set_text(album)
                self.emit_message(msgs.MEDIA_EV_TAG, "ALBUM", album)
            if (artist):
                self.__lbl_artist.set_text(artist)
                self.emit_message(msgs.MEDIA_EV_TAG, "ARTIST", artist)
            if (cover):
                imageloader.load_data(cover, self.__on_loaded_cover,
                                      self.__context_id, time.time())
        #end if
        

    def __on_change_volume(self, v):
    
        if (self.__player):
            vol = int(v * 100)
            self.__player.set_volume(vol)
            self.__volume = vol

    
    def __on_change_player_volume(self, v):
    
        if (v != self.__volume):
            self.__volume_slider.set_value(v / 100.0)
            self.__volume = v


    def __on_loaded_cover(self, pbuf, ctx_id, t):
   
        if (ctx_id == self.__context_id):
            if (pbuf):
                self.__cover_art.set_cover(pbuf)
                self.emit_message(msgs.MEDIA_EV_TAG, "PICTURE", pbuf)
            else:
                self.__cover_art.unset_cover()
                self.emit_message(msgs.MEDIA_EV_TAG, "PICTURE", None)
        #end if
        logging.profile(t, "[audioplayer] loaded cover art")


    def __load_track_info(self, item):
    
        profile_now = time.time()
        tags = tagreader.get_tags(item)
        title = tags.get("TITLE") or item.name
        artist = tags.get("ARTIST") or "-"
        album = tags.get("ALBUM") or "-"
        logging.profile(profile_now, "[audioplayer] retrieved audio tags")

        self.__lbl_title.set_text(title)
        self.__lbl_artist.set_text(artist)
        self.__lbl_album.set_text(album)
        
        profile_now = time.time()
        self.emit_message(msgs.MEDIA_EV_TAG, "TITLE", title)
        self.emit_message(msgs.MEDIA_EV_TAG, "ARTIST", artist)
        self.emit_message(msgs.MEDIA_EV_TAG, "ALBUM", album)
        logging.profile(profile_now, "[audioplayer] propagated audio tags")

        if (self.__offscreen_buffer):
            self.render_buffered(self.__offscreen_buffer)

        # load cover art
        self.call_service(msgs.COVERSTORE_SVC_GET_COVER,
                          item, self.__on_loaded_cover, self.__context_id,
                          time.time())


    def __render_lyrics(self, words, hi_from, hi_to):
    
        self.__cover_art.set_lyrics(words, hi_from, hi_to)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        screen.fill_area(x, y, w, h, theme.color_mb_background)
        self.__arr.set_geometry(0, 0, w, h)
        
        
    def load(self, f):
        
        self.render()
        self.__player = self.call_service(msgs.MEDIA_SVC_GET_OUTPUT)
        self.__player.connect_status_changed(self.__on_change_player_status)
        self.__player.connect_volume_changed(self.__on_change_player_volume)
        self.__player.connect_position_changed(self.__on_update_position)
        self.__player.connect_tag_discovered(self.__on_discovered_tags)
        self.__player.connect_error(self.__on_error)

        """
        uri = item.get_resource()
        if (not uri.startswith("/") and
            not "://localhost" in uri and
            not "://127.0.0.1" in uri):                    
            maemo.request_connection()
        #end if
        """
        
        try:
            self.__context_id = self.__player.load_audio(f)
        except:
            logging.error("error loading media file: %s\n%s",
                          f, logging.stacktrace())

        self.__current_file = f
        self.__load_track_info(f)

        # load bookmarks
        self.__progress.set_bookmarks(media_bookmarks.get_bookmarks(f))

        self.emit_message(msgs.MEDIA_EV_LOADED, self, f)

        #self.__need_slide_in = True
        #gobject.timeout_add(100, self.__slide_in)


    def handle_MEDIA_EV_LYRICS(self, words, hi_from, hi_to):
    
        self.__render_lyrics(words, hi_from, hi_to)


    def handle_MEDIA_ACT_PLAY(self):
    
        if (self.__player and self.is_player_active()):
            self.__player.play()


    def handle_MEDIA_ACT_PAUSE(self):
    
        if (self.__player and self.is_player_active()):
            self.__player.pause()


    def handle_MEDIA_ACT_STOP(self):
    
        if (self.__player and self.is_player_active()):
            self.__player.stop()


    def handle_MEDIA_ACT_SEEK(self, pos):
    
        if (self.__player and self.is_player_active()):
            self.__player.seek(pos)


    def handle_INPUT_EV_VOLUME_UP(self, pressed):
    
        self.__volume = min(100, self.__volume + 5)
        self.__volume_slider.set_value(self.__volume / 100.0)
        if (self.__player):
            self.__player.set_volume(self.__volume)
        
        
    def handle_INPUT_EV_VOLUME_DOWN(self, pressed):

        self.__volume = max(0, self.__volume - 5)
        self.__volume_slider.set_value(self.__volume / 100.0)
        if (self.__player):
            self.__player.set_volume(self.__volume)


    def handle_INPUT_EV_PLAY(self, pressed):

        if (self.is_visible() and self.__player):
            self.__player.pause()


    def handle_COM_EV_APP_SHUTDOWN(self):
    
        if (self.__player):
            self.__player.close()

