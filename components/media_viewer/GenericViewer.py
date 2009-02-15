from com import Viewer, msgs
from storage import Device
from DeviceThumbnail import DeviceThumbnail
from FileThumbnail import FileThumbnail
from HeaderItem import HeaderItem
from MediaItem import MediaItem
from SubItem import SubItem
from LibItem import LibItem
from mediabox.TrackList import TrackList
from mediabox.MediaWidget import MediaWidget
from ui.BoxLayout import BoxLayout
from ui.ImageButton import ImageButton
from ui.Image import Image
from ui.SideTabs import SideTabs
from ui import dialogs
from utils import mimetypes
from utils import logging
from io import Downloader
from mediabox import viewmodes
from mediabox import config as mb_config
from theme import theme

import os
import time
import urllib
import gtk
import gobject
import random


class GenericViewer(Viewer):
    """
    Viewer component for browsing storage devices with style.
    """

    PATH = os.path.dirname(__file__)
    ICON = theme.mb_viewer_folder
    PRIORITY = 0
    
    __GO_PARENT = 0
    __GO_CHILD = 1
    __GO_NEW = 2
    
    
    _VIEWMODE_NONE = -1
    _VIEWMODE_BROWSER = 0
    _VIEWMODE_SPLIT_BROWSER = 1
    _VIEWMODE_PLAYER_NORMAL = 2
    _VIEWMODE_PLAYER_FULLSCREEN = 3
    _VIEWMODE_LIBRARY = 4
    

    def __init__(self):
    
        # the accepted device types
        self.__accepted_device_types = []
    
        # table of devices: id -> rootpath
        self.__devices = {}
        
        # the currently selected device and path stack
        self.__current_device = None
        self.__current_file = None        
        self.__path_stack = []
        
        self.__device_items = []
        
        # file items of the current directory
        self.__items = []
        
        # playable items, i.e. items that can be loaded into a player
        self.__playable_items = []
        
        # sibling folders
        self.__sibling_folders = []

        # list for choosing random files from when in shuffle mode
        self.__random_items = []
        
        # list of thumbnails
        #self.__thumbnails = []
        
        # range of subfolder, if any
        self.__subfolder_range = None

        # table: file -> item receiving the thumbnail
        self.__items_downloading_thumbnails = {}
    
        self.__view_mode = self._VIEWMODE_NONE
        
        # the current media widget
        self.__media_widget = None
        
        # timestamp of the last list rendering
        self.__last_list_render_time = 0
    
        # whether the library has been changed
        self.__lib_is_dirty = False
        
        # whether we may advance to the next track
        self.__may_go_next = True
        
        # table: owner -> needs_reload
        self.__needs_reload = {}
        
    
        Viewer.__init__(self)
        
        # file list
        self.__list = TrackList()
        self.add(self.__list)        
        self.__list.connect_button_clicked(self.__on_item_button)

        # library list
        self.__lib_list = TrackList()
        self.__lib_list.set_visible(False)
        self.add(self.__lib_list)
        self.__lib_list.connect_button_clicked(self.__on_lib_item_button)
        self.__lib_list.connect_item_clicked(self.__on_lib_item_set_types)
        
        # media widget box
        self.__media_box = BoxLayout()
        self.add(self.__media_box)

        # side tabs
        self.__side_tabs = SideTabs()
        self.add(self.__side_tabs)

        # toolbar
        self.__btn_back = ImageButton(theme.mb_btn_dir_up_1,
                                      theme.mb_btn_dir_up_2)
        self.__btn_back.connect_clicked(self.__on_btn_back)

        self.__btn_add = ImageButton(theme.mb_btn_add_1,
                                     theme.mb_btn_add_2)
        self.__btn_add.set_visible(False)
        self.__btn_add.connect_clicked(self.__on_btn_add)

        self.__btn_prev = ImageButton(theme.mb_btn_previous_1,
                                      theme.mb_btn_previous_2)
        self.__btn_prev.connect_clicked(self.__go_previous)

        self.__btn_next = ImageButton(theme.mb_btn_next_1,
                                      theme.mb_btn_next_2)
        self.__btn_next.connect_clicked(self.__go_next)

        self.__btn_keep = ImageButton(theme.mb_btn_keep_1,
                                      theme.mb_btn_keep_2, True)
        self.__btn_keep.connect_clicked(self.__on_btn_keep)

        self.accept_device_types(Device.TYPE_GENERIC)
        
        #self.set_size(800, 480)
        self.__set_view_mode(self._VIEWMODE_BROWSER)
        gobject.idle_add(self.__init_library)



    def accept_device_types(self, *types):
        """
        Sets the device types to be accepted.
        
        @param types: list of types
        """
        
        self.__accepted_device_types = types


    def add_tab(self, name, view_mode):
        """
        Adds a new tab with the given name for the given view mode.
        
        @param name:      name to appear on the tab
        @param view_mode: view_mode to which the tab switches
        """
    
        def f():
            gobject.timeout_add(0, self.__set_view_mode, view_mode)
            
        self.__side_tabs.add_tab(None, name, f)


    def __is_device_accepted(self, device):
        """
        Returns whether the given device is of an accepted type.
        """
        
        return (device.TYPE in self.__accepted_device_types)


    def __add_device(self, ident, device):
        """
        Adds the given device with the given identifier, if the device type
        is accepted.
        """

        if (self.__is_device_accepted(device)):
            self.__devices[ident] = device
            self.__strip_needs_reload(self._VIEWMODE_BROWSER)
            self.__update_side_strip()
        
        
    def __remove_device(self, ident):
        """
        Removes the device specified by the given identifier.
        """
    
        try:
            del self.__devices[ident]
            self.__strip_needs_reload(self._VIEWMODE_BROWSER)
            self.__update_side_strip()
        except:
            pass


    def __get_device_thumbnails(self):
        """
        Returns a list of device thumbnails.
        """
    
        thumbnails = []
        self.__device_items = []            
        devs = self.__devices.items()
        
        # sort devices before putting into the list
        devs.sort(lambda a,b:cmp((a[1].CATEGORY, a[1].get_name()),
                                    (b[1].CATEGORY, b[1].get_name())))
        
        for ident, dev in devs:
            tn = DeviceThumbnail(dev)            
            thumbnails.append(tn)
            self.__device_items.append(dev)
        #end for

        return thumbnails        


    def __strip_needs_reload(self, view_mode):
        """
        Marks the current side strip to need a reload.
        """
        
        strip_owner = (self, view_mode)
        self.__needs_reload[strip_owner] = True


    def __update_side_strip(self):
        """
        Updates the side strip depending on the current view mode.
        """
        
        strip_items = []
        strip_index = -1
        
        if (not self.is_active()): return
        
        strip_owner = (self, self.__view_mode)
        needs_reload = self.__needs_reload.get(strip_owner, True)
        items_to_thumbnail = []
        
        if (not needs_reload):            
            return
        else:
            self.__needs_reload[strip_owner] = False
        

        # show devices
        if (self.__view_mode == self._VIEWMODE_BROWSER):
            strip_items = self.__get_device_thumbnails()
            if (self.__current_device in self.__device_items):
                strip_index = self.__device_items.index(self.__current_device)

        
        # show parent directory
        elif (self.__view_mode == self._VIEWMODE_SPLIT_BROWSER):
            if (len(self.__path_stack) > 1):
                for entry in self.__sibling_folders:
                    tn = FileThumbnail(None, entry)
                    items_to_thumbnail.append((None, tn, entry))
                    strip_items.append(tn)
                #end for
                        
                path = self.__path_stack[-1][0]
                if (path in self.__sibling_folders):
                    strip_index = self.__sibling_folders.index(path)

            else:
                strip_items = self.__get_device_thumbnails()
                if (self.__current_device in self.__device_items):
                    strip_index = self.__device_items.index(self.__current_device)

        
        # show playable items
        elif (self.__view_mode == self._VIEWMODE_PLAYER_NORMAL):
            for entry in self.__playable_items:
                thumb = self.call_service(
                    msgs.MEDIASCANNER_SVC_LOOKUP_THUMBNAIL, entry) or None
                tn = FileThumbnail(thumb, entry)
                if (not thumb):
                    items_to_thumbnail.append((None, tn, entry))
                strip_items.append(tn)
            #end for
            
            if (self.__current_file in self.__playable_items):
                strip_index = self.__playable_items.index(self.__current_file)           

        self.set_strip(strip_items)
        if (strip_index >= 0):
            self.hilight_strip_item(strip_index)

        if (self.__path_stack):
            self.__create_thumbnails(self.__path_stack[-1][0], items_to_thumbnail)


    def __update_toolbar(self):
        """
        Updates the contents of the toolbar.
        """
        
        items = []

        if (self.__current_file and self.__current_file.can_keep):
            self.__btn_keep.set_active(False)
            items.append(self.__btn_keep)        

        if (self.__path_stack and self.__path_stack[-1][0].can_add):
            items.append(Image(theme.mb_toolbar_space_1))
            items.append(self.__btn_add)
        
        if (self.__media_widget):
            items += self.__media_widget.get_controls()
            
        if (self.__path_stack and self.__path_stack[-1][0].can_skip):
            items.append(Image(theme.mb_toolbar_space_1))
            items.append(self.__btn_prev)
            items.append(self.__btn_next)

        if (self.__view_mode == self._VIEWMODE_BROWSER
            or self.__view_mode == self._VIEWMODE_SPLIT_BROWSER):
            items.append(Image(theme.mb_toolbar_space_1))
            items.append(self.__btn_back)
            
        self.set_toolbar(items)


    def __update_input_context(self):
        """
        Updates the input context according to the current view mode.
        """
        
        if (self.__view_mode == self._VIEWMODE_BROWSER):
            self.emit_event(msgs.INPUT_EV_CONTEXT_BROWSER)

        elif (self.__view_mode == self._VIEWMODE_SPLIT_BROWSER):
            self.emit_event(msgs.INPUT_EV_CONTEXT_BROWSER)

        elif (self.__view_mode == self._VIEWMODE_PLAYER_NORMAL):
            self.emit_event(msgs.INPUT_EV_CONTEXT_PLAYER)

        elif (self.__view_mode == self._VIEWMODE_PLAYER_FULLSCREEN):
            self.emit_event(msgs.INPUT_EV_CONTEXT_FULLSCREEN)

        elif (self.__view_mode == self._VIEWMODE_LIBRARY):
            self.emit_event(msgs.INPUT_EV_CONTEXT_BROWSER)



    def __hilight_current_file(self):
    
        if (self.__view_mode == self._VIEWMODE_BROWSER):
            if (self.__current_file in self.__items):
                idx = self.__items.index(self.__current_file)
                self.__list.hilight(idx + 1)
                self.__list.scroll_to_item(idx + 1)

        elif (self.__view_mode == self._VIEWMODE_SPLIT_BROWSER):
            if (self.__current_file in self.__items):
                idx = self.__items.index(self.__current_file)
                self.__list.hilight(idx + 1)
                self.__list.scroll_to_item(idx + 1)

        elif (self.__view_mode == self._VIEWMODE_PLAYER_NORMAL):
            if (self.__current_file in self.__playable_items):
                idx = self.__playable_items.index(self.__current_file)
                self.hilight_strip_item(idx)

        elif (self.__view_mode == self._VIEWMODE_PLAYER_FULLSCREEN):
            if (self.__current_file in self.__playable_items):
                idx = self.__playable_items.index(self.__current_file)
                self.hilight_strip_item(idx)

    
    
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        if (self.__view_mode == self._VIEWMODE_BROWSER):
            self.__side_tabs.set_geometry(w - 60 + 4, 4, 60 - 8, h - 8)
            self.__list.set_geometry(0, 0, w - 60, h)

        elif (self.__view_mode == self._VIEWMODE_SPLIT_BROWSER):
            self.__side_tabs.set_geometry(w - 60 + 4, 4, 60 - 8, h - 8)
            self.__list.set_geometry(0, 0, w - 60, h)
            
        elif (self.__view_mode == self._VIEWMODE_PLAYER_NORMAL):
            self.__side_tabs.set_geometry(w - 60 + 4, 4, 60 - 8, h - 8)
            self.__media_box.set_geometry(2, 2, w - 60 - 4, h - 4)
        
        elif (self.__view_mode == self._VIEWMODE_PLAYER_FULLSCREEN):
            self.__media_box.set_geometry(0, 0, w, h)
            
        elif (self.__view_mode == self._VIEWMODE_LIBRARY):
            self.__side_tabs.set_geometry(w - 60 + 4, 4, 60 - 8, h - 8)
            self.__lib_list.set_geometry(0, 0, w - 60, h)

        


    def __set_view_mode(self, mode):
    
        if (mode == self.__view_mode): return
        was_fullscreen = (self.__view_mode == self._VIEWMODE_PLAYER_FULLSCREEN)
        self.__view_mode = mode
        self.__update_input_context()
        w, h = self.get_size()
        
        strip_owner = (self, mode)
        if (mode != self._VIEWMODE_PLAYER_FULLSCREEN and not was_fullscreen):
            self.change_strip(strip_owner)

        if (mode == self._VIEWMODE_BROWSER):
            self.emit_event(msgs.UI_ACT_FREEZE)
            self.emit_event(msgs.UI_ACT_VIEW_MODE, viewmodes.NORMAL)
            
            #if (self.__path_stack):
            #    self.__load_folder(self.__path_stack[-1][0], None)
            
            self.__side_tabs.set_visible(True)
            self.__list.set_visible(True)
            self.__media_box.set_visible(False)
            self.__lib_list.set_visible(False)

            if (not was_fullscreen):
                self.__update_side_strip()
                self.__hilight_current_file()
                self.__update_toolbar()
            if (self.__current_device):
                self.set_title(self.__current_device.get_name())
            
            self.emit_event(msgs.UI_ACT_THAW)


        elif (mode == self._VIEWMODE_SPLIT_BROWSER):
            self.emit_event(msgs.UI_ACT_FREEZE)
            self.emit_event(msgs.UI_ACT_VIEW_MODE, viewmodes.NORMAL)

            #if (self.__path_stack):
            #    self.__load_folder(self.__path_stack[-1][0], None)
            
            self.__side_tabs.set_visible(True)
            self.__list.set_visible(True)
            self.__media_box.set_visible(False)
            self.__lib_list.set_visible(False)

            if (not was_fullscreen):
                self.__update_side_strip()
                self.__hilight_current_file()
                self.__update_toolbar()
            if (self.__current_device):
                self.set_title(self.__current_device.get_name())
                        
            self.emit_event(msgs.UI_ACT_THAW)


        elif (mode == self._VIEWMODE_PLAYER_NORMAL):
            self.emit_event(msgs.UI_ACT_VIEW_MODE, viewmodes.NORMAL)
            self.__media_box.set_visible(True)
            self.__side_tabs.set_visible(True)
            self.__list.set_visible(False)
            self.__lib_list.set_visible(False)
            
            if (not was_fullscreen):
                self.emit_event(msgs.UI_ACT_FREEZE)
                self.__update_side_strip()
                self.__hilight_current_file()
                self.__update_toolbar()
                if (self.__current_file):
                    self.set_title(self.__current_file.name)
                self.emit_event(msgs.UI_ACT_THAW)
            else:
                self.render()
                gobject.timeout_add(50, self.emit_event, msgs.UI_ACT_RENDER)


        elif (mode == self._VIEWMODE_PLAYER_FULLSCREEN):
            self.__side_tabs.set_visible(False)
            self.__list.set_visible(False)
            self.__lib_list.set_visible(False)
            self.__media_box.set_visible(True)
            self.__media_box.set_geometry(0, 0, 800, 480)
            self.emit_event(msgs.UI_ACT_VIEW_MODE, viewmodes.FULLSCREEN)

            #self.emit_event(msgs.UI_ACT_THAW)
            self.render()


        elif (mode == self._VIEWMODE_LIBRARY):           
            self.emit_event(msgs.UI_ACT_FREEZE)
            self.emit_event(msgs.UI_ACT_VIEW_MODE, viewmodes.NO_STRIP)
            
            self.__side_tabs.set_visible(True)
            self.__list.set_visible(False)
            self.__lib_list.set_visible(True)
            self.__media_box.set_visible(False)
            
            self.__update_toolbar()
            self.set_title("Media Library")
            
            self.emit_event(msgs.UI_ACT_THAW)
       
        

    def __on_toggle_fullscreen(self):
    
        if (self.__view_mode == self._VIEWMODE_PLAYER_FULLSCREEN):
            #self.__set_view_mode(self._VIEWMODE_PLAYER_NORMAL)
            self.__side_tabs.select_tab(1)
        else:
            self.__set_view_mode(self._VIEWMODE_PLAYER_FULLSCREEN)
       


    def handle_message(self, msg, *args):
        """
        Handles incoming messages.
        """
    
        Viewer.handle_message(self, msg, *args)
        
        if (msg == msgs.CORE_EV_APP_SHUTDOWN):
            if (self.__media_widget):
                self.__media_widget.close()
        
        if (msg == msgs.MEDIASCANNER_EV_SCANNING_FINISHED):
            if (self.__current_device and self.__path_stack):
                #self.__load_device(self.__current_device)
                path = self.__path_stack[-1][0]
                self.__load_folder(path, None)
        
        # watch for new storage devices
        elif (msg == msgs.CORE_EV_DEVICE_ADDED):
            ident, device = args
            self.__add_device(ident, device)
            
        # remove gone storage devices
        elif (msg == msgs.CORE_EV_DEVICE_REMOVED):
            ident = args[0]
            self.__remove_device(ident)

        elif (msg == msgs.MEDIA_ACT_STOP):
            if (self.__media_widget):
                self.__media_widget.stop()
                
        elif (msg == msgs.MEDIA_EV_LOADED):
            self.__list.hilight(-1)
            self.__current_file = None
            self.__may_go_next = False
        
        
        
        # the following messages are only accepted when the viewer is active
        if (not self.is_active()): return
        
        
        if (msg == msgs.INPUT_ACT_REPORT_CONTEXT):
            self.__update_input_context()
        
        
        elif (msg == msgs.INPUT_EV_DOWN):
            w, h = self.__list.get_size()
            idx = self.__list.get_index_at(h)
            if (idx != -1):
                new_idx = min(len(self.__items), idx + 2)
                self.__list.scroll_to_item(new_idx)
                self.emit_event(msgs.CORE_ACT_SCROLL_UP)
            
        elif (msg == msgs.INPUT_EV_UP):
            idx = self.__list.get_index_at(0)
            if (idx != -1):
                new_idx = max(0, idx - 2)
                self.__list.scroll_to_item(new_idx)
                self.emit_event(msgs.CORE_ACT_SCROLL_DOWN)
            
        
        # load selected device or file
        if (msg == msgs.CORE_ACT_LOAD_ITEM):
            idx = args[0]
            if (self.__view_mode == self._VIEWMODE_BROWSER):
                dev = self.__device_items[idx]
                if (dev != self.__current_device):
                    self.__load_device(dev)

            elif (self.__view_mode == self._VIEWMODE_SPLIT_BROWSER):
                if (len(self.__path_stack) > 1):
                    folder = self.__sibling_folders[idx]
                    if (self.__path_stack):
                        self.__path_stack.pop()
                    self.__load_folder(folder, None)
                else:
                    dev = self.__device_items[idx]
                    if (dev != self.__current_device):
                        self.__load_device(dev)               
                    
            elif (self.__view_mode == self._VIEWMODE_PLAYER_NORMAL):
                item = self.__playable_items[idx]
                if (item != self.__current_file):
                    self.__load_file(item, MediaWidget.DIRECTION_NONE)

        # provide search-as-you-type
        elif (msg == msgs.CORE_ACT_SEARCH_ITEM):
            key = args[0]
            self.__search(key)

        # select a device
        elif (msg == msgs.UI_ACT_SELECT_DEVICE):
            dev_id = args[0]
            if (dev_id in self.__devices):
                self.__load_device(self.__devices[dev_id])
                #self.__strip_needs_reload()
                #self.__update_side_strip()


        # go to previous
        elif (msg == msgs.MEDIA_ACT_PREVIOUS):
            self.__go_previous()
            
        # go to next
        elif (msg == msgs.MEDIA_ACT_NEXT):
            self.__go_next()


        # the following messages are only accepted when we have a media widget
        if (not self.__media_widget): return



        # watch FULLSCREEN hw key
        if (msg == msgs.INPUT_EV_FULLSCREEN):
            #if (self.__view_mode in \
            #  (self._VIEWMODE_PLAYER_NORMAL, self._VIEWMODE_PLAYER_FULLSCREEN)):
            self.__on_toggle_fullscreen()
                
        # watch INCREMENT hw key
        elif (msg == msgs.INPUT_EV_VOLUME_UP):
            self.__media_widget.increment()
            
        # watch DECREMENT hw key
        elif (msg == msgs.INPUT_EV_VOLUME_DOWN):
            self.__media_widget.decrement()

                
        elif (msg == msgs.INPUT_EV_PLAY):
            self.__media_widget.play_pause()

        # go to previous
        elif (msg == msgs.INPUT_EV_PREVIOUS):
            self.__go_previous()
            
        # go to next
        elif (msg == msgs.INPUT_EV_NEXT):
            self.__go_next()
   

    def __on_lib_item_button(self, item, idx, button):
    
        if (idx == -1): return
    
        if (button == item.BUTTON_REMOVE):
            self.__lib_list.remove_item(idx)
            self.__lib_list.invalidate_buffer()
            self.__lib_list.render()
            self.__save_library()
        
        
    def __on_lib_item_set_types(self, item, idx, px, py):
    
        if (idx == -1): return

        if (px < 196):
            uri = item.get_path()
            mtypes = item.get_media_types()

            if (px < 68):    mtypes ^= 1
            elif (px < 132): mtypes ^= 2
            elif (px < 196): mtypes ^= 4
            item.set_media_types(mtypes)
            self.__lib_list.invalidate_buffer()
            self.__lib_list.render()
            self.__save_library()
        #end if
        

    def __on_item_button(self, item, idx, button):
        
        if (idx == -1): return
        
        if (button == item.BUTTON_PLAY):
            entry = self.__items[idx - 1]
            self.__list.hilight(idx)
            self.__list.render()
            #gobject.timeout_add(50, self.__load_file, entry,
            #                    MediaWidget.DIRECTION_NONE)
            self.__load_file(entry, MediaWidget.DIRECTION_NONE)

        elif (button == item.BUTTON_ENQUEUE):
            if (idx == 0):
                path, list_offset = self.__path_stack[-1]
                self.emit_event(msgs.PLAYLIST_ACT_APPEND, path)

            else:
                entry = self.__items[idx - 1]
                self.emit_event(msgs.PLAYLIST_ACT_APPEND, entry)

        elif (button == item.BUTTON_ADD_TO_LIBRARY):
            path, list_offset = self.__path_stack[-1]
            self.call_service(msgs.NOTIFY_SVC_SHOW_INFO,
                              u"adding \xbb%s\xab to library" % path.name)
            self.__add_to_library(path, 7)
            self.__save_library()
            
        elif (button == item.BUTTON_REMOVE):
            entry = self.__items[idx - 1]
            entry.delete()
            f, nil = self.__path_stack.pop()
            self.__load_file(f, MediaWidget.DIRECTION_NONE)
            
        elif (button == item.BUTTON_OPEN):
            entry = self.__items[idx - 1]
            if (self.__view_mode == self._VIEWMODE_BROWSER):
                #gobject.timeout_add(50, self.__insert_folder, entry)
                self.__insert_folder(entry)
            else:
                #gobject.timeout_add(50, self.__load_folder, entry, None)
                self.__load_folder(entry, None)
                
        elif (button == item.BUTTON_CLOSE):
            self.__close_subfolder()
                        
            
    def __init_library(self):
        """
        Loads the library folders.
        """
        
        mediaroots = mb_config.mediaroot()
        self.__lib_list.clear_items()
        
        for mroot, mtypes in mediaroots:
            f = self.call_service(msgs.CORE_SVC_GET_FILE, mroot)
            if (f):
                self.__add_to_library(f, mtypes)
        #end for        
            
            
    def __add_to_library(self, f, mtypes):
        """
        Adds the given folder to the library.
        """
        
        item = LibItem(f)
        item.set_media_types(mtypes)
        self.__lib_list.append_item(item)
        
        
    def __save_library(self):
        """
        Saves the current library folders.
        """
        
        mediaroots = []
        for item in self.__lib_list.get_items():
            uri = item.get_path()
            mtypes = item.get_media_types()
            mediaroots.append((uri, mtypes))
            mb_config.set_mediaroot(mediaroots)
        self.__lib_is_dirty = True

        
    def __load_device(self, device):
        """
        Loads the given device.
        """

        self.__current_device = device
        self.__path_stack = []
        
        root = device.get_root()
        
        if (self.__current_device in self.__device_items):
            strip_index = self.__device_items.index(self.__current_device)        
            self.hilight_strip_item(strip_index)
        
        self.set_title(device.get_name())
        if (root.mimetype == root.DIRECTORY):
            self.__load_folder(root, self.__GO_NEW)
        else:
            self.__load_file(root, self.__GO_NEW)
            
        self.emit_event(msgs.UI_EV_DEVICE_SELECTED, device.get_device_id())



    def __load_file(self, f, direction):
        """
        Loads the given file.
        """

        if (f.mimetype.endswith("-folder")):    
            #gobject.timeout_add(250, self.__load_folder, f, self.__GO_CHILD)
            self.__load_folder(f, self.__GO_CHILD)
                
        else:
            self.__current_file = f
            self.set_title(f.name)

            if (not f.mimetype in mimetypes.get_image_types()):
                self.emit_event(msgs.MEDIA_ACT_STOP)

            # request media widget
            media_widget = self.call_service(
                            msgs.MEDIAWIDGETREGISTRY_SVC_GET_WIDGET,
                            self, f.mimetype)

            if (not media_widget):
                dialogs.error("Unhandled Type",
                              "There is no handler for\n"
                              "MIME type '%s'" % f.mimetype)
                return
                
            # remove old media widget
            if (media_widget != self.__media_widget):
                if (self.__media_widget):
                    self.__media_widget.stop()
                    self.__media_box.remove(self.__media_widget)
                self.__media_widget = media_widget                
                            
            self.__update_toolbar()
            
            self.__media_widget.set_visible(True)
            self.__media_widget.connect_media_position(self.__on_media_position)
            self.__media_widget.connect_media_eof(self.__on_media_eof)
            self.__media_widget.connect_media_volume(self.__on_media_volume)
            self.__media_widget.connect_media_previous(self.__go_previous)
            self.__media_widget.connect_media_next(self.__go_next)
            self.__media_widget.connect_fullscreen_toggled(
                                                self.__on_toggle_fullscreen)
            logging.debug("using media widget [%s] for MIME type %s" \
                            % (str(self.__media_widget), f.mimetype))
            if (not self.__media_widget in self.__media_box.get_children()):
                self.__media_box.add(self.__media_widget)

            if (not f.mimetype in mimetypes.get_audio_types()
                and not self.__view_mode == self._VIEWMODE_PLAYER_FULLSCREEN):
                self.__side_tabs.select_tab(1)

            self.__hilight_current_file()

            self.emit_event(msgs.UI_ACT_RENDER)
            self.__media_widget.load(f, direction)
            self.emit_event(msgs.MEDIA_EV_LOADED, self, f)

            try:
                idx = self.__playable_items.index(f)
            except:
                pass
            else:
                if (idx + 1 < len(self.__playable_items)):
                    self.__media_widget.preload(self.__playable_items[idx + 1])



    def __load_folder(self, path, direction):
        """
        Loads the given folder and displays its contents.
        """
        
        def on_child(f, path, entries, items_to_thumbnail):
            # abort if the user has changed the directory again
            if (self.__path_stack[-1][0] != path): return False

            if (f):
                self.__list.get_item(0).set_info("Loading (%d items)..." \
                                                 % len(self.__items))
                entries.append(f)
                self.__add_file(f, items_to_thumbnail, -1)

            else:
                self.__list.get_item(0).set_info("%d items" % len(self.__items))
                self.__random_items = self.__playable_items[:]
                # finished loading items; now create thumbnails
                self.__create_thumbnails(path, items_to_thumbnail)
                self.__strip_needs_reload(self._VIEWMODE_PLAYER_NORMAL)

            now = time.time()
            if (not f or len(entries) == 4 or \
                  now > self.__last_list_render_time + 0.5):
                self.__last_list_render_time = now
            #if (not f or len(entries) == 4 or len(entries) % 10 == 0):
                self.__list.invalidate_buffer()
                self.__list.render()
            
            return True

        
        def on_sibling(f, path, entries):
            # abort if the user has changed the directory again
            if (self.__path_stack[-2][0] != path): return False
            
            if (f and f.mimetype.endswith("-folder")):
                entries.append(f)
            else:
                if (`entries` != `self.__sibling_folders`):
                    self.__sibling_folders = entries
                    self.__update_side_strip()

            return True
                    


        self.__close_subfolder()
                   
        # clear items
        self.__items = []
        self.__playable_items = []
        self.__items_downloading_thumbnails.clear()

        # update path stack
        reload_only = False
        if (self.__path_stack):
            if (path == self.__path_stack[-1][0]):
                reload_only = True

            self.__path_stack[-1][1] = self.__list.get_offset()
        #end if

        if (not reload_only):
            self.__path_stack.append([path, 0])

        self.__list.clear_items()        
        #if (direction == self.__GO_PARENT):
        #    self.__list.fx_slide_right()
        #elif (direction == self.__GO_CHILD):
        #    self.__list.fx_slide_left()

        header = HeaderItem(path.name)
        header.set_info("Retrieving...")
        buttons = [(header.BUTTON_ENQUEUE, theme.mb_item_btn_enqueue)]
        if (path.can_add_to_library):
            buttons.append((header.BUTTON_ADD_TO_LIBRARY, theme.mb_item_btn_add))
        header.set_buttons(*buttons)
        self.__list.append_item(header)
        self.__update_toolbar()
        #self.__list.render()
        self.emit_event(msgs.UI_ACT_RENDER)
        
        if (self.__view_mode == self._VIEWMODE_SPLIT_BROWSER):
            if (len(self.__path_stack) > 1):
                parent_path = self.__path_stack[-2][0]
                gobject.timeout_add(0, parent_path.get_children_async,
                                    on_sibling, parent_path, [])
            else:
                self.__sibling_folders = []
                self.__update_side_strip()

        gobject.timeout_add(0, path.get_children_async, on_child, path, [], [])



    def __insert_folder(self, path):

        def on_child(f, path, entries, items_to_thumbnail, insert_at):
            # abort if the user has changed the directory again
            if (self.__path_stack[-1][0] != path): return False

            if (f):
                #self.__list.get_item(insert_at).set_info("Loading (%d items)" \
                #                                         % len(entries))
                self.__add_file(f, items_to_thumbnail, insert_at + len(entries))
                entries.append(f)

            else:
                #self.__list.get_item(insert_at).set_info("%d items" % len(entries))
                self.__random_items = self.__playable_items[:]
                # finished loading items; now create thumbnails
                self.__create_thumbnails(path, items_to_thumbnail)

            now = time.time()
            self.__subfolder_range = (insert_at, insert_at + len(entries))
            if (not f or len(entries) == 4 or \
                  now > self.__last_list_render_time + 0.5):
                self.__last_list_render_time = now
                self.__list.invalidate_buffer()
                self.__list.render()
            
            return True
    
        idx = self.__items.index(path)
        self.__list.scroll_to_item(idx + 1, force_on_top = True)
        self.__close_subfolder()
        idx = self.__items.index(path)
    
        # clear items
        self.__playable_items = []

        # change item button
        item = self.__list.get_item(idx + 1)
        item.set_buttons(#(item.BUTTON_CLOSE, theme.mb_item_btn_close),
                         (item.BUTTON_ENQUEUE, theme.mb_item_btn_enqueue))

        gobject.timeout_add(0, path.get_children_async, on_child,
                            self.__path_stack[-1][0], [], [], idx + 1)


    def __close_subfolder(self):
    
        if (not self.__subfolder_range): return
        
        idx1, idx2 = self.__subfolder_range
        n = idx2 - idx1
        for i in range(n):
            self.__list.remove_item(idx1 + 1)
            del self.__items[idx1]
        #end for
        
        item = self.__list.get_item(idx1)
        item.set_buttons((item.BUTTON_OPEN, theme.mb_item_btn_open))
        
        self.__subfolder_range = None
        self.__list.render()


    def __add_file(self, entry, items_to_thumbnail, insert_at):
        """
        Adds the given file item to the list.
        """

        # determine available item buttons
        if (insert_at == -1):
            thumbnail = self.call_service(
                msgs.MEDIASCANNER_SVC_LOOKUP_THUMBNAIL, entry) or None
            item = MediaItem(entry, thumbnail)
            if (not thumbnail):
                items_to_thumbnail.append((item, None, entry))
                
        else:
            item = SubItem(entry)
            
        buttons = []
        
        if (entry.mimetype == "application/x-music-folder"):
            buttons.append((item.BUTTON_OPEN, theme.mb_item_btn_open))
            
        elif (entry.mimetype.endswith("-folder")):
            buttons.append((item.BUTTON_PLAY, theme.mb_item_btn_play))
            
        else:
            buttons.append((item.BUTTON_PLAY, theme.mb_item_btn_play))
            buttons.append((item.BUTTON_ENQUEUE, theme.mb_item_btn_enqueue))
            
        if (entry.can_delete):
            buttons.append((item.BUTTON_REMOVE, theme.mb_item_btn_remove))
        item.set_buttons(*buttons)

        # remember if thumbnail does not yet exist
        #if (insert_at == -1 and (not os.path.exists(icon))):
        #    if (entry.is_local or entry.thumbnail):
        #items_to_thumbnail.append((item, None, entry))
        #end if
        
        self.__list.set_frozen(True)
        if (insert_at == -1):
            self.__list.append_item(item)
            self.__items.append(entry)
        else:
            self.__list.insert_item(item, insert_at)
            self.__items.insert(insert_at, entry)
        self.__list.set_frozen(False)
        
        if (not entry.mimetype.endswith("-folder")):
            self.__playable_items.append(entry)
            
        # hilight currently selected item
        if (self.__current_file == entry):
            self.__list.hilight(self.__list.get_items().index(item))


    def __on_media_position(self, info):
        """
        Reacts when the media playback position has changed.
        """
    
        self.set_info(info)
        
        
    def __on_media_eof(self):
        """
        Reacts on media EOF.
        """
        
        logging.debug("reached EOF")
        self.__may_go_next = True
        
        self.emit_event(msgs.MEDIA_EV_EOF)

        if (self.__may_go_next):
            logging.debug("going to next item")
            self.__go_next()


    def __on_media_volume(self, volume):
        """
        Reacts on changing the sound volume.
        """

        self.emit_event(msgs.MEDIA_EV_VOLUME_CHANGED, volume)


    def __go_previous(self):

        try:
            idx = self.__playable_items.index(self.__current_file)
        except:
            return False
            
        if (idx > 0):
            next_item = self.__playable_items[idx - 1]
            self.__load_file(next_item, MediaWidget.DIRECTION_PREVIOUS)
            
            
    def __go_next(self):

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
    
        self.__load_file(self.__current_file, MediaWidget.DIRECTION_NONE)

        return True
        
        
    def __play_next(self, wraparound):
        
        try:
            idx = self.__playable_items.index(self.__current_file)
        except:
            idx = -1
            #return False
            
        if (idx + 1 < len(self.__playable_items)):
            next_item = self.__playable_items[idx + 1]
            self.__load_file(next_item, MediaWidget.DIRECTION_NEXT)
            return True

        elif (wraparound):
            next_item = self.__playable_items[0]
            self.__load_file(next_item, MediaWidget.DIRECTION_NEXT)
            return True
            
        else:
            return False

        
    def __play_shuffled(self, from_all):
    
        if (from_all):
            # TODO...
            pass

        if (not self.__random_items):
            self.__random_items = self.__playable_items[:]
        idx = random.randint(0, len(self.__random_items) - 1)
        next_item = self.__random_items.pop(idx)
        self.__load_file(next_item, MediaWidget.DIRECTION_NEXT)
        
        return True



    def __on_btn_back(self):
        """
        Reacts on pressing the [Back] button.
        """

        if (self.__subfolder_range):
            self.__close_subfolder()
        
        elif (len(self.__path_stack) > 1):
            self.__path_stack.pop()
            path, list_offset = self.__path_stack.pop()
            self.__load_folder(path, self.__GO_PARENT)
            
            
    def __on_btn_add(self):
        """
        Reacts on pressing the [Add] button.
        """
        
        if (self.__path_stack):
            path, list_offset = self.__path_stack[-1]
            f = path.new_file()
            if (f):
                self.__add_file(f, [], -1)
                self.__list.render()


    def __on_btn_keep(self):
        """
        Reacts on pressing the [Keep] button.
        """

        self.__btn_keep.set_active(True)

        if (self.__current_file):
            self.__current_file.keep()


    def __create_thumbnails(self, path, items_to_thumbnail):
        """
        Creates thumbnails for the given items.
        """

        def on_loaded(thumbpath, item, tn):
            if (item):
                item.set_icon(thumbpath)
                item.invalidate()
                self.__list.invalidate_buffer()
                self.__list.render()
            
            if (tn):
                tn.set_thumbnail(thumbpath)
                tn.invalidate()
            
            if (self.__view_mode == self._VIEWMODE_PLAYER_NORMAL):
                self.emit_event(msgs.CORE_ACT_RENDER_ITEMS)

            # proceed to next thumbnail
            gobject.idle_add(self.__create_thumbnails, path,
                             items_to_thumbnail)
            

        # abort if the user has changed the directory again
        if (self.__path_stack[-1][0] != path): return
        
        if (not self.is_active()): return
    
        if (items_to_thumbnail):
            # hmm, may we want to reorder a bit?
            if (len(items_to_thumbnail) % 10 == 0 and\
                  len(items_to_thumbnail) > 5):
                idx_in_list = self.__list.get_index_at(0)
                item_in_view = self.__items[idx_in_list - 1]
                cnt = 0
                for i in items_to_thumbnail:
                    if (i[2] == item_in_view):
                        items_to_thumbnail = \
                                items_to_thumbnail[cnt:cnt + 5] + \
                                items_to_thumbnail[:cnt] + \
                                items_to_thumbnail[cnt + 5:]
                        break
                    cnt += 1 
                #end for
            #end if            
        
            item, tn, f = items_to_thumbnail.pop(0)

            # load thumbnail
            self.call_service(msgs.MEDIASCANNER_SVC_LOAD_THUMBNAIL, f,
                              on_loaded, item, tn)
        #end if
            


    def __search(self, key):
    
        idx = 0
        for item in self.__items:
            if (key in item.name.lower()):
                self.__list.scroll_to_item(idx + 1)
                if (self.__view_mode == self._VIEWMODE_PLAYER_NORMAL):
                    self.show_strip_item(idx)
                logging.info("search: found '%s' for '%s'" % (item.name, key))
                break
            idx += 1
        #end for


    def show(self):
        
        def f():
            if (self.may_render() and not self.__current_device):
                self.select_strip_item(0)
                return False
            else:
                return True
    
        Viewer.show(self)
        self.change_strip((self, self.__view_mode))
        self.__update_side_strip()
        
        if (not self.__current_device):
            self.__list.clear_items()
            self.__subfolder_range = None
            
            gobject.timeout_add(50, f)


    def hide(self):
    
        if (self.__lib_is_dirty):
            self.emit_event(msgs.CORE_ACT_SCAN_MEDIA, False)
            self.__lib_is_dirty = False
        Viewer.hide(self)

