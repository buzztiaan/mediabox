from com import Player, msgs
from ui.ImageButton import ImageButton
from ui.ProgressBar import ProgressBar
from ui.Slider import Slider
from ui.Image import Image
from ui.Label import Label
from ui.Toolbar import Toolbar
from ui.layout import Arrangement
from ui.layout import HBox, VBox
from ui.Pixmap import Pixmap
from mediabox import tagreader
from utils import textutils
from utils import logging
from theme import theme

import gobject


_LANDSCAPE_ARRANGEMENT = """
  <arrangement>
    <widget name="btn_nav" x1="0" y1="-64" x2="64" y2="100%"/>
    <widget name="progress" x1="90" y1="-50" x2="-90" y2="-10"/>
    <widget name="toolbar" x1="-80" y1="0" x2="100%" y2="100%"/>
    <widget name="slider" x1="0" y1="0" x2="40" y2="-64"/>
    
    <widget name="cover" x1="50" y1="10" x2="48%" y2="-64"/>
    <widget name="trackinfo" x1="50%" y1="160" x2="-90" y2="260"/>
  </arrangement>
"""


_PORTRAIT_ARRANGEMENT = """
  <arrangement>
    <widget name="btn_nav" x1="-64" y1="0" x2="100%" y2="64"/>
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
        
        # offscreen buffer
        self.__buffer = None
        self.__screen = None
        
        self.__need_slide_in = False
              
        self.__sliding_direction = self.SLIDE_LEFT
    
        Player.__init__(self)
        
        # cover art
        self.__cover_art = Image()
        self.__cover_art.connect_clicked(self.__on_btn_play)
        
        self.__trackinfo = VBox()
        
        # title label
        self.__lbl_title = Label("-", theme.font_mb_headline,
                                 theme.color_audio_player_trackinfo_title)
        self.__lbl_title.set_alignment(Label.CENTERED)
        self.__trackinfo.add(self.__lbl_title, True)


        # artist and album labels
        self.__lbl_album = Label("-", theme.font_mb_plain,
                                 theme.color_audio_player_trackinfo_album)
        self.__lbl_album.set_alignment(Label.CENTERED)
        self.__trackinfo.add(self.__lbl_album, True)

        self.__lbl_artist = Label("-", theme.font_mb_plain,
                                  theme.color_audio_player_trackinfo_artist)
        self.__lbl_artist.set_alignment(Label.CENTERED)
        self.__trackinfo.add(self.__lbl_artist, True)
        
        
        # volume slider
        self.__volume_slider = Slider(theme.mb_list_slider)
        self.__volume_slider.set_mode(Slider.VERTICAL)
        self.__volume_slider.connect_value_changed(self.__on_change_volume)
        
        # navigator button
        self.__btn_navigator = ImageButton(theme.mb_btn_navigator_1,
                                           theme.mb_btn_navigator_2)
        self.__btn_navigator.connect_clicked(self.__on_btn_navigator)

        # progress bar
        self.__progress = ProgressBar()
        self.__progress.connect_changed(self.__on_seek)


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
        self.__arr.add(self.__btn_navigator, "btn_nav")
        self.__arr.add(self.__toolbar, "toolbar")
        self.__arr.add(self.__progress, "progress")
        self.__arr.add(self.__volume_slider, "slider")
        self.__arr.add(self.__cover_art, "cover")
        #self.__arr.add(self.__lbl_title, "lbl_title")
        self.__arr.add(self.__trackinfo, "trackinfo")
        self.add(self.__arr)
        
        
    def __update_layout(self):
    
        w, h = self.get_size()
        if (w < h):
            self.__arr.set_xml(_PORTRAIT_ARRANGEMENT)           
        else:
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


    def __on_btn_navigator(self):
    
        self.emit_message(msgs.UI_ACT_SHOW_DIALOG, "navigator.Navigator")
              
            
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


    def __on_error(self, ctx_id, err):
    
        if (ctx_id == self.__context_id):
            # TODO: display readable text here...
            self.emit_message(msgs.UI_ACT_SHOW_INFO, `err`)


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
            
            if (title):
                self.__lbl_title.set_text(title)
            if (album):
                self.__lbl_album.set_text(album)
            if (artist):
                self.__lbl_artist.set_text(artist)
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


    def __on_loaded_cover(self, pbuf, ctx_id):
   
        print "LOADED COVER", pbuf, ctx_id, self.__context_id, self.__buffer
        if (not pbuf):
            pbuf = theme.mb_unknown_album
   
        if (ctx_id == self.__context_id):
            #if (self.__cover):
            #    del self.__cover

            #self.__cover = pbuf
            print "SETTING COVER"
            self.__cover_art.set_image(pbuf)
            if (self.__buffer):
                if (self.__need_slide_in):
                    self.__slide_in()
                else:
                    self.render_buffered(self.__buffer)
            #end if
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


    def set_size(self, w, h):
    
        old_w, old_h = self.get_size()
        if ((old_w, old_h) != (w, h)):
            Player.set_size(self, w, h)
            self.__buffer = Pixmap(None, w, h)
        #end if


    def __render_lyrics(self, words, hi_from, hi_to):
    
        cx, cy = self.__cover_art.get_screen_pos()
        cw, ch = self.__cover_art.get_size()
        
        self.__buffer.fill_area(cx, cy, cw, ch, theme.color_mb_background)
        self.__cover_art.render_at(self.__buffer, cx, cy)

        if (hi_from > 0 or hi_to < len(words) - 1):
            text = "%s<span color='red'>%s</span>%s" \
                   % (textutils.escape_xml(words[:hi_from]),
                      textutils.escape_xml(words[hi_from:hi_to]),
                      textutils.escape_xml(words[hi_to:]))
        else:
            text = textutils.escape_xml(words)
        
        bx = cx
        by = cy + ch - 16 - 130
        bw = cw
        bh = 130
        #print text, hi_from, hi_to

        self.__buffer.draw_frame(theme.mb_lyrics_box, bx, by, bw, bh, True)
        self.__buffer.draw_formatted_text(text, theme.font_mb_headline,
                                            bx + 8, by + 8, bw - 16, bh - 16,
                                            theme.color_audio_player_lyrics,
                                            self.__buffer.LEFT,
                                            True)

        self.get_screen().copy_buffer(self.__buffer, bx, by, bx, by, bw, bh)



    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        screen.fill_area(x, y, w, h, theme.color_mb_background)
        self.__arr.set_geometry(0, 0, w, h)


    def __slide_in(self):
    
        if (not self.__need_slide_in or 
              not self.may_render() or
              not self.__buffer):
            return
    
        self.__need_slide_in = False
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        self.set_screen(self.__screen)
        buf = self.__buffer
        
        self.render_at(buf)
        x = 0
        y = 0
        if (w < h):
            # portrait mode
            self.fx_slide_horizontal(buf, x + 40, y, w - 40, h - 80,
                                        self.__sliding_direction)
        else:
            # landscape mode
            self.fx_slide_horizontal(buf, x + 40, y, w - 40 - 80, h - 64,
                                        self.__sliding_direction)

        self.__sliding_direction = self.SLIDE_LEFT
        self.render_buffered(buf)
        

        
    def load(self, f):
        
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
        
        uri = f.get_resource()
        try:
            self.__context_id = self.__player.load_audio(f)
        except:
            logging.error("error loading media file: %s\n%s",
                          uri, logging.stacktrace())

        self.__screen = self.get_screen()
        self.set_screen(self.__buffer)
        self.__load_track_info(f)

        self.emit_message(msgs.MEDIA_EV_LOADED, self, f)

        self.__need_slide_in = True
        gobject.timeout_add(100, self.__slide_in)


    def handle_MEDIA_EV_LYRICS(self, words, hi_from, hi_to):
    
        self.__render_lyrics(words, hi_from, hi_to)


    def handle_MEDIA_ACT_PAUSE(self):
    
        if (self.__player):
            self.__player.pause()


    def handle_MEDIA_ACT_STOP(self):
    
        if (self.__player):
            self.__player.stop()


    def handle_INPUT_EV_VOLUME_UP(self):
    
        if (self.is_visible()):
            self.__volume = min(100, self.__volume + 5)
            self.__volume_slider.set_value(self.__volume / 100.0)
            if (self.__player):
                self.__player.set_volume(self.__volume)
        
        
    def handle_INPUT_EV_VOLUME_DOWN(self):

        if (self.is_visible()):    
            self.__volume = max(0, self.__volume - 5)
            self.__volume_slider.set_value(self.__volume / 100.0)
            if (self.__player):
                self.__player.set_volume(self.__volume)

