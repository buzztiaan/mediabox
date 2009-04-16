from com import msgs
from mediabox.MediaWidget import MediaWidget
from mediabox import media_bookmarks
from mediabox import tagreader
from mediabox import config as mb_config
from ui.Button import Button
from ui.EventBox import EventBox
from ui.ImageButton import ImageButton
from ui.Image import Image
from ui.ProgressBar import ProgressBar
from ui.Label import Label
from ui.Pixmap import TEMPORARY_PIXMAP
from ui import pixbuftools
from ui import dialogs
import mediaplayer
from utils import maemo
from theme import theme

import gtk
import gobject
import os


class AudioWidget(MediaWidget):
    """
    Media widget for playing audio files.
    """

    def __init__(self):
    
        self.__player = None
        self.__load_handler = None
        mediaplayer.add_observer(self.__on_observe_player)

        self.__current_file = None
        self.__context_id = 0

        MediaWidget.__init__(self)


        self.__cover_pbuf = None
        self.__buffer = TEMPORARY_PIXMAP
        
        self.__title = Label("-", theme.font_mb_headline,
                             theme.color_mb_trackinfo_text)
        #self.__title.set_alignment(Label.CENTERED)
        self.add(self.__title)

        self.__album = Label("-", theme.font_mb_plain,
                             theme.color_mb_trackinfo_text)
        self.add(self.__album)

        self.__artist = Label("-", theme.font_mb_plain,
                              theme.color_mb_trackinfo_text)
        self.add(self.__artist)

        self.__lyrics = Label("", theme.font_mb_trackinfo_lyrics,
                              theme.color_mb_trackinfo_text)
        self.__lyrics.set_alignment(Label.CENTERED)
        #self.__lyrics = Button("")
        self.add(self.__lyrics)


        self.__progress_label = Label("", theme.font_mb_headline,
                                      theme.color_mb_trackinfo_text)
        self.add(self.__progress_label)
        self.__progress_label.set_alignment(Label.RIGHT)

        self.__cover = ImageButton(theme.mb_btn_play_1,
                                   theme.mb_btn_play_2,
                                   True)
        self.add(self.__cover)
        self.__cover.connect_clicked(self.__on_play_pause)
        
        
        # controls
        self.__btn_play = ImageButton(theme.mb_btn_play_1,
                                      theme.mb_btn_play_2)
        self.__btn_play.connect_clicked(self.__on_play_pause)

        self.__progress = ProgressBar()
        self.__progress.connect_changed(self.__on_set_position)
        self.__progress.connect_bookmark_changed(self.__on_change_bookmark)

        btn_bookmark = ImageButton(theme.mb_btn_bookmark_1,
                                   theme.mb_btn_bookmark_2)
        btn_bookmark.connect_clicked(self.__on_add_bookmark)
        
        self._set_controls(Image(theme.mb_toolbar_space_1),
                           self.__btn_play,
                           Image(theme.mb_toolbar_space_2),
                           self.__progress,
                           Image(theme.mb_toolbar_space_2),
                           btn_bookmark,
                           Image(theme.mb_toolbar_space_1))

        # car controls
        self.__car_btn_prev = ImageButton(theme.mb_btn_car_previous_1,
                                          theme.mb_btn_car_previous_2)
        self.__car_btn_prev.connect_clicked(
                                    self.send_event, self.EVENT_MEDIA_PREVIOUS)
        self.add(self.__car_btn_prev)

        self.__car_btn_next = ImageButton(theme.mb_btn_car_next_1,
                                          theme.mb_btn_car_next_2)
        self.__car_btn_next.connect_clicked(
                                        self.send_event, self.EVENT_MEDIA_NEXT)
        self.add(self.__car_btn_next)
        


        

    def set_size(self, w, h):
    
        old_w, old_h = self.get_size()
        MediaWidget.set_size(self, w, h)
        if ((w, h) != (old_w, old_h)):
            self.__prepare_cover()

    def _reload(self):
    
        self.__prepare_cover()


    def handle_message(self, msg, *args):
    
        if (msg == msgs.MEDIA_EV_LYRICS):
            words, hi_from, hi_to = args
            self.__lyrics.set_text(words)
                                   #words[:hi_from] +\
                                   #"[" + words[hi_from:hi_to] + "]" + \
                                   #words[hi_to:])

        elif (msg == msgs.MEDIA_EV_DOWNLOAD_PROGRESS):
            f, amount, total = args
            if (f == self.__current_file and total > 0):
                percent = int(float(amount) / total * 100)
                self.__progress.set_message("... loading (%d%%)..." % percent)



    def render_this(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        screen.fill_area(x, y, w, h, theme.color_mb_trackinfo_background)
        
        if (w < 800):
            self.__car_btn_prev.set_visible(False)
            self.__car_btn_next.set_visible(False)
            self.__progress_label.set_visible(False)
            border_width = 10
        else:
            self.__car_btn_prev.set_visible(True)
            self.__car_btn_next.set_visible(True)
            self.__progress_label.set_visible(True)
            self.__car_btn_prev.set_geometry(0, 50, 128, h - 100)
            self.__car_btn_next.set_geometry(w - 128, 50, 128, h - 100)
            self.__progress_label.set_geometry(w - 200, h - 90, 190, 0)
            border_width = 10

        # top and bottom borders
        screen.fill_area(x, y, w, 50,
                         theme.color_mb_trackinfo_background_2)
        screen.fill_area(x, y + h - 50, w, 50,
                         theme.color_mb_trackinfo_background_2)
                
        # title label
        lbl_x = 10
        lbl_y = 6
        lbl_w = w - 2 * 20
        self.__title.set_geometry(lbl_x, lbl_y, lbl_w, 0)       

        # lyrics label
        lbl_x = 10
        lbl_y = h - 42
        lbl_w = w - 20
        self.__lyrics.set_geometry(lbl_x, lbl_y, lbl_w, 0)

        # album label
        lbl_x = w / 2
        lbl_y = 64 #h - 42
        lbl_w = w / 2 - 2 * border_width
        screen.draw_pixbuf(theme.mb_music_album, x + lbl_x, y + lbl_y)
        self.__album.set_geometry(lbl_x + 48, lbl_y + 4, lbl_w -48, 0)
        
        # artist label
        lbl_y = 112
        screen.draw_pixbuf(theme.mb_music_artist, x + lbl_x, y + lbl_y)
        self.__artist.set_geometry(lbl_x + 48, lbl_y + 4, lbl_w - 48, 0)

        
        # cover art
        cover_size = min(h - 128, w / 2 - 2 * border_width)
        cover_x = (w / 2 - cover_size) / 2 #20 #(w - cover_size) / 2
        cover_y = 60

        self.__cover.set_geometry(cover_x, cover_y,
                                  cover_size + 11, cover_size + 11)
                                               


    def __prepare_cover(self):

        w, h = self.get_size()
    
        if (w <= 0 or h <= 0): return
    
        cover_size = h - 128
        cover_x = (w - cover_size) / 2
        cover_y = 60
        

        pbuf = pixbuftools.make_frame(theme.mb_frame_music,
                                      cover_size + 11, cover_size + 11,
                                      True)
        
        if (self.__cover_pbuf):
            pixbuftools.draw_pbuf(pbuf, self.__cover_pbuf, 3, 3,
                                  cover_size, cover_size)
      
        else:
            pixbuftools.draw_pbuf(pbuf, theme.mb_unknown_album, 3, 3,
                                  cover_size, cover_size)
    

        cover1 = pbuf.copy()
        pixbuftools.draw_pbuf(pbuf, theme.mb_trackinfo_btn_play,
                              3 + (cover_size - 120) / 2,
                              3 + (cover_size - 120) / 2)
        cover2 = pbuf.copy()
        self.__cover.set_images(cover1, cover2)
        del pbuf
        del cover1
        del cover2
        


        


    def __on_observe_player(self, src, cmd, *args):
           
        if (cmd == src.OBS_POSITION):
            ctx, pos, total = args
            if (ctx == self.__context_id):
                pos_m = pos / 60
                pos_s = pos % 60
                if (total > 0.001):
                    total_m = total / 60
                    total_s = total % 60
                    info = "%d:%02d / %d:%02d" % (pos_m, pos_s, total_m, total_s)
                else:
                    info = "%d:%02d" % (pos_m, pos_s)
                    total = 0

                self.send_event(self.EVENT_MEDIA_POSITION, info)
                self.emit_message(msgs.MEDIA_EV_POSITION,
                                  pos * 1000, total * 1000)
                self.__progress.set_position(pos, total)
                self.__progress_label.set_text(info)

        elif (cmd == src.OBS_STARTED):
            print "Started Player"
            self.__progress.set_message("")
            self.__cover.set_active(True)
            self.__btn_play.set_images(theme.mb_btn_play_1,
                                       theme.mb_btn_play_2)
            
        elif (cmd == src.OBS_KILLED):
            print "Killed Player"
            self.__current_file = None
            self.__progress.set_message("")
            self.__cover.set_active(True)
            self.__btn_play.set_images(theme.mb_btn_play_1,
                                       theme.mb_btn_play_2)

        elif (cmd == src.OBS_CONNECTING):
            ctx = args[0]
            if (ctx == self.__context_id):
                self.__progress.set_message("... connecting ...")

        elif (cmd == src.OBS_BUFFERING):
            ctx, value = args
            if (ctx == self.__context_id):
                self.__progress.set_message("... buffering (%d%%)..." % value)

        elif (cmd == src.OBS_ERROR):
            ctx, err = args
            if (ctx == self.__context_id):
                self.__current_file = None
                self.__btn_play.set_images(theme.mb_btn_play_1,
                                           theme.mb_btn_play_2)
                self.__cover.set_active(True)
                self.__progress.set_message("error")
                self.__show_error(err)
                self.emit_message(msgs.MEDIA_EV_PAUSE)
                

        elif (cmd == src.OBS_PLAYING):
            ctx = args[0]
            if (ctx == self.__context_id):
                print "Playing"
                self.__progress.set_message("")
                self.__player.set_volume(mb_config.volume())
                self.__btn_play.set_images(theme.mb_btn_pause_1,
                                           theme.mb_btn_pause_2)                
                self.__cover.set_active(False)
                self.emit_message(msgs.MEDIA_EV_PLAY)
            
        elif (cmd == src.OBS_STOPPED):
            ctx = args[0]
            if (ctx == self.__context_id):
                print "Stopped"
                self.__progress.set_message("")
                self.__btn_play.set_images(theme.mb_btn_play_1,
                                           theme.mb_btn_play_2)
                self.__cover.set_active(True)
                self.emit_message(msgs.MEDIA_EV_PAUSE)
            
        elif (cmd == src.OBS_EOF):
            ctx = args[0]
            if (ctx == self.__context_id):        
                #self.__current_file = None
                self.__progress.set_message("")
                self.__btn_play.set_images(theme.mb_btn_play_1,
                                           theme.mb_btn_play_2)
                self.__cover.set_active(True)
                self.send_event(self.EVENT_MEDIA_EOF)
                self.emit_message(msgs.MEDIA_EV_PAUSE)

        elif (cmd == src.OBS_TAG_INFO):
            ctx, tags = args
            title = tags.get("TITLE", "-")
            self.__title.set_text(title)
            


    def __show_error(self, errcode):
    
        if (errcode == self.__player.ERR_INVALID):
            self.call_service(msgs.DIALOG_SVC_ERROR,
                              "Invalid Stream",
                              "The media stream is invalid and cannot be loaded.")
            #dialogs.error("Invalid Stream", "Cannot load this stream.")
        elif (errcode == self.__player.ERR_NOT_FOUND):
            self.call_service(msgs.DIALOG_SVC_ERROR,
                              "Media Not Found",
                              "Cannot find a media stream to play.")
            #dialogs.error("Not found", "Cannot find a stream to play.")
        elif (errcode == self.__player.ERR_CONNECTION_TIMEOUT):
            self.call_service(msgs.DIALOG_SVC_ERROR,
                              "Connection Timeout",
                              "A connection timeout occured while loading the media stream.")
            #dialogs.error("Timeout", "Connection timed out.")       
        elif (errcode == self.__player.ERR_NOT_SUPPORTED):
            self.call_service(msgs.DIALOG_SVC_ERROR,
                              "Unsupported Media Format",
                              "The format of this media stream is not supported.")
            #dialogs.error("Not supported", "The media format is not supported.")


    def __on_set_position(self, pos):
    
        self.__player.set_volume(mb_config.volume())
        self.__player.seek_percent(pos)


    def __on_play_pause(self):
    
        self.__player.set_volume(mb_config.volume())
        self.__player.pause()


    def __on_add_bookmark(self):
    
        if (self.__current_file):
            self.__progress.add_bookmark()


    def __on_change_bookmark(self):
    
        if (self.__current_file):
            bookmarks = self.__progress.get_bookmarks()
            media_bookmarks.set_bookmarks(self.__current_file, bookmarks)


    def __show_info(self, item):
    
        tags = tagreader.get_tags(item)
        title = tags.get("TITLE") or item.name
        artist = tags.get("ARTIST") or "-"
        album = tags.get("ALBUM") or "-"
            
        self.__title.set_text(title or item.name)
        self.__artist.set_text(artist or item.artist)
        if (album): self.__album.set_text(album)
        try:
            self.__cover_pbuf = self.__load_cover(item)
        except:
            self.__cover_pbuf = None
        self.__prepare_cover()



    def load(self, item, direction = MediaWidget.DIRECTION_NEXT):

        def f():
            self.__load_handler = None
            #if (item == self.__current_file): return

            self.__player = mediaplayer.get_player_for_mimetype(item.mimetype)
            
            uri = item.get_resource()
            if (not uri.startswith("/") and
                not "://localhost" in uri and
                not "://127.0.0.1" in uri):                    
                maemo.request_connection()
            #end if
            
            try:
                self.__context_id = self.__player.load_audio(uri)
            except:
                import traceback; traceback.print_exc()
                return
                            
            self.__player.set_volume(mb_config.volume())
            self.__current_file = item
            
            bookmarks = media_bookmarks.get_bookmarks(item)
            self.__progress.set_bookmarks(bookmarks)
                        
            self.__show_info(item)
            self.__lyrics.set_text("- no lyrics found -")
            self.render()

                
        if (self.__load_handler):
            gobject.source_remove(self.__load_handler)
            
        self.__load_handler = gobject.idle_add(f)


    def play_pause(self):
    
        if (self.__player):
            self.__on_play_pause()


    def stop(self):
    
        if (self.__player):
            self.__player.stop()


    def close(self):
        
        if (self.__player):
            self.__player.close()


    def increment(self):

        vol = mb_config.volume()
        vol = min(100, vol + 5)
        mb_config.set_volume(vol)        
        if (self.__player):
            self.__player.set_volume(vol)
        self.send_event(self.EVENT_MEDIA_SCALE, vol / 100.0)

       
        
    def decrement(self):

        vol = mb_config.volume()
        vol = max(0, vol - 5)
        mb_config.set_volume(vol)        
        if (self.__player):
            self.__player.set_volume(vol)
        self.send_event(self.EVENT_MEDIA_SCALE, vol / 100.0)    


    def set_scaling(self, v):

        vol = int(v * 100)
        mb_config.set_volume(vol)        
        if (self.__player):
            self.__player.set_volume(vol)
        self.send_event(self.EVENT_MEDIA_SCALE, v)


    def rewind(self):
    
        if (self.__player):
            self.__player.rewind()
        
        
    def forward(self):
    
        if (self.__player):
            self.__player.forward()


    def __find_cover(self, uri):
        
        candidates = [ os.path.join(uri, ".folder.png"),
                       os.path.join(uri, "folder.jpg"),
                       os.path.join(uri, "cover.jpg"),
                       os.path.join(uri, "cover.jpeg"),
                       os.path.join(uri, "cover.png"),
                       os.path.join(uri, "cover.bmp") ]

        imgs = [ os.path.join(uri, f)
                 for f in os.listdir(uri)
                 if f.lower().endswith(".png") or
                 f.lower().endswith(".jpg") or
                 f.lower().endswith(".bmp") ]

        cover = ""
        for c in candidates + imgs:
            if (os.path.exists(c)):
                cover = c
                break
        #end for
        
        return cover
        
        
    def __load_cover(self, item):

        uri = item.get_resource()
        tags = tagreader.get_tags(item)
        coverdata = tags.get("PICTURE")

        pbuf = None
        if (coverdata):
            # load embedded APIC
            pbuf = self.__load_apic(coverdata)
            
        if (not pbuf):
            # load cover from file
            coverfile = self.__find_cover(os.path.dirname(uri))
            try:
                pbuf = gtk.gdk.pixbuf_new_from_file(coverfile)
            except:
                pass
        
        return pbuf           

        
        
    def __load_apic(self, data):
    
        idx = data.find("\x00", 1)
        idx = data.find("\x00", idx + 1)
        while (data[idx] == "\x00"): idx +=1
        picdata = data[idx:]

        try:
            loader = gtk.gdk.PixbufLoader()
            loader.write(picdata)
            loader.close()
            pbuf = loader.get_pixbuf()
        except:
            import traceback; traceback.print_exc()
            pbuf = None
            
        return pbuf

