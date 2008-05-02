from viewers.Viewer import Viewer
from mediabox.TrackList import TrackList
from AlbumHeader import AlbumHeader
from ListItem import ListItem
from PlaylistItem import PlaylistItem
from AlbumThumbnail import AlbumThumbnail
from mediabox.ThrobberDialog import ThrobberDialog
import mediaplayer
from mediabox.TrackInfo import TrackInfo
from mediabox import caps
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
    CAPS = caps.PLAYING | caps.SKIPPING | caps.POSITIONING | caps.PLAYLIST
    CAPS_ALBUMS = CAPS
    CAPS_PLAYLIST = caps.PLAYING | caps.SKIPPING | caps.POSITIONING | caps.ALBUMS
    CAPS_FULLSCREEN = caps.PLAYING | caps.SKIPPING | caps.POSITIONING
    

    def __init__(self, esens):

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
    
        Viewer.__init__(self, esens)
    
        self.__list = TrackList(esens, with_header = True)
        self.__list.set_geometry(0, 40, 610, 370)
        self.__list.add_observer(self.__on_observe_track_list)
        self.add(self.__list)
                      
        self.__playlist = TrackList(esens, with_drag_sort = True)
        self.__playlist.set_visible(False)
        self.__playlist.set_geometry(10, 40, 780, 370)
        self.__playlist.add_observer(self.__on_observe_playlist)
        self.add(self.__playlist)
        
        self.__trackinfo = TrackInfo(esens)
        self.__trackinfo.set_visible(False)
        self.__trackinfo.set_geometry(0, 40, 800, 370)
        self.add(self.__trackinfo)
        
        self.__throbber = ThrobberDialog(esens)
        self.__throbber.set_throbber(theme.throbber)
        self.__throbber.set_visible(False)
        self.add(self.__throbber)


    def clear_items(self):
    
        self.__items = []


    def update_media(self, mscanner):
    
        self.__items = []
        for item in mscanner.get_media(mscanner.MEDIA_AUDIO):
            if (not item.thumbnail_pmap):
                tn = AlbumThumbnail(item.thumbnail, item.name)
                item.thumbnail_pmap = tn
            self.__items.append(item)
       
       
    def do_toggle_playlist(self):

        if (self.__view_mode == _VIEW_ALBUMS):
            self.__view_mode = _VIEW_PLAYLIST
        else:
            self.__view_mode = _VIEW_ALBUMS
        self.__set_view_mode(self.__view_mode)
        

    def __set_view_mode(self, mode):
    
        if (mode == _VIEW_PLAYLIST):
            self.__list.set_visible(False)
            self.__playlist.set_visible(True)
            self.update_observer(self.OBS_REPORT_CAPABILITIES,
                                 self.CAPS_PLAYLIST)
            self.update_observer(self.OBS_HIDE_COLLECTION)
            self.update_observer(self.OBS_RENDER)            
        else:
            self.__list.set_visible(True)
            self.__playlist.set_visible(False)
            self.update_observer(self.OBS_REPORT_CAPABILITIES,
                                 self.CAPS_ALBUMS)
            self.update_observer(self.OBS_SHOW_COLLECTION)
            self.update_observer(self.OBS_RENDER)
        
       
       
    def __on_observe_player(self, src, cmd, *args):
    
        #if (not self.is_active()): return        
    
        if (cmd == src.OBS_STARTED):
            print "Started Player"
            self.update_observer(self.OBS_STATE_PAUSED)            
            
        elif (cmd == src.OBS_KILLED):
            self.__current_uri = ""
            print "Killed Player"
            self.set_title("")
            self.update_observer(self.OBS_STATE_PAUSED)           

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
                self.update_observer(self.OBS_STATE_PLAYING)
            
        elif (cmd == src.OBS_STOPPED):
            ctx = args[0]
            if (ctx == self.__context_id):
                self.__current_uri = ""
                print "Stopped"            
                self.update_observer(self.OBS_STATE_PAUSED)
            
        elif (cmd == src.OBS_POSITION):
            ctx, pos, total = args
            if (ctx == self.__context_id and self.is_active()):
                #print "%d / %d" % (pos, total)
                self.update_observer(self.OBS_TIME, pos, total)
            
        elif (cmd == src.OBS_EOF):
            ctx = args[0]
            if (ctx == self.__context_id):
                self.__current_uri = ""        
                print "End of Track"
                self.set_title("")
                self.update_observer(self.OBS_STATE_PAUSED)
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



    def __on_observe_track_list(self, src, cmd, *args):
    
        if (cmd == src.OBS_ADD_ALBUM):
            self.__add_to_playlist(*self.__tracks)
        elif (cmd == src.OBS_ADD_TRACK):
            idx = args[0]
            trk = self.__tracks[idx]
            self.__add_to_playlist(trk)
        elif (cmd == src.OBS_PLAY_TRACK):
            idx = args[0]
            trk = self.__tracks[idx]
            self.__play_track(trk)
            
        
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

        self.update_observer(self.OBS_STOP_PLAYING, self)
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
         
         
    def shutdown(self):

        mediaplayer.close()
        
        
    def load(self, item):
        """
        Loads the given album.
        """

        uri = item.uri
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
        files = os.listdir(uri)
        tracks = []
        for f in files:      
            filepath = os.path.join(uri, f)
            ext = os.path.splitext(f)[-1].lower()

            if (ext in mediaplayer.AUDIO_FORMATS):
                tags = idtags.read(filepath) or {}
                title = tags.get("TITLE", f)
                artist = tags.get("ARTIST", "")
                album = tags.get("ALBUM", "")
                try:
                    trackno = int(tags.get("TRACKNUMBER"))
                except:
                    trackno = 0
                   
                trk = _Track()
                trk.uri = filepath
                trk.trackno = trackno
                trk.title = title
                trk.artist = artist
                trk.album = album
                trk.icon_uri = item.thumbnail
                trk.icon = item.thumbnail_pmap
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
        item = AlbumHeader(self.__find_cover(uri),
                           os.path.basename(uri), len(tracks))
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
            


    def do_enter(self):
    
        self.__player.pause()
        
        
    def do_increment(self):
    
        if (self.__volume + 5 <= 100):
            self.__volume += 5
        self.__player.set_volume(self.__volume)
        self.update_observer(self.OBS_VOLUME, self.__volume)
        
        
    def do_decrement(self):

        if (self.__volume - 5 >= 0):
            self.__volume -= 5
        self.__player.set_volume(self.__volume)
        self.update_observer(self.OBS_VOLUME, self.__volume)        
        
    
    def do_set_position(self, pos):
    
        self.__player.seek_percent(pos)


    def do_play_pause(self):
    
        self.__player.pause()

    
    def do_previous(self):
        
        self.__previous_track()

        
    def do_next(self):
    
        self.__next_track()
        
        
    def stop_playing(self, issued_by):
    
        if (issued_by != self):
            self.__player.stop()
        

    def show(self):
    
        Viewer.show(self)
        self.update_observer(self.OBS_SET_COLLECTION, self.__items)


    def do_fullscreen(self):
    
        self.__is_fullscreen = not self.__is_fullscreen
        
        if (self.__is_fullscreen):
            self.__list.set_visible(False)
            self.__playlist.set_visible(False)
            self.__trackinfo.set_visible(True)
            self.update_observer(self.OBS_REPORT_CAPABILITIES,
                                 self.CAPS_FULLSCREEN)
            self.update_observer(self.OBS_HIDE_COLLECTION)            
            self.update_observer(self.OBS_RENDER)
        else:            
            self.__trackinfo.set_visible(False)
            self.__set_view_mode(self.__view_mode)
            self.update_observer(self.OBS_RENDER)
