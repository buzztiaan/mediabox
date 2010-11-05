from com import Player, msgs
from InfoBox import InfoBox
from ui.ToolbarButton import ToolbarButton
from ui.ImageButton import ImageButton
from ui.MediaProgressBar import MediaProgressBar
from ui.Slider import Slider
from ui.Toolbar import Toolbar
from ui.layout import Arrangement
from ui.Pixmap import Pixmap
from mediabox import media_bookmarks
from mediabox import tagreader
from mediabox import imageloader
from utils import logging
from utils import textutils
from theme import theme

import gobject
import gtk
import time
import threading


_LANDSCAPE_ARRANGEMENT = """
  <arrangement>
    <widget name="slider" x1="0" y1="0" x2="40" y2="-172"/>
    <widget name="toolbar" x1="-100" y1="0" x2="100%" y2="100%"/>
    <widget name="trackinfo" x1="0" y1="-100" x2="-100" y2="100%"/>
    <widget name="progress" x1="0" y1="-172" x2="-100" y2="-100"/>
  </arrangement>
"""


_PORTRAIT_ARRANGEMENT = """
  <arrangement>
    <widget name="slider" x1="0" y1="0" x2="40" y2="-272"/>
    <widget name="toolbar" x1="0" y1="-100" x2="100%" y2="100%"/>
    <widget name="trackinfo" x1="0" y1="-200" x2="100%" y2="-100"/>
    <widget name="progress" x1="0" y1="-272" x2="100%" y2="-200"/>
  </arrangement>
"""



class AudioPlayer(Player):
    """
    Player component for playing audio files.
    """

    def __init__(self):
    
        # cover pixbuf
        self.__cover = None
        self.__cover_scaled = None
        
        # lyrics text with hilights formatting
        self.__lyrics = ""
    
        self.__player = None
        self.__context_id = 0
        self.__volume = 0
        
        self.__offscreen_buffer = None
        
        # the currently playing file object (e.g. used for bookmarking)
        self.__current_file = None
    
        Player.__init__(self)
        self.set_visible(False)
        
        self.__trackinfo = InfoBox()        
        
        # volume slider
        self.__volume_slider = Slider(theme.mb_list_slider)
        self.__volume_slider.set_mode(Slider.VERTICAL)
        self.__volume_slider.connect_value_changed(self.__on_change_volume)

        # progress bar
        self.__progress = MediaProgressBar(MediaProgressBar.DOWN)
        self.__progress.connect_changed(self.__on_seek)
        self.__progress.connect_bookmark_changed(self.__on_change_bookmark)

        # star button for bookmarks
        self.__btn_star = ImageButton(theme.mb_btn_bookmark_1,
                                      theme.mb_btn_bookmark_2)
        self.__btn_star.connect_clicked(self.__on_btn_star)


        # toolbar elements
        self.__btn_play = ToolbarButton(theme.mb_btn_play_1)
        self.__btn_play.connect_clicked(self.__on_btn_play)

        btn_previous = ToolbarButton(theme.mb_btn_previous_1)
        btn_previous.connect_clicked(self.__on_btn_previous)

        btn_next = ToolbarButton(theme.mb_btn_next_1)
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
        #self.__arr.add(self.__btn_star, "btn_star")
        self.__arr.add(self.__volume_slider, "slider")
        self.__arr.add(self.__trackinfo, "trackinfo")
        self.add(self.__arr)


    def _reload(self):

        theme.color_mb_background.reload()


    def set_size(self, w, h):

        if ((w, h) != self.get_size()):
            self.__offscreen_buffer = Pixmap(None, w, h)
            self.__cover_scaled = None
            
        Player.set_size(self, w, h)
        
        
    def __update_layout(self):
    
        w, h = self.get_size()
        if (w < h):
            #self.__btn_star.set_visible(False)
            self.__arr.set_xml(_PORTRAIT_ARRANGEMENT)           

        else:
            #self.__btn_star.set_visible(True)
            self.__arr.set_xml(_LANDSCAPE_ARRANGEMENT)


    def __set_cover(self, pbuf):
    
        if (not self.__cover):
            self.__cover = pbuf
            self.__cover_scaled = None


    def __set_lyrics(self, words, hi_from, hi_to):
    
        if (hi_from > 0 or hi_to < len(words) - 1):
            self.__lyrics = "%s<span color='red'>%s</span>%s" \
                            % (textutils.escape_xml(words[:hi_from]),
                            textutils.escape_xml(words[hi_from:hi_to]),
                            textutils.escape_xml(words[hi_to:]))
        else:
            self.__lyrics = textutils.escape_xml(words)


        
    def get_mime_types(self):
    
        return ["application/ogg", "audio/*"]


    def __on_btn_play(self):
    
        if (self.__player):
            self.__player.pause()


    def __on_btn_previous(self):
        
        self.emit_message(msgs.MEDIA_ACT_PREVIOUS)


    def __on_btn_star(self):
    
        print "ADDING BOOKMARK"
        self.__progress.add_bookmark()


    def __on_btn_next(self):
        
        self.emit_message(msgs.MEDIA_ACT_NEXT)
              
            
    def __on_change_player_status(self, ctx_id, status):
    
        if (ctx_id == self.__context_id):
            if (status == self.__player.STATUS_PLAYING):
                self.__btn_play.set_icon(theme.mb_btn_pause_1)
                self.emit_message(msgs.MEDIA_EV_PLAY)

            elif (status == self.__player.STATUS_STOPPED):
                self.__btn_play.set_icon(theme.mb_btn_play_1)
                self.emit_message(msgs.MEDIA_EV_PAUSE)

            elif (status == self.__player.STATUS_EOF):
                self.__btn_play.set_icon(theme.mb_btn_play_1)
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
                self.__trackinfo.set_title(title)
                self.emit_message(msgs.MEDIA_EV_TAG, "TITLE", title)
            if (album):
                self.__trackinfo.set_album(album)
                self.emit_message(msgs.MEDIA_EV_TAG, "ALBUM", album)
            if (artist):
                self.__trackinfo.set_artist(artist)
                self.emit_message(msgs.MEDIA_EV_TAG, "ARTIST", artist)
            if (cover and not self.__cover):
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


    def __on_loaded_cover(self, pbuf, ctx_id, stopwatch):
   
        if (ctx_id == self.__context_id):
            self.__cover = None
            if (pbuf):
                self.__set_cover(pbuf)
                self.emit_message(msgs.MEDIA_EV_TAG, "PICTURE", pbuf)
            else:
                self.__cover = None
                self.__cover_scaled = None
                self.emit_message(msgs.MEDIA_EV_TAG, "PICTURE", None)

            if (self.__offscreen_buffer):
                self.render_buffered(self.__offscreen_buffer)
        #end if
        logging.profile(stopwatch, "[audioplayer] loaded cover art")


    def __load_track_info(self, item):
    
        stopwatch = logging.stopwatch()
        tags = tagreader.get_tags(item)
        logging.profile(stopwatch, "[audioplayer] retrieved audio tags")

        gobject.timeout_add(0, self.__on_track_info, item, tags)


    def __on_track_info(self, item, tags):

        logging.debug("[audioplayer] processing track info")
        title = tags.get("TITLE") or item.name
        artist = tags.get("ARTIST") or "-"
        album = tags.get("ALBUM") or "-"

        self.__trackinfo.set_title(title)
        self.__trackinfo.set_album(album)
        self.__trackinfo.set_artist(artist)
        
        if (self.__offscreen_buffer):
            self.render_buffered(self.__offscreen_buffer)

        # load cover art
        self.call_service(msgs.COVERSTORE_SVC_GET_COVER,
                          item, self.__on_loaded_cover, self.__context_id,
                          logging.stopwatch())

        stopwatch = logging.stopwatch()
        self.emit_message(msgs.MEDIA_EV_TAG, "TITLE", title)
        self.emit_message(msgs.MEDIA_EV_TAG, "ARTIST", artist)
        self.emit_message(msgs.MEDIA_EV_TAG, "ALBUM", album)
        logging.profile(stopwatch, "[audioplayer] propagated audio tags")



    def __scale_cover(self):

        w, h = self.get_size()
        if (w < h):
            h -= (100 + 100)
        else:
            w -= 100
            h -= 100
            
        p_w = self.__cover.get_width()
        p_h = self.__cover.get_height()
        
        factor1 = w / float(p_w)
        factor2 = h / float(p_h)
        print (p_w, p_h), (w, h), factor1, factor2
        
        if (p_h * factor1 < h):
            factor = factor2
        else:
            factor = factor1
        
        s_w = int(w / factor)
        s_h = int(h / factor)
        
        crop_x = (p_w - s_w) / 2
        crop_y = (p_h - s_h) / 3
        crop_w = s_w
        crop_h = s_h
        print "CROP", (crop_x, crop_y), (crop_w, crop_h), "->", (w, h)

        self.__cover_scaled = self.__cover.subpixbuf(crop_x, crop_y,
                                                     crop_w, crop_h) \
                                          .scale_simple(w, h,
                                                        gtk.gdk.INTERP_BILINEAR)


    def __render_lyrics(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        if (self.__lyrics):
            #self.__buffer.draw_frame(theme.mb_lyrics_box, bx, by, bw, bh, True)
            screen.fill_area(x + 8, y + 8, w - 16, 200, "#000000a0")
            screen.draw_formatted_text(self.__lyrics, theme.font_mb_headline,
                                       x + 8, y + 8, w - 16, 200,
                                       theme.color_audio_player_lyrics,
                                       screen.LEFT,
                                       True)


    def __render_background(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        if (w < h):
            h -= (100 + 100)
        else:
            w -= 100
            h -= 100
    
        if (self.__cover):
            if (not self.__cover_scaled):
                self.__scale_cover()

            screen.draw_pixbuf(self.__cover_scaled, x, y)
            #screen.fill_area(x, y, w, h, "#000000a0")

            self.__volume_slider.set_background(
                               self.__cover_scaled.subpixbuf(0, 0, 40, h - 72))
            self.__progress.set_background(
                               self.__cover_scaled.subpixbuf(0, h - 72, w, 72))


        else:
            screen.fill_area(x, y, w, h, theme.color_mb_background)
            p_w = theme.mb_unknown_album.get_width()
            p_h = theme.mb_unknown_album.get_height()
            screen.draw_pixbuf(theme.mb_unknown_album,
                               x + (w - p_w) / 2,
                               y + (h - p_h) / 2)
            self.__volume_slider.set_background(None)
            self.__progress.set_background(None)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        self.__render_background()      
        self.__render_lyrics()      
            
        self.__arr.set_geometry(0, 0, w, h)
        #x, y = self.__progress.get_screen_pos()
        #w, h = self.__progress.get_size()
        #self.__progress.set_background(screen.subpixmap(x, y, w, h))
        
        
    def load(self, f):

        stopwatch = logging.stopwatch()
        self.__player = self.call_service(msgs.MEDIA_SVC_GET_OUTPUT)
        self.__player.connect_status_changed(self.__on_change_player_status)
        self.__player.connect_volume_changed(self.__on_change_player_volume)
        self.__player.connect_position_changed(self.__on_update_position)
        self.__player.connect_tag_discovered(self.__on_discovered_tags)
        self.__player.connect_error(self.__on_error)
        logging.profile(stopwatch, "[audioplayer] connected audio output")
        
        try:
            stopwatch = logging.stopwatch()
            self.__context_id = self.__player.load_audio(f)
            logging.profile(stopwatch, "[audioplayer] loaded media file: %s", f)
        except:
            logging.error("error loading media file: %s\n%s",
                          f, logging.stacktrace())

        stopwatch = logging.stopwatch()
        self.__current_file = f
        logging.profile(stopwatch, "[audioplayer] loaded track info")

        # load bookmarks
        self.__progress.set_bookmarks(media_bookmarks.get_bookmarks(f))

        self.emit_message(msgs.MEDIA_EV_LOADED, self, f)

        t = threading.Thread(target = self.__load_track_info, args = [f])
        t.setDaemon(True)
        t.start()
        
        if (self.__offscreen_buffer):
            self.render_buffered(self.__offscreen_buffer)


    def handle_MEDIA_EV_LYRICS(self, words, hi_from, hi_to):
    
        self.__set_lyrics(words, hi_from, hi_to)
        if (self.__offscreen_buffer):
            self.render_buffered(self.__offscreen_buffer)


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

