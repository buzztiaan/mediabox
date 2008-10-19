from com import Viewer, msgs
from PlaylistThumbnail import PlaylistThumbnail
from ItemThumbnail import ItemThumbnail
from PlaylistItem import PlaylistItem
from mediabox.TrackList import TrackList
from Playlist import Playlist
from mediabox import viewmodes
from mediabox import values
from mediabox import config as mb_config
from ui.BoxLayout import BoxLayout
from ui.ImageButton import ImageButton
from ui.Image import Image
from ui.SideTabs import SideTabs
from ui.Dialog import Dialog
from ui import dialogs
from utils import urlquote
from utils import mimetypes
from utils import logging
import theme

import os
import gobject
import random


_PLAYLIST_DIR = os.path.join(values.USER_DIR, "playlists")


_VIEWMODE_NONE = -1
_VIEWMODE_PLAYLIST = 0
_VIEWMODE_PLAYER = 1
_VIEWMODE_PLAYER_FULLSCREEN = 2


class PlaylistViewer(Viewer):

    ICON = theme.mb_viewer_playlist
    PRIORITY = 5

    def __init__(self):
    
        # list of playlists
        self.__lists = []
        self.__current_list = 0
    
        # list of thumbnails representing the playlists
        self.__pl_thumbnails = []
    
        self.__current_file = None
        self.__media_widget = None
        self.__view_mode = _VIEWMODE_NONE
    
        Viewer.__init__(self)
        
        self.__playlist = TrackList(with_drag_sort = True)
        self.__playlist.connect_button_clicked(self.__on_item_button)
        self.__playlist.connect_items_swapped(self.__on_swap)
        self.add(self.__playlist)

        self.__side_tabs = SideTabs()
        self.__side_tabs.set_size(60 - 8, 370 - 8)
        self.__side_tabs.add_tab(None, "Playlist",
                                 self.__set_view_mode, _VIEWMODE_PLAYLIST)
        self.__side_tabs.add_tab(None, "Player",
                                 self.__set_view_mode, _VIEWMODE_PLAYER)
        self.add(self.__side_tabs)

        # box for media widgets
        self.__media_box = BoxLayout()
        self.add(self.__media_box)

        # toolbar
        btn_prev = ImageButton(theme.mb_btn_previous_1, theme.mb_btn_previous_2)
        btn_prev.connect_clicked(self.__go_previous)
        
        btn_next = ImageButton(theme.mb_btn_next_1, theme.mb_btn_next_2)
        btn_next.connect_clicked(self.__go_next)

        btn_add = ImageButton(theme.mb_btn_add_1, theme.mb_btn_add_2)
        btn_add.connect_clicked(self.__create_new_playlist)

        self.__playlist_tbset = [
            btn_prev,
            btn_next,
            Image(theme.mb_toolbar_space_1),
            btn_add
        ]
        self.set_toolbar(self.__playlist_tbset)

        self.__set_view_mode(_VIEWMODE_PLAYLIST)
        gobject.idle_add(self.__load_playlists)


    def render_this(self):
        """
        Computes the layout.
        """

        w, h = self.get_size()        
        playlist, tabs, mbox = self.get_children()
        tabs_w, tabs_h = tabs.get_size()
        
        if (self.__view_mode == _VIEWMODE_PLAYLIST):
            playlist.set_geometry(0, 0, w - tabs_w - 8, h)
            tabs.set_pos(w - tabs_w - 4, 4)

        elif (self.__view_mode == _VIEWMODE_PLAYER):
            mbox.set_geometry(2, 2, w - tabs_w - 8, h - 4)
            tabs.set_pos(w - tabs_w - 4, 4)

        elif (self.__view_mode == _VIEWMODE_PLAYER_FULLSCREEN):
            mbox.set_geometry(0, 0, w, h)


    def __is_queue(self):
        """
        Returns whether the currently selected playlist is the playqueue.
        """
        
        return (self.__current_list == 0)


    def __get_playlist_thumbnail_pieces(self, pl):
    
        pieces = []
        for f in pl.get_files():
            thumb = self.call_service(msgs.MEDIASCANNER_SVC_GET_THUMBNAIL, f)
            if (not (thumb, f.mimetype) in pieces and os.path.exists(thumb)):
                pieces.append((thumb, f.mimetype))
            if (len(pieces) == 4):
                break
        #end for

        return pieces


    def __update_playlist_thumbnail(self):
    
        pl_tn = self.__pl_thumbnails[self.__current_list]
        pl = self.__lists[self.__current_list]
        pl_tn.set_thumbnails(self.__get_playlist_thumbnail_pieces(pl))
        if (self.__view_mode == _VIEWMODE_PLAYLIST):
            self.set_collection(self.__pl_thumbnails)

        
    def __load_playlists(self):
        """
        Loads the available playlists.
        """

        def cb(pl, name, location):
            f = self.call_service(msgs.CORE_SVC_GET_FILE, location)
            if (f):
                self.__add_item(pl, f)


        self.__lists = []

        # create playlist folder if it does not yet exist
        if (not os.path.exists(_PLAYLIST_DIR)):
            try:
                os.makedirs(_PLAYLIST_DIR)
            except:
                pass
        pl_path = os.path.join(_PLAYLIST_DIR, "Playlist.m3u")
        if (not os.path.exists(pl_path)):
            try:
                open(pl_path, "w").write("")
            except:
                pass

        # initialize playqueue
        queue = Playlist()
        queue.set_name("Queue")
        self.__lists.append(queue)
        self.__pl_thumbnails.append(PlaylistThumbnail(queue))
        
        # load playlists
        files = [ f for f in os.listdir(_PLAYLIST_DIR)
                  if f.endswith(".m3u") ]
        files.sort()
        for f in files:
            path = os.path.join(_PLAYLIST_DIR, f)
            pl = Playlist()
            pl.load_from_file(path, cb)

            self.__lists.append(pl)
            pl_tn = PlaylistThumbnail(pl)
            pl_tn.set_thumbnails(self.__get_playlist_thumbnail_pieces(pl))
            self.__pl_thumbnails.append(pl_tn)
            #self.__update_playlist_thumbnail()
        #end for
        
        self.set_collection(self.__pl_thumbnails)
        self.__current_list = 0
        self.__display_playlist(self.__lists[self.__current_list])
       
        
    def __save_playlists(self):
        """
        Saves all playlists.
        """
        
        for pl in self.__lists.values():
            pl.save()
        
        
    def __create_new_playlist(self):
        """
        Creates a new playlist.
        """
        
        dlg = Dialog()
        dlg.add_entry("Name of Playlist:")
        dlg.set_title("New Playlist")
        values = dlg.wait_for_values()

        if (values):
            name = values[0]
            if (name in [ pl.get_name() for pl in self.__lists ]):
                dialogs.error("Error",
                              u"There is already a playlist with name " \
                               "\302\273%s\302\253." % name)
                return

            pl_path = os.path.join(_PLAYLIST_DIR,
                                   urlquote.quote(name, safe = "") + ".m3u")
            print "PL PATH", pl_path
            pl = Playlist()
            pl.set_name(name)
            pl.save_as(pl_path)
            self.__lists.append(pl)
            pl_tn = PlaylistThumbnail(pl)
            self.__pl_thumbnails.append(pl_tn)
        
            self.set_collection(self.__pl_thumbnails)
            self.emit_event(msgs.CORE_ACT_SELECT_ITEM, len(self.__lists) - 1)
        #end if
        

    def __on_toggle_fullscreen(self):
    
        if (self.__view_mode == _VIEWMODE_PLAYER_FULLSCREEN):
            self.__set_view_mode(_VIEWMODE_PLAYER)
        else:
            self.__set_view_mode(_VIEWMODE_PLAYER_FULLSCREEN)


    def __set_view_mode(self, mode):

        if (mode == self.__view_mode): return
        self.__view_mode = mode
        
        if (mode == _VIEWMODE_PLAYLIST):
            self.emit_event(msgs.UI_ACT_FREEZE)
        
            self.__playlist.set_visible(True)
            self.__media_box.set_visible(False)
            self.__side_tabs.set_visible(True)
            
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NORMAL)
            self.set_collection(self.__pl_thumbnails)
            self.emit_event(msgs.CORE_ACT_HILIGHT_ITEM, self.__current_list)

            self.emit_event(msgs.UI_ACT_THAW)

        elif (mode == _VIEWMODE_PLAYER):
            self.emit_event(msgs.UI_ACT_FREEZE)
            
            self.__playlist.set_visible(False)
            self.__media_box.set_visible(True)
            self.__side_tabs.set_visible(True)

            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NORMAL)
                                 
            pl = self.__lists[self.__current_list]
            self.set_collection(pl.get_thumbnails())
            self.emit_event(msgs.CORE_ACT_HILIGHT_ITEM, pl.get_position())

            self.emit_event(msgs.UI_ACT_THAW)
                

        elif (mode == _VIEWMODE_PLAYER_FULLSCREEN):
            self.__playlist.set_visible(False)
            self.__side_tabs.set_visible(False)
            self.__media_box.set_visible(True)
                
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.FULLSCREEN)
            self.render()
       

    def __on_item_button(self, item, idx, button):

        pl = self.__lists[self.__current_list]
    
        if (button == item.BUTTON_PLAY):
            #self.__playlist.hilight(idx)
            #self.__playlist.render()
            self.__load_item(pl, idx)
            
        elif (button == item.BUTTON_REMOVE):
            self.__remove_item(pl, idx)
            pl.save()
                
        elif (button == item.BUTTON_REMOVE_PRECEEDING):
            self.__playlist.set_frozen(True)
            for i in range(0, idx + 1):
                self.__remove_item(pl, 0)
            pl.save()
            self.__playlist.set_frozen(False)

        elif (button == item.BUTTON_REMOVE_FOLLOWING):
            self.__playlist.set_frozen(True)
            for i in range(idx, pl.get_size()):
                self.__remove_item(pl, idx)
            pl.save()
            self.__playlist.set_frozen(False)


    def __on_swap(self, idx1, idx2):
    
        pl = self.__lists[self.__current_list]
        pl.swap(idx1, idx2)
        pl.save()
        """
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
        """
        

    def __on_media_eof(self):
    
        if (self.__is_queue()):
            pl = self.__lists[self.__current_list]
            idx = pl.get_position()
            self.__remove_item(pl, idx)
            pl.set_position(idx - 1)
            self.set_collection(pl.get_thumbnails())
            
        self.emit_event(msgs.MEDIA_EV_EOF)        
        self.__go_next()


    def __on_media_volume(self, volume):
        """
        Reacts on changing the sound volume.
        """

        self.emit_event(msgs.MEDIA_EV_VOLUME_CHANGED, volume)



    def __on_media_position(self, info):
        """
        Reacts when the media playback position has changed.
        """
    
        self.set_info(info)
        

    def __go_previous(self):

        pl = self.__lists[self.__current_list]
        if (pl.has_previous()):
            idx = pl.get_position()
            self.__load_item(pl, idx - 1)
            self.emit_event(msgs.CORE_ACT_HILIGHT_ITEM, idx - 1)
                    
        
    def __go_next(self):

        pl = self.__lists[self.__current_list]
        if (self.__is_queue()):
            if (pl.has_next()):
                idx = pl.get_position() + 1
                self.__load_item(pl, idx)
                
        else:
            repeat_mode = mb_config.repeat_mode()
            shuffle_mode = mb_config.shuffle_mode()
            
            if (repeat_mode == mb_config.REPEAT_MODE_NONE):
                if (shuffle_mode == mb_config.SHUFFLE_MODE_NONE):
                    self.__play_next(False)

                elif (shuffle_mode == mb_config.SHUFFLE_MODE_ONE):
                    self.__play_shuffled(False)
                    
                elif (shuffle_mode == mb_config.SHUFFLE_MODE_ALL):
                    self.__play_shuffled(True)
                
            elif (repeat_mode == mb_config.REPEAT_MODE_ONE):
                self.__play_same()

            elif (repeat_mode == mb_config.REPEAT_MODE_ALL):
                if (shuffle_mode == mb_config.SHUFFLE_MODE_NONE):
                    self.__play_next(True)

                elif (shuffle_mode == mb_config.SHUFFLE_MODE_ONE):
                    self.__play_shuffled(False)

                elif (shuffle_mode == mb_config.SHUFFLE_MODE_ALL):
                    self.__play_shuffled(True)
            

    def __play_same(self):
    
        pl = self.__lists[self.__current_list]
        idx = pl.get_position()
        self.__load_item(pl, idx)

        return True
        
        
    def __play_next(self, wraparound):
        
        pl = self.__lists[self.__current_list]
        idx = pl.get_position()
        if (pl.has_next()):
            self.__load_item(pl, idx + 1)
            return True

        elif (wraparound):
            self.__load_item(pl, 0)
            return True
            
        else:
            return False

        
    def __play_shuffled(self, from_all):
    
        if (from_all):
            self.__current_list = random.randint(1, len(self.__lists) - 1)
            # TODO...
                    
        pl = self.__lists[self.__current_list]
        new_idx = random.randint(0, pl.get_size() - 1)
        self.__load_item(pl, new_idx)
        
        return True


    def __load_item(self, pl, idx):        

        if (idx < 0): return
        self.emit_event(msgs.MEDIA_ACT_STOP)
        
        f = pl.get_files()[idx]
        #if (f == self.__current_file): return
        self.__current_file = f

        if (self.__media_widget):
            self.__media_widget.stop()
            self.__media_box.remove(self.__media_widget)

        # get media widget
        self.__media_widget = self.call_service(
                                      msgs.MEDIAWIDGETREGISTRY_SVC_GET_WIDGET,
                                      self, f.mimetype)

        if (not self.__media_widget):
            return
            
        self.__media_widget.connect_media_eof(self.__on_media_eof)
        self.__media_widget.connect_media_volume(self.__on_media_volume)
        self.__media_widget.connect_media_position(self.__on_media_position)
        #media_widget.connect_fullscreen_toggled(
        #                                    self.__on_toggle_fullscreen)
        
        self.set_toolbar(self.__media_widget.get_controls() + \
                         self.__playlist_tbset)
        self.__media_box.add(self.__media_widget)
        self.__media_widget.set_visible(True)

        if (not f.mimetype in mimetypes.get_audio_types()):
            self.__side_tabs.select_tab(1)

        self.emit_event(msgs.UI_ACT_RENDER)

        self.__playlist.hilight(idx)
        self.__playlist.scroll_to_item(idx)
        self.__playlist.render()
        self.set_title(f.name)
        pl.set_position(idx)
        
        self.__media_widget.load(f)
        self.emit_event(msgs.MEDIA_EV_LOADED, self, f)

        if (self.__view_mode == _VIEWMODE_PLAYER):
            self.emit_event(msgs.CORE_ACT_HILIGHT_ITEM, idx)



    def __add_item(self, pl, f):
        """
        Adds the given item to the playlist.
        """
        
        if (f.mimetype in (f.DIRECTORY, "audio/x-music-folder")):
            items = [ c for c in f.get_children()
                    if not c.mimetype in (f.DIRECTORY, "audio/x-music-folder") ]
            for item in items:
                self.__add_item(pl, item)
            return
        #end if
        
        thumb = self.call_service(msgs.MEDIASCANNER_SVC_GET_THUMBNAIL, f)
        plitem = PlaylistItem(thumb, f)
        self.__playlist.append_item(plitem)
        self.__playlist.render()

        tn = ItemThumbnail(thumb, f)
        #self.__thumbnails.append(tn)
        #self.set_collection(self.__thumbnails)

        pl.append(plitem, tn, f)
        


    def __remove_item(self, pl, idx):
        """
        Removes the item at the given index position.
        """

        pl.remove(idx)

        self.__playlist.remove_item(idx)
        #if (idx == self.__current_index):
        #    self.__current_index = -1
        #elif (idx < self.__current_index):
        #    self.__current_index -= 1

        #self.set_collection(self.__thumbnails)
        self.__update_playlist_thumbnail()



    def __display_playlist(self, pl):
        """
        Displays the contents of the given playlist.
        """

        self.__playlist.clear_items()
        for item in pl.get_items():
            self.__playlist.append_item(item)
        self.__playlist.render()
        
        
    def handle_event(self, msg, *args):
              
        Viewer.handle_event(self, msg, *args)
                    
        if (msg == msgs.PLAYLIST_ACT_APPEND):
            files = args
            if (not files): return
            pl = self.__lists[self.__current_list]
            pl_name = pl.get_name()
            
            if (len(files) == 1):
                self.call_service(msgs.NOTIFY_SVC_SHOW_INFO,
                          u"adding \xbb%s\xab to %s" % (files[0].name, pl_name))
            else:
                self.call_service(msgs.NOTIFY_SVC_SHOW_INFO,
                               u"adding %d items to %s" % (len(files), pl_name))
                              
            self.__playlist.set_frozen(True)
            for f in files:
                logging.info("adding '%s' to %s" % (f.name, pl_name))
                self.__add_item(pl, f)
            pl.save()
            self.__playlist.set_frozen(False)
            
            self.__update_playlist_thumbnail()
            #self.__playlist_modified = True
            #self.__save_playlist(_PLAYLIST_FILE)

        elif (msg == msgs.MEDIA_EV_EOF):
            if (self.__is_queue()):
                self.__go_next()
                self.drop_event()

        #elif (msg == msgs.CORE_EV_DEVICE_ADDED):
        #    if (not self.__playlist_modified):
        #        self.__load_playlist(_PLAYLIST_FILE)

        #elif (msg == msgs.CORE_EV_APP_SHUTDOWN):
        #    self.__save_playlist(_PLAYLIST_FILE)

        elif (msg == msgs.MEDIA_ACT_STOP):
            if (self.__media_widget):
                self.__media_widget.stop()

        if (self.is_active()):
            # load selected file
            if (msg == msgs.CORE_ACT_LOAD_ITEM):
                idx = args[0]
                if (self.__view_mode == _VIEWMODE_PLAYLIST):
                    self.__current_list = idx
                    pl = self.__lists[self.__current_list]
                    self.__display_playlist(pl)
                else:
                    pl = self.__lists[self.__current_list]
                    self.__load_item(pl, idx)
                
            # provide search-as-you-type
            elif (msg == msgs.CORE_ACT_SEARCH_ITEM):
                key = args[0]
                self.__search(key)                  

            if (self.__media_widget):
                # watch FULLSCREEN hw key
                if (msg == msgs.HWKEY_EV_FULLSCREEN):
                    if (self.__view_mode in \
                      (_VIEWMODE_PLAYER, _VIEWMODE_PLAYER_FULLSCREEN)):
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
        if (self.__view_mode == _VIEWMODE_PLAYLIST):
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NORMAL)
            self.emit_event(msgs.CORE_ACT_HILIGHT_ITEM, self.__current_list)


    def __search(self, key):
    
        idx = 0
        pl = self.__lists[self.__current_list]
        for item in pl.get_files():
            if (key in item.name.lower()):
                self.__playlist.scroll_to_item(idx)
                if (self.__view_mode == _VIEWMODE_PLAYER):
                    self.emit_event(msgs.CORE_ACT_SCROLL_TO_ITEM, idx)
                logging.info("search: found '%s' for '%s'" % (item.name, key))
                break
            idx += 1
        #end for
