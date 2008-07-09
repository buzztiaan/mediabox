from com import Viewer, msgs

from mediabox.TrackList import TrackList
from AlbumHeader import AlbumHeader
from ListItem import ListItem
from PlaylistItem import PlaylistItem
from AlbumThumbnail import AlbumThumbnail
from ui.ImageButton import ImageButton
from ui.ProgressBar import ProgressBar
from mediabox.ThrobberDialog import ThrobberDialog
import mediaplayer
from mediabox.TrackInfo import TrackInfo
from mediabox import viewmodes
from ui import dialogs
import theme
import idtags

import gtk
import gobject
import os



# view modes
_VIEW_ALBUMS = 0
_VIEW_PLAYLIST = 1


class _Track(object):
    __slots__ = ["title", "trackno", "artist", "album", "uri",
                 "icon", "icon_uri"]
    def __init__(self, trk = None):
        if (trk):
            self.title = trk.title
            self.trackno = trk.trackno
            self.artist = trk.artist
            self.album = trk.album
            self.uri = trk.uri
            self.icon = trk.icon
            self.icon_uri = trk.icon_uri
        else:
            self.title = ""
            self.trackno = 0
            self.artist = ""
            self.album = ""
            self.uri = ""
            self.icon = None
            self.icon_uri = ""



class AlbumViewer(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_music
    ICON_ACTIVE = theme.viewer_music_active
    PRIORITY = 20
    

    def __init__(self):

        self.__items = []
        self.__is_fullscreen = False

        self.__view_mode = _VIEW_ALBUMS
    
        self.__player = mediaplayer.get_player_for_uri("")
        mediaplayer.add_observer(self.__on_observe_player)
        self.__volume = 50
                
        # list of tracks
        self.__tracks = []
        self.__current_index = -1
        self.__current_uri = ""
        self.__current_album_uri = ""
        
        # tracks in playlist
        self.__playlist_tracks = []
        self.__playlist_index = -1
        
        self.__context_id = 0
    
        Viewer.__init__(self)
    
        self.__list = TrackList(with_header = True)
        self.__list.set_geometry(0, 40, 610, 370)
        #self.__list.add_observer(self.__on_observe_track_list)
        self.__list.connect_button_clicked(self.__on_list_button_clicked)
        self.add(self.__list)

        self.__playlist = TrackList(with_drag_sort = True)
        self.__playlist.set_visible(False)
        self.__playlist.set_geometry(10, 40, 780, 370)
        #self.__playlist.add_observer(self.__on_observe_playlist)
        self.__playlist.connect_button_clicked(self.__on_plist_button_clicked)
        self.add(self.__playlist)
        
        self.__trackinfo = TrackInfo()
        self.__trackinfo.set_visible(False)
        self.__trackinfo.set_geometry(0, 40, 800, 370)
        self.add(self.__trackinfo)
        
        self.__throbber = ThrobberDialog()
        self.__throbber.set_throbber(theme.throbber)
        self.__throbber.set_visible(False)
        self.add(self.__throbber)


        # toolbars
        self.__btn_toggle = ImageButton(theme.btn_playlist_1,
                                        theme.btn_playlist_2)
        self.__btn_toggle.connect_clicked(self.do_toggle_playlist)
         
        self.__btn_play = ImageButton(theme.btn_play_1,
                                      theme.btn_play_2)
        self.__btn_play.connect_clicked(self.__on_play_pause)

        btn_prev = ImageButton(theme.btn_previous_1,
                               theme.btn_previous_2)
        btn_prev.connect_clicked(self.__on_previous)

        btn_next = ImageButton(theme.btn_next_1,
                               theme.btn_next_2)
        btn_next.connect_clicked(self.__on_next)

        self.__progress = ProgressBar()
        self.__progress.connect_changed(self.do_set_position)

        self.__tbset_albums = self.new_toolbar_set(self.__btn_toggle,
                                                   self.__btn_play,
                                                   self.__progress,
                                                   btn_prev,
                                                   btn_next)
        self.__tbset_playlist = self.new_toolbar_set(self.__btn_toggle,
                                                     self.__btn_play,
                                                     self.__progress,
                                                     btn_prev,
                                                     btn_next)
        self.__tbset_fullscreen = self.new_toolbar_set(self.__btn_play,
                                                       self.__progress,
                                                       btn_prev,
                                                       btn_next)

        self.set_toolbar_set(self.__tbset_albums)



    def handle_event(self, event, *args):
    
        if (event == msgs.CORE_EV_APP_SHUTDOWN):
            mediaplayer.close()
            
        elif (event == msgs.MEDIASCANNER_EV_SCANNING_FINISHED):
            self.__update_media()
    
        elif (event == msgs.MEDIA_EV_PLAY):
            self.__player.stop()
    
        if (self.is_active()):
            if (event == msgs.CORE_ACT_LOAD_ITEM):
                idx = args[0]
                item = self.__items[idx]
                self.__load(item)
        
            if (event == msgs.HWKEY_EV_INCREMENT):
                self.__on_increment()
                
            elif (event == msgs.HWKEY_EV_DECREMENT):
                self.__on_decrement()
                
            elif (event == msgs.HWKEY_EV_ENTER):
                self.__player.pause()
                
            elif (event == msgs.HWKEY_EV_FULLSCREEN):
                self.__on_fullscreen()
                
        #end if


    def clear_items(self):
    
        self.__items = []


    def __update_media(self):
    
        self.__items = []
        thumbnails = []
        
        media = self.call_service(msgs.MEDIASCANNER_SVC_GET_MEDIA,
                                  ["audio/"])
        for f in media:
            thumb = self.call_service(msgs.MEDIASCANNER_SVC_GET_THUMBNAIL, f)
            tn = AlbumThumbnail(thumb, f.name)
            self.__items.append(f)
            thumbnails.append(tn)
        #end for
        self.set_collection(thumbnails)

       
       
    def do_toggle_playlist(self):

        if (self.__view_mode == _VIEW_ALBUMS):
            self.__view_mode = _VIEW_PLAYLIST
            self.__btn_toggle.set_images(theme.btn_albums_1,
                                         theme.btn_albums_2)
        else:
            self.__view_mode = _VIEW_ALBUMS
            self.__btn_toggle.set_images(theme.btn_playlist_1,
                                         theme.btn_playlist_2)

        self.__set_view_mode(self.__view_mode)
        

    def __set_view_mode(self, mode):
    
        if (mode == _VIEW_PLAYLIST):
            self.__list.set_visible(False)
            self.__playlist.set_visible(True)
            self.set_toolbar_set(self.__tbset_playlist)
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NO_STRIP)
            self.emit_event(msgs.CORE_ACT_RENDER_ALL)
     
        else:
            self.__list.set_visible(True)
            self.__playlist.set_visible(False)
            self.set_toolbar_set(self.__tbset_albums)
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NORMAL)
            self.emit_event(msgs.CORE_ACT_RENDER_ALL)


    def __on_observe_player(self, src, cmd, *args):
    
        #if (not self.is_active()): return        
       
        if (cmd == src.OBS_STARTED):
            print "Started Player"
            self.__btn_play.set_images(theme.btn_play_1,
                                       theme.btn_play_2)
                       
        elif (cmd == src.OBS_KILLED):
            print "Killed Player"
            #self.set_title("")
            self.__btn_play.set_images(theme.btn_play_1,
                                       theme.btn_play_2)

        elif (cmd == src.OBS_ERROR):
            ctx, err = args
            if (ctx == self.__context_id):
                self.__show_error(err)
                self.__list.hilight(-1)
                            
        elif (cmd == src.OBS_NEW_STREAM_TRACK):
            ctx, title = args
            if (ctx == self.__context_id):
                print "NEW TRACK", title
            
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
            
        elif (cmd == src.OBS_POSITION):
            ctx, pos, total = args
            if (ctx == self.__context_id and self.is_active()):
                pos_m = pos / 60
                pos_s = pos % 60
                total_m = total / 60
                total_s = total % 60
                info = "%d:%02d / %d:%02d" % (pos_m, pos_s, total_m, total_s)
                self.set_info(info)

                self.__progress.set_position(pos, total)
            
        elif (cmd == src.OBS_EOF):
            ctx = args[0]
            if (ctx == self.__context_id):
                self.__current_uri = ""        
                print "End of Track"
                self.set_title("")
                self.__btn_play.set_images(theme.btn_play_1,
                                           theme.btn_play_2)
                self.__next_track()
       

    def __show_error(self, errcode):
    
        if (errcode == self.__player.ERR_INVALID):
            dialogs.error("Invalid Stream", "Cannot load this stream.")
        elif (errcode == self.__player.ERR_NOT_FOUND):
            dialogs.error("Not found", "Cannot find a stream to play.")
        elif (errcode == self.__player.ERR_CONNECTION_TIMEOUT):
            dialogs.error("Timeout", "Connection timed out.")       
        elif (errcode == self.__player.ERR_NOT_SUPPORTED):
            dialogs.error("Not supported", "The media format is not supported.")



    def __on_list_button_clicked(self, item, idx, button):
    
        if (button == item.BUTTON_ADD_ALBUM):
            self.__add_to_playlist(*self.__tracks)

        elif (button == item.BUTTON_ADD_TRACK):
            trk = self.__tracks[idx - 1]
            self.__add_to_playlist(trk)

        elif (button == item.BUTTON_PLAY):
            trk = self.__tracks[idx - 1]
            self.__play_track(trk)
            

    def __on_plist_button_clicked(self, item, idx, button):
    
        #print idx, button
        if (button == item.BUTTON_PLAY):
            trk = self.__playlist_tracks[idx]
            self.__play_track(trk)
            
        elif (button == item.BUTTON_REMOVE):
            self.__remove_from_playlist(idx)

        elif (button == item.BUTTON_REMOVE_PRECEEDING):
            self.__playlist.set_frozen(True)
            for i in range(0, idx + 1):
                self.__remove_from_playlist(0)
            self.__playlist.set_frozen(False)

        elif (button == item.BUTTON_REMOVE_FOLLOWING):
            self.__playlist.set_frozen(True)            
            for i in range(idx, len(self.__playlist_tracks)):
                self.__remove_from_playlist(idx)
            self.__playlist.set_frozen(False)
        
    def __on_observe_playlist(self, src, cmd, *args):
    
        if (cmd == src.OBS_PLAY_TRACK):
            idx = args[0]
            trk = self.__playlist_tracks[idx]
            self.__play_track(trk)

        elif (cmd == src.OBS_REMOVE_TRACK):
            idx = args[0]
            self.__remove_from_playlist(idx)

        elif (cmd == src.OBS_REMOVE_PRECEEDING_TRACKS):
            idx = args[0]
            self.__playlist.set_frozen(True)
            for i in range(0, idx + 1):
                self.__remove_from_playlist(0)
            self.__playlist.set_frozen(False)

        elif (cmd == src.OBS_REMOVE_FOLLOWING_TRACKS):
            idx = args[0]
            self.__playlist.set_frozen(True)            
            for i in range(idx, len(self.__playlist_tracks)):
                self.__remove_from_playlist(idx)
            self.__playlist.set_frozen(False)                

        elif (cmd == src.OBS_SWAPPED):
            idx1, idx2 = args
            temp = self.__playlist_tracks[idx1]
            self.__playlist_tracks[idx1] = self.__playlist_tracks[idx2]
            self.__playlist_tracks[idx2] = temp
            if (self.__playlist_index == idx1):
                self.__playlist_index = idx2
            elif (self.__playlist_index == idx2):
                self.__playlist_index = idx1

   
    def __add_to_playlist(self, *tracks):
        """
        Adds the given item to the playlist.
        """

        self.__throbber.set_text("Adding to Playlist")
        self.__throbber.set_visible(True)
        self.__throbber.render()
        
        self.__playlist.set_frozen(True)
        
        for trk in tracks:
            plitem = PlaylistItem(trk.icon_uri, #self.__find_cover(os.path.dirname(trk.uri)),
                                  trk.title, trk.artist)
            self.__playlist.append_item(plitem)
                                  
            # clone the track for the playlist to avoid having the same track
            # in the playlist twice
            new_trk = _Track(trk)
            self.__playlist_tracks.append(new_trk)
            self.__throbber.rotate()
        #end for
            
        self.__playlist.set_frozen(False)            
        self.__throbber.set_visible(False)
        self.render()
        
        
    def __remove_from_playlist(self, idx):

        del self.__playlist_tracks[idx]
        self.__playlist.remove_item(idx)
        if (idx == self.__playlist_index):
            self.__playlist_index = -1
        elif (idx < self.__playlist_index):
            self.__playlist_index -= 1
        
        
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
        
        
    def __load_cover(self, uri, tags = {}):
    
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
        

    def __previous_track(self):
        """
        Jumps to the previous track.
        """
        
        self.__stop_current_track()

        # if there is a playlist, take track from playlist
        if (self.__playlist_tracks and
              self.__playlist_index > 0):
            trk = self.__playlist_tracks[self.__playlist_index - 1]
        
        # don't play from album when in playlist mode
        elif (self.__view_mode == _VIEW_ALBUMS and self.__tracks and
              self.__current_index > 0):
            trk = self.__tracks[self.__current_index - 1]
        
        else:
            trk = None

        if (trk):
            self.__play_track(trk)
            
                    
    def __next_track(self):
        """
        Advances to the next track.
        """
        
        self.__stop_current_track()
        
        # if there is a playlist, take track from playlist
        if (self.__playlist_tracks and
              self.__playlist_index + 1 < len(self.__playlist_tracks)):
            trk = self.__playlist_tracks[self.__playlist_index + 1]
        
        # don't play from album when in playlist mode
        elif (self.__view_mode == _VIEW_ALBUMS and self.__tracks and
              self.__current_index + 1 < len(self.__tracks)):
            trk = self.__tracks[self.__current_index + 1]
        
        else:
            trk = None

        if (trk):
            self.__play_track(trk)

        
        
        
    def __play_track(self, trk):

        if (trk.uri == self.__current_uri): return

        #self.update_observer(self.OBS_STOP_PLAYING, self)
        self.emit_event(msgs.MEDIA_EV_PLAY)
        self.__player = mediaplayer.get_player_for_uri(trk.uri)

        self.__player.set_window(-1)
        self.__player.set_options("")

        try:
            self.__current_index = self.__tracks.index(trk)
        except:
            self.__list.hilight(-1)
        else:
            self.__list.hilight(self.__current_index + 1)
            
        try:
            self.__playlist_index = self.__playlist_tracks.index(trk)
        except:
            self.__playlist.hilight(-1)
        else:
            self.__playlist.hilight(self.__playlist_index)

        self.render()
    
            
        def f():               
            try:
                self.__context_id = self.__player.load_audio(trk.uri)
                self.__current_uri = trk.uri
                self.__player.set_volume(self.__volume)
               
                tags = idtags.read(trk.uri) or {}
                cover = self.__load_cover(trk.uri, tags)

                self.set_title(trk.title)
                self.__trackinfo.set_title(trk.title)
                self.__trackinfo.set_info(trk.album, trk.artist)
                self.__trackinfo.set_cover(cover)
                self.__trackinfo.render()

                #self.update_observer(self.OBS_RENDER)
                
            except:
                import traceback; traceback.print_exc()
                self.__list.hilight(-1)
                self.__playlist.hilight(-1)
            
            if (self.__current_index >= 0):
                # add 1 because the first list item is not a track
                self.__list.scroll_to_item(self.__current_index + 1)
            if (self.__playlist_index >= 0):
                self.__playlist.scroll_to_item(self.__playlist_index)            
                
        gobject.idle_add(f)
        

    def __stop_current_track(self):
    
        self.__list.hilight(-1)
        self.__current_uri = ""
         
               
        
    def __load(self, item):
        """
        Loads the given album.
        """

        uri = item.resource
        if (uri == self.__current_album_uri): return
        
        self.__current_album_uri = uri
        self.__list.set_frozen(True)
        self.__throbber.set_text("Loading")
        self.__throbber.set_visible(True)
        self.__throbber.render()

        self.__tracks = []
        self.__list.clear_items()
        self.__current_index = -1
               
        # find tracks
        files = item.get_children()
        tracks = []
        for f in files:      
            filepath = f.resource #os.path.join(uri, f)
            #ext = os.path.splitext(f)[-1].lower()

            if (f.mimetype.startswith("audio/")):
                tags = idtags.read(filepath) or {}
                title = tags.get("TITLE", f.name)
                artist = tags.get("ARTIST", "")
                album = tags.get("ALBUM", "")
                try:
                    trackno = tags.get("TRACKNUMBER")
                    trackno = trackno.split("/")[0]
                    trackno = int(trackno)
                except:
                    trackno = 0
                   
                trk = _Track()
                trk.uri = filepath
                print "path", filepath
                trk.trackno = trackno
                trk.title = title
                trk.artist = artist
                trk.album = album
                #trk.icon_uri = item.thumbnail
                #trk.icon = item.thumbnail_pmap
                tracks.append(trk)
                self.__throbber.rotate()

                if (uri != self.__current_album_uri):
                    # give up if the user selected another album while
                    # the throbber was being rotated
                    return
            #end if
        #end for
        
        # sort by tracknumber, filename
        tracks.sort(lambda a,b: cmp((a.trackno, a.uri), (b.trackno, b.uri)))
        
        # make album header
        item = AlbumHeader(None, #self.__find_cover(item),
                           item.name, len(tracks))
        self.__list.append_item(item)
        
        # build track list
        for trk in tracks:
            self.__tracks.append(trk)
            item = ListItem(trk.title, trk.artist)
            self.__list.append_item(item)
            
            # hilight currently selected item
            if (trk.uri == self.__current_uri):            
                idx = len(self.__tracks) - 1
                self.__list.hilight(idx + 1)
        #end for
            
        self.__list.set_frozen(False)
        self.__throbber.set_visible(False)
        self.render()


    def search(self, key):
    
        if (self.__view_mode == _VIEW_ALBUMS):
            idx = 1  # 1 because the first list item is the header, not a track
            for trk in self.__tracks:
                if (key in trk.title.lower()):
                    self.__list.scroll_to_item(idx)
                    print "found", trk.title, "for", key
                    break
                idx += 1
            #end for
        elif (self.__view_mode == _VIEW_PLAYLIST):
            idx = 0
            for trk in self.__playlist_tracks:
                if (key in trk.title.lower()):
                    print "search", key
                    self.__playlist.scroll_to_item(idx)
                    print "found", trk.title, "for", key
                    break
                idx += 1
            #end for
            


    def __on_enter(self):
    
        self.__player.pause()
        
        
    def __on_increment(self):
    
        if (self.__volume + 5 <= 100):
            self.__volume += 5
        self.__player.set_volume(self.__volume)
        self.emit_event(msgs.CORE_EV_VOLUME_CHANGED, self.__volume)
        
        
    def __on_decrement(self):

        if (self.__volume - 5 >= 0):
            self.__volume -= 5
        self.__player.set_volume(self.__volume)
        self.emit_event(msgs.CORE_EV_VOLUME_CHANGED, self.__volume)
        
    
    def do_set_position(self, pos):
    
        self.__player.seek_percent(pos)


    def __on_play_pause(self):
    
        self.__player.pause()

    
    def __on_previous(self):
        
        self.__previous_track()

        
    def __on_next(self):
    
        self.__next_track()


    def __on_fullscreen(self):
    
        self.__is_fullscreen = not self.__is_fullscreen
        
        if (self.__is_fullscreen):
            self.__list.set_visible(False)
            self.__playlist.set_visible(False)
            self.__trackinfo.set_visible(True)
            self.set_toolbar_set(self.__tbset_fullscreen)
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NO_STRIP)
            self.emit_event(msgs.CORE_ACT_RENDER_ALL)
        else:            
            self.__trackinfo.set_visible(False)
            self.__set_view_mode(self.__view_mode)
            self.emit_event(msgs.CORE_ACT_RENDER_ALL)

