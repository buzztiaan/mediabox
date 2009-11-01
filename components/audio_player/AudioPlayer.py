from com import Player, msgs
from ui.Toolbar import Toolbar
from ui.ImageButton import ImageButton
from ui.ProgressBar import ProgressBar
from ui.Slider import Slider
from ui.Image import Image
from ui.Label import Label
from ui.layout import Arrangement
from ui.layout import HBox, VBox
from ui.Pixmap import Pixmap
import mediaplayer
from mediabox.ShuffleBar import ShuffleBar
from mediabox import tagreader
from utils import logging
from theme import theme


_LANDSCAPE_ARRANGEMENT = """
  <arrangement>
    <widget name="toolbar" x1="-80" y1="0" x2="100%" y2="-80"/>
    <widget name="btn_nav" x1="-80" y1="-80" x2="100%" y2="100%"/>
    <widget name="shuffle_bar" x1="42" y1="-50" x2="128" y2="100%"/>
    <widget name="progress" x1="128" y1="-50" x2="-90" y2="100%"/>
    <widget name="slider" x1="0" y1="0" x2="40" y2="100%"/>
    
    <widget name="cover" x1="50" y1="10" x2="48%" y2="-80"/>
    <widget name="lbl_title" x1="50%" y1="10" x2="-90" y2="50"/>
    <widget name="trackinfo" x1="50%" y1="60" x2="-90" y2="160"/>
  </arrangement>
"""


class AudioPlayer(Player):

    def __init__(self):
    
        self.__player = None
        self.__context_id = 0
        self.__volume = 50
              
        self.__sliding_direction = self.SLIDE_LEFT
    
        Player.__init__(self)
        
        # cover art
        self.__cover_art = Image()
        
        # title label
        self.__lbl_title = Label("-", theme.font_mb_headline,
                                 theme.color_mb_trackinfo_text)
        #self.add(self.__lbl_title)


        # artist and album labels
        self.__trackinfo = VBox()
        #self.add(self.__trackinfo)
        
        hbox = HBox()
        hbox.set_spacing(24)
        self.__trackinfo.add(hbox, True)
        img = Image(theme.mb_music_album)
        img.set_size(48, 48)
        hbox.add(img, False)
        self.__lbl_album = Label("-", theme.font_mb_plain,
                                 theme.color_mb_trackinfo_text)
        hbox.add(self.__lbl_album, True)

        hbox = HBox()
        hbox.set_spacing(24)
        self.__trackinfo.add(hbox, True)
        img = Image(theme.mb_music_artist)
        img.set_size(48, 48)
        hbox.add(img, False)
        self.__lbl_artist = Label("-", theme.font_mb_plain,
                                  theme.color_mb_trackinfo_text)
        hbox.add(self.__lbl_artist, True)
        
        
        # volume slider
        self.__volume_slider = Slider(theme.mb_list_slider)
        self.__volume_slider.set_mode(Slider.VERTICAL)
        self.__volume_slider.connect_value_changed(self.__on_change_volume)
        #self.add(self.__volume_slider)
        
        # shuffle and repeat
        self.__shuffle_bar = ShuffleBar()
        #self.add(self.__shuffle_bar)

        # navigator button
        self.__btn_navigator = ImageButton(theme.mb_btn_play_1,
                                           theme.mb_btn_play_2)
        self.__btn_navigator.connect_clicked(lambda *a:self.get_window().close())
        #self.add(self.__btn_navigator)

        # toolbar
        self.__toolbar = Toolbar()
        #self.add(self.__toolbar)
        
        self.__btn_play = ImageButton(theme.mb_btn_play_1,
                                      theme.mb_btn_play_2)
        self.__btn_play.connect_clicked(self.__on_btn_play)

        btn_previous = ImageButton(theme.mb_btn_previous_1,
                                   theme.mb_btn_previous_2)
        btn_previous.connect_clicked(self.__on_btn_previous)

        btn_next = ImageButton(theme.mb_btn_next_1,
                               theme.mb_btn_next_2)
        btn_next.connect_clicked(self.__on_btn_next)

        btn_bookmark = ImageButton(theme.mb_btn_bookmark_1,
                                   theme.mb_btn_bookmark_2)
        btn_bookmark.connect_clicked(self.__on_btn_next)


        # progress bar
        self.__progress = ProgressBar()
        #self.add(self.__progress)
        self.__progress.connect_changed(self.__on_seek)

        self.__toolbar.set_toolbar(btn_previous,
                                   self.__btn_play,
                                   btn_next)
                                   #btn_bookmark)

        # arrangement
        self.__arr = Arrangement()
        self.__arr.connect_resized(self.__update_layout)
        self.__arr.add(self.__toolbar, "toolbar")
        self.__arr.add(self.__btn_navigator, "btn_nav")
        self.__arr.add(self.__shuffle_bar, "shuffle_bar")
        self.__arr.add(self.__progress, "progress")
        self.__arr.add(self.__volume_slider, "slider")
        self.__arr.add(self.__cover_art, "cover")
        self.__arr.add(self.__lbl_title, "lbl_title")
        self.__arr.add(self.__trackinfo, "trackinfo")
        self.add(self.__arr)
        
        
    def __update_layout(self):
    
        w, h = self.get_size()
        if (w < h):
            # portrait mode
            self.__arr.set_xml(_LANDSCAPE_ARRANGEMENT)           
        else:
            # landscape mode
            self.__arr.set_xml(_LANDSCAPE_ARRANGEMENT)

        
    def get_mime_types(self):
    
        return ["application/ogg", "audio/*"]


    def __on_btn_play(self):
    
        if (self.__player):
            self.__player.pause()


    def __on_btn_previous(self):
        
        self.__sliding_direction = self.SLIDE_RIGHT
        self.emit_message(msgs.MEDIA_ACT_PREVIOUS)


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


    def __on_seek(self, progress):
    
        if (self.__player):
            self.__player.seek_percent(progress)


    def __on_update_position(self, ctx_id, pos, total):
    
        if (ctx_id == self.__context_id):
            self.__progress.set_position(pos, total)
            self.__progress.set_message("%s / %s" \
                                        % (self.seconds_to_hms(pos),
                                           self.seconds_to_hms(total)))


    def __on_change_volume(self, v):
    
        if (self.__player):
            vol = int(v * 100)
            self.__player.set_volume(vol)
            self.__volume = vol
        


    def __on_loaded_cover(self, pbuf, ctx_id):
   
        if (pbuf and ctx_id == self.__context_id):
            #if (self.__cover):
            #    del self.__cover

            #self.__cover = pbuf
            self.__cover_art.set_image(pbuf)
            self.render()
        #end if


    def __load_track_info(self, item):
    
        tags = tagreader.get_tags(item)
        title = tags.get("TITLE") or item.name
        artist = tags.get("ARTIST") or "-"
        album = tags.get("ALBUM") or "-"
            
        self.__lbl_title.set_text(title)
        self.__lbl_artist.set_text(artist)
        self.__lbl_album.set_text(album)

        # load cover art
        self.call_service(msgs.COVERSTORE_SVC_GET_COVER,
                          item, self.__on_loaded_cover, self.__context_id)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        screen.fill_area(x, y, w, h, theme.color_mb_background)
        self.__arr.set_geometry(0, 0, w, h)

        """
        if (w < h):
            # portrait mode
            cover_size = w - 84
            self.__toolbar.set_geometry(0, h - 80, w - 80, 80)
            self.__btn_navigator.set_geometry(w - 80, h - 80, 80, 80)
            self.__progress.set_geometry(42 + 20, h - (80 + 50), w - 84 - 40, 32)
            lbl_width = w - cover_size - 42
            self.__lbl_title.set_geometry(42, cover_size + 20, w - 84, 0)
            self.__lbl_title.set_alignment(Label.CENTERED)
            self.__trackinfo.set_geometry(42, cover_size + 60, w - 84, 80)
            self.__volume_slider.set_geometry(0, 0, 42, h - 80)

        else:
            # landscape mode
            cover_size = h - 90
            self.__toolbar.set_geometry(w - 80, 0, 80, h - 80)
            self.__btn_navigator.set_geometry(w - 80, h - 80, 80, 80)
            self.__shuffle_bar.set_geometry(42, h - 50, 128, 50)
            self.__progress.set_geometry(42 + 20 + 128, h - 50, w - (80 + 84 + 40) - 128, 32)
            lbl_width = w - cover_size - 42 - 80
            self.__lbl_title.set_geometry(w - lbl_width - 80 + 10, 10,
                                          lbl_width - 20, 0)
            self.__lbl_title.set_alignment(Label.LEFT)
            self.__trackinfo.set_geometry(w - lbl_width - 80 + 10, 60,
                                          lbl_width - 20, 80)
            self.__volume_slider.set_geometry(0, 0, 42, h)
        """

        """
        if (self.__cover):
            screen.fit_pixbuf(self.__cover,
                              x + 42, y + 10,
                              cover_size, cover_size)
        else:
            screen.draw_rect(x + 42, y + 10, cover_size, cover_size,
                             "#000000")
            screen.fill_area(x + 44, y + 12, cover_size - 4, cover_size - 4,
                             "#aaaaaa")
        """


        
        
    def load(self, f):
    
        self.__player = self.call_service(msgs.MEDIA_SVC_GET_OUTPUT)
        #self.__player = mediaplayer.get_player_for_mimetype(f.mimetype)
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
            self.__context_id = self.__player.load_audio(f)
        except:
            logging.error("error loading media file: %s\n%s",
                          uri, logging.stacktrace())


        self.set_frozen(True)
        self.__load_track_info(f)
        self.set_frozen(False)
        
        if (self.may_render()):
            x, y = self.get_screen_pos()
            w, h = self.get_size()
            buf = Pixmap(None, w, h)
            self.render_at(buf)
            if (w < h):
                # portrait mode
                self.fx_slide_horizontal(buf, x + 42, y, w - 84, h - (70 + 70),
                                         self.__sliding_direction)
            else:
                # landscape mode
                self.fx_slide_horizontal(buf, x + 42, y, w - (42 + 70), h - 70,
                                         self.__sliding_direction)

            self.__sliding_direction = self.SLIDE_LEFT
        #end if
        self.emit_message(msgs.MEDIA_EV_LOADED, self, f)

        #self.render()



    def handle_INPUT_EV_VOLUME_UP(self):
    
        self.__volume = min(100, self.__volume + 5)
        self.__volume_slider.set_value(self.__volume / 100.0)
        if (self.__player):
            self.__player.set_volume(self.__volume)
        
        
    def handle_INPUT_EV_VOLUME_DOWN(self):
    
        self.__volume = max(0, self.__volume - 5)
        self.__volume_slider.set_value(self.__volume / 100.0)
        if (self.__player):
            self.__player.set_volume(self.__volume)

