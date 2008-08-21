from com import Viewer, msgs
from PlaylistThumbnail import PlaylistThumbnail
from PlaylistItem import PlaylistItem
from mediabox.TrackList import TrackList
import m3u
from mediabox import viewmodes
from ui.ImageButton import ImageButton
from ui.SideTabs import SideTabs
from utils import logging
import theme

import os
import gobject


_PLAYLIST_FILE = os.path.expanduser("~/.mediabox/playlist.m3u")


_VIEWMODE_NONE = -1
_VIEWMODE_NO_PLAYER = 0
_VIEWMODE_PLAYER_NORMAL = 1
_VIEWMODE_PLAYER_FULLSCREEN = 2


class PlaylistViewer(Viewer):

    ICON = theme.mb_viewer_playlist
    ICON_ACTIVE = theme.mb_viewer_playlist_active
    PRIORITY = 5

    def __init__(self):
    
        # whether the playlist was modified since loading
        self.__playlist_modified = False
        
        self.__items = []
        self.__thumbnails = []
        self.__current_index = 0
        self.__media_widget = None
        self.__view_mode = _VIEWMODE_NONE
    
        Viewer.__init__(self)
        self.set_title("Playlist")
        
        self.__playlist = TrackList(with_drag_sort = True)
        self.__playlist.set_geometry(10, 0, 730, 370)
        self.__playlist.connect_button_clicked(self.__on_item_button)
        self.__playlist.connect_items_swapped(self.__on_swap)
        self.add(self.__playlist)

        self.__side_tabs = SideTabs()
        self.__side_tabs.set_size(60 - 8, 370 - 8)
        self.__side_tabs.add_tab(None, "Playlist",
                                 self.__set_view_mode, _VIEWMODE_NO_PLAYER)
        self.__side_tabs.add_tab(None, "Player",
                                 self.__set_view_mode, _VIEWMODE_PLAYER_NORMAL)
        self.add(self.__side_tabs)

        # toolbar
        self.__playlist_tbset = []
        for icon1, icon2, action in [
          (theme.btn_previous_1, theme.btn_previous_2, self.__go_previous),
          (theme.btn_next_1, theme.btn_next_2, self.__go_next)]:
            btn = ImageButton(icon1, icon2)
            btn.connect_clicked(action)
            self.__playlist_tbset.append(btn)
        #end for

        self.__set_view_mode(_VIEWMODE_NO_PLAYER)


        gobject.timeout_add(0, self.__load_playlist, _PLAYLIST_FILE)
        
        
        
    def __load_playlist(self, path):
        
        logging.info("loading playlist from '%s'" % path)

        self.__playlist.clear_items()
        self.__items = []
        self.__thumbnails = []

        for location, name in m3u.load(path):
            f = self.call_service(msgs.CORE_SVC_GET_FILE, location)
            if (f):
                self.__add_item(f)
        #end for
        self.__playlist_modified = False
        
        
    def __save_playlist(self, path):
        
        logging.info("saving playlist to '%s'" % path)
        items = [ (f.get_full_path(), f.name) for f in self.__items ]
        m3u.save(path, items)
        

    def __on_toggle_fullscreen(self):
    
        if (self.__view_mode == _VIEWMODE_PLAYER_FULLSCREEN):
            self.__set_view_mode(_VIEWMODE_PLAYER_NORMAL)
        else:
            self.__set_view_mode(_VIEWMODE_PLAYER_FULLSCREEN)


    def __set_view_mode(self, mode):

        if (mode == self.__view_mode): return
        self.__view_mode = mode
        
        if (mode == _VIEWMODE_NO_PLAYER):
            self.__playlist.set_visible(True)
            self.__side_tabs.set_pos(740 + 4, 0 + 4)

            if (self.__media_widget):
                self.__media_widget.set_visible(False)
            self.set_toolbar(self.__playlist_tbset)
            
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NO_STRIP)
            self.emit_event(msgs.CORE_ACT_RENDER_ALL)

        elif (mode == _VIEWMODE_PLAYER_NORMAL):
            self.__playlist.set_visible(False)
            self.__side_tabs.set_pos(560 + 4, 0 + 4)

            if (self.__media_widget):
                self.__media_widget.set_visible(True)
                self.__media_widget.set_geometry(0, 0, 560, 370)
                self.set_toolbar(self.__media_widget.get_controls() + \
                                 self.__playlist_tbset)

            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NORMAL)
                                 
            self.set_collection(self.__thumbnails)
                
            self.emit_event(msgs.CORE_ACT_RENDER_ALL)

        elif (mode == _VIEWMODE_PLAYER_FULLSCREEN):
            self.__playlist.set_visible(False)
            if (self.__media_widget):
                self.__media_widget.set_visible(True)
                self.__media_widget.set_geometry(0, 0, 800, 480)
                
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.FULLSCREEN)
            self.render()
       

    def __on_item_button(self, item, idx, button):
    
        if (button == item.BUTTON_PLAY):
            f = self.__items[idx]
            self.__playlist.hilight(idx)
            self.__playlist.render()
            self.__load_item(f)
            self.__current_index = idx
            
        elif (button == item.BUTTON_REMOVE):
            self.__remove_item(idx)
                
        elif (button == item.BUTTON_REMOVE_PRECEEDING):
            self.__playlist.set_frozen(True)
            for i in range(0, idx + 1):
                self.__remove_item(0)
            self.__playlist.set_frozen(False)

        elif (button == item.BUTTON_REMOVE_FOLLOWING):
            self.__playlist.set_frozen(True)
            for i in range(idx, len(self.__items)):
                self.__remove_item(idx)
            self.__playlist.set_frozen(False)


    def __on_swap(self, idx1, idx2):
    
        temp = self.__items[idx1]
        self.__items[idx1] = self.__items[idx2]
        self.__items[idx2] = temp

        temp = self.__thumbnails[idx1]
        self.__thumbnails[idx1] = self.__thumbnails[idx2]
        self.__thumbnails[idx2] = temp

        if (self.__current_index == idx1):
            self.__current_index = idx2
        elif (self.__current_index == idx2):
            self.__current_index = idx1


    def __on_eof(self):
    
        self.__go_next()


    def __on_media_volume(self, volume):
        """
        Reacts on changing the sound volume.
        """

        self.emit_event(msgs.MEDIA_EV_VOLUME_CHANGED, volume)
        

    def __go_previous(self):

        if (self.__current_index > 0):
            idx = self.__current_index
            self.__current_index -= 1
            f = self.__items[self.__current_index]
            self.__playlist.hilight(self.__current_index)
            self.__playlist.render()
            self.__remove_item(idx)
            
            self.__load_item(f)
        
        
    def __go_next(self):
    
        if (self.__current_index < len(self.__items) - 1):
            idx = self.__current_index
            self.__current_index += 1
            f = self.__items[self.__current_index]
            self.__playlist.hilight(self.__current_index)
            self.__playlist.render()
            self.__remove_item(idx)
            
            self.__load_item(f)



    def __load_item(self, f):
    
        if (self.__media_widget):
            self.remove(self.__media_widget)

        # get media widget
        self.__media_widget = self.call_service(
                                      msgs.MEDIAWIDGETREGISTRY_SVC_GET_WIDGET,
                                      self, f.mimetype)
        self.__media_widget.connect_media_eof(self.__on_eof)
        self.__media_widget.connect_media_volume(self.__on_media_volume)
        #media_widget.connect_media_position(self.__on_media_position)
        #media_widget.connect_fullscreen_toggled(
        #                                    self.__on_toggle_fullscreen)

        if (self.__media_widget):
            self.set_toolbar(self.__media_widget.get_controls())
            self.__media_widget.set_geometry(180, 40, 620, 370)
            self.__media_widget.set_visible(True)
            self.add(self.__media_widget)

            self.__side_tabs.select_tab(1)
            #self.__set_view_mode(_VIEWMODE_PLAYER_NORMAL)
            self.render()

            self.__media_widget.load(f)
            



    def __add_item(self, f):
        """
        Adds the given item to the playlist.
        """
        
        thumb = self.call_service(msgs.MEDIASCANNER_SVC_GET_THUMBNAIL, f)
        plitem = PlaylistItem(thumb, f)
        self.__playlist.append_item(plitem)
        self.__playlist.render()
        self.__items.append(f)

        tn = PlaylistThumbnail(thumb, f)
        self.__thumbnails.append(tn)
        self.set_collection(self.__thumbnails)


    def __remove_item(self, idx):
        """
        Removes the item at the given index position.
        """

        del self.__items[idx]
        del self.__thumbnails[idx]

        self.__playlist.remove_item(idx)
        if (idx == self.__current_index):
            self.__current_index = -1
        elif (idx < self.__current_index):
            self.__current_index -= 1

        self.set_collection(self.__thumbnails)


        
    def handle_event(self, msg, *args):
                    
        if (msg == msgs.PLAYLIST_ACT_APPEND):
            f = args[0]
            logging.info("adding '%s' to playlist" % f.name)
            self.call_service(msgs.NOTIFY_SVC_SHOW_INFO,
                              u"adding \xbb%s\xab to playlist" % f.name)
            self.__playlist_modified = True
            self.__add_item(f)

        elif (msg == msgs.CORE_EV_DEVICE_ADDED):
            if (not self.__playlist_modified):
                self.__load_playlist(_PLAYLIST_FILE)

        elif (msg == msgs.CORE_EV_APP_SHUTDOWN):
            self.__save_playlist(_PLAYLIST_FILE)

        elif (msg == msgs.MEDIA_ACT_STOP):
            if (self.__media_widget):
                self.__media_widget.stop()

        if (self.is_active()):
            # load selected file
            if (msg == msgs.CORE_ACT_LOAD_ITEM):
                idx = args[0]
                item = self.__items[idx]
                self.__load_item(item)

            if (self.__media_widget):
                # watch FULLSCREEN hw key
                if (msg == msgs.HWKEY_EV_FULLSCREEN):
                    if (self.__view_mode in \
                      (_VIEWMODE_PLAYER_NORMAL, _VIEWMODE_PLAYER_FULLSCREEN)):
                        self.__on_toggle_fullscreen()
                # watch INCREMENT hw key
                elif (msg == msgs.HWKEY_EV_INCREMENT):
                    self.__media_widget.increment()
                # watch DECREMENT hw key
                elif (msg == msgs.HWKEY_EV_DECREMENT):
                    self.__media_widget.decrement()
            #end if
            
        #end if


    def show(self):
    
        Viewer.show(self)
        self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NO_STRIP)
        
