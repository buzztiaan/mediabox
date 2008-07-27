from mediabox.MediaWidget import MediaWidget
from ui.EventBox import EventBox
from ui.ImageButton import ImageButton
from ui.ProgressBar import ProgressBar
from ui.Label import Label
from ui.Pixmap import TEMPORARY_PIXMAP
import mediaplayer
from utils import maemo
import theme

import gtk
import gobject
import os


_COVER_SIZE = 256


class AudioWidget(MediaWidget):
    """
    Media widget for viewing videos.
    """


    def __init__(self):
    
        self.__player = None
        mediaplayer.add_observer(self.__on_observe_player)
        self.__volume = 50

        self.__uri = ""
        self.__context_id = 0

        MediaWidget.__init__(self)


        self.__cover = None
        self.__buffer = TEMPORARY_PIXMAP
        
        self.__title = Label("-", theme.font_headline,
                             theme.color_fg_trackinfo)
        self.add(self.__title)

        self.__album = Label("-", theme.font_plain,
                             theme.color_fg_trackinfo)
        self.add(self.__album)

        self.__artist = Label("-", theme.font_plain,
                              theme.color_fg_trackinfo)
        self.add(self.__artist)



        # controls
        self.__btn_play = ImageButton(theme.btn_play_1,
                                      theme.btn_play_2)
        self.__btn_play.connect_clicked(self.__on_play_pause)

        self.__progress = ProgressBar()
        self.__progress.connect_changed(self.__on_set_position)
        
        self._set_controls(self.__btn_play, self.__progress)


    def render_this(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        cover_x = 24
        cover_y = 94
        
        label_x = cover_x + _COVER_SIZE + 32

        self.__title.set_geometry(cover_x, 34, 500, 0)
        self.__album.set_geometry(label_x + 48, 94, 300 - 48, 0)
        self.__artist.set_geometry(label_x + 48, 134, 300 - 48, 0)
        
        self.__buffer.fill_area(x, y, w, h, theme.color_bg)
        if (self.__cover):
            self.__buffer.draw_frame(theme.viewer_music_frame,
                                     x + cover_x, y + cover_y,
                                     _COVER_SIZE + 11, _COVER_SIZE + 11,
                                     True)
            self.__buffer.fit_pixbuf(self.__cover,
                                     x + cover_x + 3, y + cover_y + 3,
                                     _COVER_SIZE, _COVER_SIZE)
        
        else:
            self.__buffer.fit_pixbuf(theme.mb_unknown_album,
                                     x + cover_x + 3, y + cover_y + 3,
                                     _COVER_SIZE, _COVER_SIZE)


        self.__buffer.draw_pixbuf(theme.viewer_music_album, x + label_x, y + 92)
        self.__buffer.draw_pixbuf(theme.viewer_music_artist, x + label_x, y + 132)
        
        screen.copy_pixmap(self.__buffer, x, y, x, y, w, h)


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
                self.send_event(self.EVENT_MEDIA_EOF)



    def __on_set_position(self, pos):
    
        self.__player.seek_percent(pos)


    def __on_play_pause(self):
    
        self.__player.pause()



    def __show_info(self, item):
    
        if (item.tags):
            title = item.tags.get("TITLE")
            artist = item.tags.get("ARTIST")
            album = item.tags.get("ALBUM")
        else:
            title = ""
            artist = ""
            album = ""
            
        self.__title.set_text(title or item.name)
        self.__artist.set_text(artist or item.artist)
        if (album): self.__album.set_text(album)
        try:
            self.__cover = self.__load_cover(item)
        except:
            pass
        self.render_all()



    def load(self, item):

        def f():
            uri = item.get_resource()
            if (uri == self.__uri): return

            # TODO: get player for MIME type
            self.__player = mediaplayer.get_player_for_mimetype(item.mimetype)
            
            try:
                self.__context_id = self.__player.load_video(uri)
            except:
                import traceback; traceback.print_exc()
                return
                            
            self.__player.set_volume(self.__volume)
            self.__uri = uri
            
            self.__show_info(item)
            
                
        gobject.idle_add(f)




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
        if (item.tags):
            coverdata = item.tags.get("PICTURE")
        else:
            coverdata = None
            
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

