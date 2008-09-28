from com import Viewer, msgs

from mediabox.TrackList import TrackList
from AlbumHeader import AlbumHeader
from ListItem import ListItem
from AlbumThumbnail import AlbumThumbnail
from ui.ImageButton import ImageButton
from ui.ProgressBar import ProgressBar
from mediabox.ThrobberDialog import ThrobberDialog
import mediaplayer
from mediabox import viewmodes
import theme
import idtags
from mediabox import config as mb_config

import gtk
import gobject
import os



# view modes
_VIEW_NORMAL = 0
_VIEW_FULLSCREEN = 1


class AlbumViewer(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.mb_viewer_audio
    PRIORITY = 20
    

    def __init__(self):

        self.__items = []
        self.__thumbnails_needed = []
        self.__is_fullscreen = False
        self.__audio_widget = None

        self.__view_mode = _VIEW_NORMAL
        self.__volume = 50
                
        # list of tracks
        self.__tracks = []
        self.__current_index = -1
        self.__current_track = None
        self.__current_album = None
             
        self.__context_id = 0
    
        Viewer.__init__(self)
    
        self.__list = TrackList(with_header = True)
        self.__list.set_geometry(0, 0, 610, 370)
        self.__list.connect_button_clicked(self.__on_list_button_clicked)
        self.add(self.__list)
        
        self.__throbber = ThrobberDialog()
        self.__throbber.set_throbber(theme.throbber)
        self.__throbber.set_visible(False)
        self.add(self.__throbber)


    def render_this(self):

        if (not self.__audio_widget):
            self.__audio_widget = self.call_service(
                                      msgs.MEDIAWIDGETREGISTRY_SVC_GET_WIDGET,
                                      self, "audio/*")
            if (not self.__audio_widget):
                return
                
            self.__audio_widget.set_visible(False)
            self.add(self.__audio_widget)            
            self.__audio_widget.connect_media_position(self.__on_media_position)
            self.__audio_widget.connect_media_eof(self.__on_eof)
            self.__audio_widget.connect_media_volume(self.__on_media_volume)

            # create toolbar
            ctrls = self.__audio_widget.get_controls()

            btn_prev = ImageButton(theme.mb_btn_previous_1,
                                   theme.mb_btn_previous_2)
            btn_prev.connect_clicked(self.__on_previous)

            btn_next = ImageButton(theme.mb_btn_next_1,
                                   theme.mb_btn_next_2)
            btn_next.connect_clicked(self.__on_next)

            ctrls += [btn_prev, btn_next]
            self.set_toolbar(ctrls)


    def handle_event(self, event, *args):
    
        Viewer.handle_event(self, event, *args)
    
        if (event == msgs.CORE_EV_APP_SHUTDOWN):
            mediaplayer.close()
            
        elif (event == msgs.MEDIASCANNER_EV_SCANNING_FINISHED):
            self.__update_media()
    
        elif (event == msgs.MEDIA_EV_PLAY):
            #self.__player.stop()
            pass

        elif (event == msgs.MEDIA_ACT_STOP):
            if (self.__audio_widget):
                self.__audio_widget.stop()
    
        if (self.is_active()):
            if (event == msgs.CORE_ACT_LOAD_ITEM):
                idx = args[0]
                item = self.__items[idx]
                self.__load(item)

            elif (event == msgs.CORE_ACT_SEARCH_ITEM):
                key = args[0]
                self.__search(key)     
        
            elif (event == msgs.HWKEY_EV_INCREMENT):
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



    def __load_thumbnails(self, tn_list):
    
        def on_thumbnail(thumb, tn, files):
            tn.set_thumbnail(thumb)
            tn.invalidate()
            self.emit_event(msgs.CORE_ACT_RENDER_ITEMS)
            
            if (tn_list):
                f, tn = tn_list.pop(0)
                self.call_service(msgs.MEDIASCANNER_SVC_SCAN_FILE, f,
                                  on_thumbnail, tn, tn_list)
        
        f, tn = tn_list.pop(0)
        self.call_service(msgs.MEDIASCANNER_SVC_SCAN_FILE, f,
                          on_thumbnail, tn, tn_list)


    def __update_media(self):
    
        self.__items = []
        thumbnails = []
        self.__thumbnails_needed = []
        
        media = self.call_service(msgs.MEDIASCANNER_SVC_GET_MEDIA,
                                  ["audio/"])
        for f in media:
            thumb = self.call_service(msgs.MEDIASCANNER_SVC_GET_THUMBNAIL, f)
            tn = AlbumThumbnail(thumb, f.name)
            tn.set_emblem(f.source_icon)
            self.__items.append(f)
            thumbnails.append(tn)
            
            if (not os.path.exists(thumb)):
                self.__thumbnails_needed.append((f, tn))            
        #end for
        
        self.set_collection(thumbnails)

       
       
       

    def __set_view_mode(self, mode):
    
        self.__view_mode = mode
        
        if (mode == _VIEW_NORMAL):
            self.__list.set_visible(True)
            self.__audio_widget.set_visible(False)
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NORMAL)
            self.emit_event(msgs.CORE_ACT_RENDER_ALL)
    
        elif (mode == _VIEW_FULLSCREEN):
            self.__list.set_visible(False)
            self.__audio_widget.set_visible(True)
            self.__audio_widget.set_geometry(0, 0, 800, 370)
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NO_STRIP)
            self.emit_event(msgs.CORE_ACT_RENDER_ALL)
        




        """
    def __show_error(self, errcode):
    
        if (errcode == self.__player.ERR_INVALID):
            dialogs.error("Invalid Stream", "Cannot load this stream.")
        elif (errcode == self.__player.ERR_NOT_FOUND):
            dialogs.error("Not found", "Cannot find a stream to play.")
        elif (errcode == self.__player.ERR_CONNECTION_TIMEOUT):
            dialogs.error("Timeout", "Connection timed out.")       
        elif (errcode == self.__player.ERR_NOT_SUPPORTED):
            dialogs.error("Not supported", "The media format is not supported.")
        """



    def __on_media_position(self, info):
        """
        Reacts on player position information.
        """
    
        self.set_info(info)
        

    def __on_eof(self):
        """
        Reacts on reaching the end of a file.
        """
    
        self.emit_event(msgs.MEDIA_EV_EOF)
        if (self.may_go_next()):
            self.__next_track()
        else:
            self.__list.hilight(-1)


    def __on_media_volume(self, volume):
        """
        Reacts on changing the sound volume.
        """

        self.emit_event(msgs.MEDIA_EV_VOLUME_CHANGED, volume)
        


    def __on_list_button_clicked(self, item, idx, button):
    
        if (button == item.BUTTON_ADD_ALBUM):
            self.emit_event(msgs.PLAYLIST_ACT_APPEND, *self.__tracks)

        elif (button == item.BUTTON_ADD_TRACK):
            trk = self.__tracks[idx - 1]
            self.emit_event(msgs.PLAYLIST_ACT_APPEND, trk)

        elif (button == item.BUTTON_PLAY):
            trk = self.__tracks[idx - 1]
            self.__play_track(trk)
            
     

    def __previous_track(self):
        """
        Jumps to the previous track.
        """
        
        self.__stop_current_track()
        if (self.__tracks and self.__current_index > 0):
            trk = self.__tracks[self.__current_index - 1]
        
        else:
            trk = None

        if (trk):
            self.__play_track(trk)
            
                    
    def __next_track(self):
        """
        Advances to the next track.
        """

        repeat_mode = mb_config.repeat_mode()
        #shuffle_mode = mb_config.shuffle_mode()

        current_track = self.__current_track
        self.__stop_current_track()
        
        handled = False
        if (repeat_mode == mb_config.REPEAT_MODE_NONE):
            if (self.__tracks and self.__current_index + 1 < len(self.__tracks)):
                trk = self.__tracks[self.__current_index + 1]
                self.__play_track(trk)
                handled = True

        elif (repeat_mode == mb_config.REPEAT_MODE_ONE):
            self.__play_track(current_track, True)
            handled = True
            
        elif (repeat_mode == mb_config.REPEAT_MODE_ALL):
            if (self.__current_index + 1 < len(self.__tracks)):
                trk = self.__tracks[self.__current_index + 1]
                self.__play_track(trk)
                handled = True
            elif (self.__tracks):
                self.__play_track(self.__tracks[0], True)
                handled = True
                
        #end if
        
        if (not handled):
            self.emit_event(msgs.MEDIA_EV_EOF)




    def __stop_current_track(self):
    
        self.__list.hilight(-1)
        self.__current_track = None
         
         
         
    def __play_track(self, trk, force = False):
    
        self.emit_event(msgs.MEDIA_ACT_STOP)
        
        if (force or trk != self.__current_track):
            idx = self.__tracks.index(trk)
                    
            self.__current_track = trk
            self.__current_index = idx
            
            self.__list.hilight(idx + 1)
            self.__list.scroll_to_item(idx + 1)
            self.set_title(trk.title)
            self.__audio_widget.load(trk)
            self.emit_event(msgs.MEDIA_EV_LOADED, self, trk)
         
               
        
    def __load(self, item):
        """
        Loads the given album.
        """

        uri = item.resource
        if (item == self.__current_album): return
        
        self.__current_album = item
        self.__list.set_frozen(True)
        self.__throbber.set_text("Loading")
        self.__throbber.set_visible(True)
        self.__throbber.render()

        # save memory and remove tags on the old tracks
        for t in self.__tracks: t.tags = None

        self.__tracks = []
        self.__list.clear_items()
        self.__current_index = -1
               
        # find tracks
        files = item.get_children()
        tracks = []
        for f in files:      
            #filepath = f.resource #os.path.join(uri, f)
            #ext = os.path.splitext(f)[-1].lower()

            if (f.mimetype.startswith("audio/")):
                fd = f.get_fd()
                tags = idtags.read_fd(fd) or {}
                fd.close()
                
                title = tags.get("TITLE", f.name)
                artist = tags.get("ARTIST", "")
                album = tags.get("ALBUM", "")
                try:
                    trackno = tags.get("TRACKNUMBER")
                    trackno = trackno.split("/")[0]
                    trackno = int(trackno)
                except:
                    trackno = 0
                   
                if (tags): f.tags = tags
                f.trackno = trackno
                f.title = title
                f.artist = artist
                f.album = album
                #f.md5 = item.md5

                tracks.append(f)
                self.__throbber.rotate()

                if (item != self.__current_album):
                    # give up if the user selected another album while
                    # the throbber was being rotated
                    return
            #end if
        #end for
        
        # sort by tracknumber, filename
        tracks.sort(lambda a,b: cmp((a.trackno, a.name), (b.trackno, b.name)))
        
        # make album header
        cover = self.call_service(msgs.MEDIASCANNER_SVC_GET_THUMBNAIL, item)
        item = AlbumHeader(cover, item.name, len(tracks))
        self.__list.append_item(item)
        
        # build track list
        for trk in tracks:
            self.__tracks.append(trk)
            item = ListItem(trk.title, trk.artist)
            self.__list.append_item(item)
            
            # hilight currently selected track
            if (trk == self.__current_track):            
                idx = len(self.__tracks)
                self.__list.hilight(idx)
                self.__current_index = idx - 1
        #end for
            
        self.__list.set_frozen(False)
        self.__throbber.set_visible(False)
        self.render()


    def __search(self, key):
    
        idx = 1  # 1 because the first list item is the header, not a track
        for trk in self.__tracks:
            if (key in trk.title.lower()):
                self.__list.scroll_to_item(idx)
                print "found", trk.title, "for", key
                break
            idx += 1
        #end for


    def __on_increment(self):
    
        self.__audio_widget.increment()
        
        
    def __on_decrement(self):

        self.__audio_widget.decrement()


    def __on_previous(self):
        
        self.__previous_track()

        
    def __on_next(self):
    
        self.__next_track()


    def __on_fullscreen(self):
    
        self.__is_fullscreen = not self.__is_fullscreen
        
        if (self.__is_fullscreen):
            self.__set_view_mode(_VIEW_FULLSCREEN)
        else:
            self.__set_view_mode(_VIEW_NORMAL)



    def show(self):
    
        Viewer.show(self)
        if (self.__thumbnails_needed):
            self.__load_thumbnails(self.__thumbnails_needed)

