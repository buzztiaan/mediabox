from mediabox.MediaWidget import MediaWidget
from mediabox import media_bookmarks
from mediabox import tagreader
from mediabox import config as mb_config
from ui.EventBox import EventBox
from ui.ImageButton import ImageButton
from ui.Image import Image
from ui.ProgressBar import ProgressBar
from ui.Label import Label
from ui.Pixmap import TEMPORARY_PIXMAP
from ui import dialogs
import mediaplayer
from utils import maemo
import theme

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


        self.__cover = None
        self.__buffer = TEMPORARY_PIXMAP
        
        self.__title = Label("-", theme.font_headline,
                             theme.color_fg_trackinfo)
        #self.__title.set_alignment(Label.CENTERED)
        self.add(self.__title)

        self.__album = Label("-", theme.font_plain,
                             theme.color_fg_trackinfo)
        self.add(self.__album)

        self.__artist = Label("-", theme.font_plain,
                              theme.color_fg_trackinfo)
        self.add(self.__artist)

        self.__progress_label = Label("", theme.font_headline,
                                      theme.color_fg_trackinfo)
        self.add(self.__progress_label)
        self.__progress_label.set_alignment(Label.RIGHT)

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
        
        self.__cover_ebox = EventBox()
        self.__cover_ebox.connect_clicked(self.__on_play_pause)
                                    
        self.add(self.__cover_ebox)
        


    def render_this(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        screen.fill_area(x, y, w, h, theme.color_bg)
        
        if (w < 800):
            self.__car_btn_prev.set_visible(False)
            self.__car_btn_next.set_visible(False)
            self.__progress_label.set_visible(False)
        else:
            self.__car_btn_prev.set_visible(True)
            self.__car_btn_next.set_visible(True)
            self.__progress_label.set_visible(True)
            self.__car_btn_prev.set_geometry(0, 0, 128, h - 96 - 10)
            self.__car_btn_next.set_geometry(w - 128, 0, 128, h - 96 - 10)
            self.__progress_label.set_geometry(w - 200, 10, 190, 0)
                
        # place labels
        lbl_x = 10
        lbl_y = h - 96
        lbl_w = w - 20
        self.__title.set_geometry(lbl_x, lbl_y, lbl_w, 0)
        
        screen.fill_area(x, y + lbl_y - 10, w, 96 + 10, "#dddddd")
               
        lbl_y += 48
        lbl_w = w / 2 - 20
        screen.draw_pixbuf(theme.viewer_music_album,
                                  x + lbl_x, y + lbl_y)
        self.__album.set_geometry(lbl_x + 48, lbl_y + 4, lbl_w -48, 0)
        
        lbl_x += w / 2
        screen.draw_pixbuf(theme.viewer_music_artist,
                                  x + lbl_x, y + lbl_y)
        self.__artist.set_geometry(lbl_x + 48, lbl_y + 4, lbl_w - 48, 0)

        # place lyrics box
        lb_x = lbl_x
        lb_y = lbl_y + 48
        lb_w = lbl_w
        lb_h = h - lb_y - 10
        #screen.fill_area(x + lb_x, y + lb_y, lb_w, lb_h, "#666666")

        gobject.idle_add(self.__render_cover)


    def __render_cover(self):

        if (not self.may_render()): return

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
    
        cover_size = h - 128
        cover_x = (w - cover_size) / 2
        cover_y = 10
        
        self.__cover_ebox.set_geometry(cover_x, cover_y,
                                       cover_size + 11, cover_size + 11)
                                       
        self.__buffer.fill_area(0, 0, cover_size + 11, cover_size + 11,
                                theme.color_bg)
        
        if (self.__cover):
            self.__buffer.draw_frame(theme.viewer_music_frame,
                                     0, 0,
                                     cover_size + 11, cover_size + 11,
                                     True)
            self.__buffer.fit_pixbuf(self.__cover,
                                     3, 3,
                                     cover_size, cover_size)
        
        else:
            self.__buffer.fit_pixbuf(theme.mb_unknown_album,
                                     3, 3,
                                     cover_size, cover_size)        

        screen.copy_pixmap(self.__buffer, 0, 0, x + cover_x, y + cover_y,
                           cover_size + 11, cover_size + 11)
        


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
                self.__progress.set_position(pos, total)
                self.__progress_label.set_text(info)

        elif (cmd == src.OBS_STARTED):
            print "Started Player"
            self.__progress.set_message("")
            self.__btn_play.set_images(theme.mb_btn_play_1,
                                       theme.mb_btn_play_2)
            
        elif (cmd == src.OBS_KILLED):
            print "Killed Player"
            self.__current_file = None
            self.__progress.set_message("")
            self.__btn_play.set_images(theme.mb_btn_play_1,
                                       theme.mb_btn_play_2)

        elif (cmd == src.OBS_BUFFERING):
            ctx = args[0]
            if (ctx == self.__context_id):
                self.__progress.set_message("... buffering ...")

        elif (cmd == src.OBS_ERROR):
            ctx, err = args
            if (ctx == self.__context_id):
                self.__current_file = None
                self.__btn_play.set_images(theme.mb_btn_play_1,
                                           theme.mb_btn_play_2)
                self.__progress.set_message("error")
                self.__show_error(err)
                

        elif (cmd == src.OBS_PLAYING):
            ctx = args[0]
            if (ctx == self.__context_id):
                print "Playing"
                self.__progress.set_message("")
                self.__player.set_volume(mb_config.volume())
                self.__btn_play.set_images(theme.mb_btn_pause_1,
                                           theme.mb_btn_pause_2)                
            
        elif (cmd == src.OBS_STOPPED):
            ctx = args[0]
            if (ctx == self.__context_id):
                print "Stopped"
                self.__progress.set_message("")
                self.__btn_play.set_images(theme.mb_btn_play_1,
                                           theme.mb_btn_play_2)
            
        elif (cmd == src.OBS_EOF):
            ctx = args[0]
            if (ctx == self.__context_id):        
                #self.__current_file = None
                self.__progress.set_message("")
                self.__btn_play.set_images(theme.mb_btn_play_1,
                                           theme.mb_btn_play_2)
                self.send_event(self.EVENT_MEDIA_EOF)

        elif (cmd == src.OBS_NEW_STREAM_TRACK):
            ctx, title = args
            self.__title.set_text(title)
            


    def __show_error(self, errcode):
    
        if (errcode == self.__player.ERR_INVALID):
            dialogs.error("Invalid Stream", "Cannot load this stream.")
        elif (errcode == self.__player.ERR_NOT_FOUND):
            dialogs.error("Not found", "Cannot find a stream to play.")
        elif (errcode == self.__player.ERR_CONNECTION_TIMEOUT):
            dialogs.error("Timeout", "Connection timed out.")       
        elif (errcode == self.__player.ERR_NOT_SUPPORTED):
            dialogs.error("Not supported", "The media format is not supported.")


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
            self.__cover = self.__load_cover(item)
        except:
            pass



    def load(self, item):

        def f():
            self.__load_handler = None
            #if (item == self.__current_file): return

            self.__player = mediaplayer.get_player_for_mimetype(item.mimetype)
            self.__player.set_options("-novideo")
            
            uri = item.get_resource()
            try:
                self.__context_id = self.__player.load(uri)
            except:
                import traceback; traceback.print_exc()
                return
                            
            self.__player.set_volume(mb_config.volume())
            self.__current_file = item
            
            bookmarks = media_bookmarks.get_bookmarks(item)
            self.__progress.set_bookmarks(bookmarks)
                        
            self.__show_info(item)
            self.render()
            
                
        if (self.__load_handler):
            gobject.source_remove(self.__load_handler)
            
        self.__load_handler = gobject.idle_add(f)


    def stop(self):
    
        if (self.__player):
            self.__player.stop()



    def increment(self):

        vol = mb_config.volume()
        vol = min(100, vol + 5)
        mb_config.set_volume(vol)        
        if (self.__player):
            self.__player.set_volume(vol)
        self.send_event(self.EVENT_MEDIA_VOLUME, vol)

       
        
    def decrement(self):

        vol = mb_config.volume()
        vol = max(0, vol - 5)
        mb_config.set_volume(vol)        
        if (self.__player):
            self.__player.set_volume(vol)
        self.send_event(self.EVENT_MEDIA_VOLUME, vol)    



    def __find_cover(self, uri):
        
        candidates = [ os.path.join(uri, ".folder.png"),
                       os.path.join(uri, "folder.jpg"),
                       os.path.join(uri, "cover.jpg"),
                       os.path.join(uri, "cover.jpeg"),
                       os.path.join(uri, "cover.png") ]

        imgs = [ os.path.join(uri, f)
                 for f in os.listdir(uri)
                 if f.lower().endswith(".png") or
                 f.lower().endswith(".jpg") ]

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
            
        
        path = os.path.dirname(uri)
        for i in (".folder.png", "folder.jpg", "cover.jpg",
                  "cover.jpeg", "cover.png"):
            coverpath = os.path.join(path, i)
            if (os.path.exists(coverpath)): return coverpath
            
        return None
        
        
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

