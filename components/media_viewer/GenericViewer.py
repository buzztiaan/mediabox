from com import Viewer, msgs
from storage import Device
from DeviceThumbnail import DeviceThumbnail
from FileThumbnail import FileThumbnail
from HeaderItem import HeaderItem
from MediaItem import MediaItem
from SubItem import SubItem
from LibItem import LibItem
from mediabox.TrackList import TrackList
from ui.BoxLayout import BoxLayout
from ui.ImageButton import ImageButton
from ui.SideTabs import SideTabs
from ui import dialogs
from mediabox.ThrobberDialog import ThrobberDialog
from utils import mimetypes
from utils import logging
from io import Downloader
from mediabox import viewmodes
from mediabox import config
import idtags
import theme

import os
import time
import urllib
import gtk
import gobject


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
    _VIEWMODE_PLAYER_NORMAL = 1
    _VIEWMODE_PLAYER_FULLSCREEN = 2
    _VIEWMODE_LIBRARY = 3
    

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
        self.__non_folder_items = []
        self.__thumbnails = []
        
        # range of subfolder, if any
        self.__subfolder_range = None

        # table: file -> item receiving the thumbnail
        self.__items_downloading_thumbnails = {}
    
        self.__view_mode = self._VIEWMODE_NONE
        
        # the current media widget
        self.__media_widget = None
        
        # timestamp of the last list rendering
        self.__last_list_render_time = 0
    
        Viewer.__init__(self)
        
        # file list
        self.__list = TrackList()
        self.__list.set_geometry(0, 0, 560, 370)
        self.add(self.__list)        
        self.__list.connect_button_clicked(self.__on_item_button)

        # library list
        self.__lib_list = TrackList()
        self.__lib_list.set_geometry(10, 0, 730, 370)
        self.__lib_list.set_visible(False)
        self.add(self.__lib_list)
        self.__lib_list.connect_button_clicked(self.__on_lib_item_button)
        self.__lib_list.connect_item_clicked(self.__on_lib_item_set_types)
        
        # media widget box
        self.__media_box = BoxLayout()
        self.add(self.__media_box)

        # side tabs
        self.__side_tabs = SideTabs()
        self.__side_tabs.set_geometry(560 + 4, 0 + 4, 60 - 8, 370 - 8)
        #self.__side_tabs.add_tab(None, "Browser",
        #                         self.__set_view_mode, self._VIEWMODE_BROWSER)
        #self.__side_tabs.add_tab(None, "Player",
        #                         self.__set_view_mode, self._VIEWMODE_PLAYER_NORMAL)
        #self.__side_tabs.add_tab(None, "Library",
        #                         self.__set_view_mode, self._VIEWMODE_LIBRARY)
        self.add(self.__side_tabs)

        self.__throbber = ThrobberDialog()
        self.__throbber.set_throbber(theme.throbber)
        self.__throbber.set_visible(False)
        self.add(self.__throbber)



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
        #self.__btn_prev.connect_clicked(self.__on_previous)

        self.__btn_next = ImageButton(theme.mb_btn_next_1,
                                      theme.mb_btn_next_2)
        #self.__btn_next.connect_clicked(self.__on_next)

        self.accept_device_types(Device.TYPE_GENERIC)
        #self.add_tab("Browser", self._VIEWMODE_BROWSER)
        #self.add_tab("Player", self._VIEWMODE_PLAYER_NORMAL)
        #self.add_tab("Library", self._VIEWMODE_LIBRARY)
        
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
    
        self.__side_tabs.add_tab(None, name, self.__set_view_mode, view_mode)


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
            self.__update_device_list()
        
        
    def __remove_device(self, ident):
        """
        Removes the device specified by the given identifier.
        """
    
        try:
            del self.__devices[ident]
            self.__update_device_list()
        except:
            pass


    def __update_device_list(self):
        """
        Updates the list of available storage devices.
        """
    
        items = []
        self.__device_items = []
        devs = self.__devices.items()
        
        # sort devices before putting into the list
        devs.sort(lambda a,b:cmp((a[1].CATEGORY, a[1].get_name()),
                                 (b[1].CATEGORY, b[1].get_name())))
        
        for ident, dev in devs:
            tn = DeviceThumbnail(dev)            
            items.append(tn)
            self.__device_items.append(dev)
        #end for
    
        self.set_collection(items)
        if (self.__current_device in self.__device_items):
            idx = self.__device_items.index(self.__current_device)
            self.emit_event(msgs.CORE_ACT_HILIGHT_ITEM, idx)        


    def __update_toolbar(self):
        """
        Updates the contents of the toolbar.
        """
        
        items = []
        
        if (self.__path_stack and self.__path_stack[-1][0].can_add):
            items.append(self.__btn_add)
        
        if (self.__media_widget):
            items += self.__media_widget.get_controls()
            
        items.append(self.__btn_prev)
        items.append(self.__btn_next)
                
        if (self.__view_mode == self._VIEWMODE_BROWSER):
            items.append(self.__btn_back)
            
        self.set_toolbar(items)


    def __set_view_mode(self, mode):
    
        if (mode == self.__view_mode): return
        self.__view_mode = mode
    
        if (mode == self._VIEWMODE_BROWSER):
            self.emit_event(msgs.UI_ACT_FREEZE)

            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NORMAL)
            self.__update_device_list()
            
            self.__side_tabs.set_pos(560 + 4, 0 + 4)
            self.__side_tabs.set_visible(True)
            self.__list.set_visible(True)
            self.__media_box.set_visible(False)
            self.__lib_list.set_visible(False)

            self.__update_toolbar()
            if (self.__current_device):
                self.set_title(self.__current_device.get_name())

            # hilight current item        
            if (self.__current_file in self.__items):
                idx = self.__items.index(self.__current_file)
                self.__list.hilight(idx + 1)
                self.__list.scroll_to_item(idx + 1)
                        

            self.emit_event(msgs.UI_ACT_THAW)


        elif (mode == self._VIEWMODE_PLAYER_NORMAL):
            self.emit_event(msgs.UI_ACT_FREEZE)

            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NORMAL)
            
            self.__side_tabs.set_pos(560 + 4, 0 + 4)
            self.__side_tabs.set_visible(True)
            self.__list.set_visible(False)
            self.__lib_list.set_visible(False)
            self.__media_box.set_visible(True)
            self.__media_box.set_geometry(2, 2, 560 - 4, 370 - 4)

            self.__update_toolbar()
            if (self.__current_file):
                self.set_title(self.__current_file.name)

            # hilight current item
            self.set_collection(self.__thumbnails)
            if (self.__current_file in self.__non_folder_items):
                idx = self.__non_folder_items.index(self.__current_file)
                self.emit_event(msgs.CORE_ACT_HILIGHT_ITEM, idx)

            self.emit_event(msgs.UI_ACT_THAW)


        elif (mode == self._VIEWMODE_PLAYER_FULLSCREEN):
            self.__side_tabs.set_visible(False)
            self.__list.set_visible(False)
            self.__lib_list.set_visible(False)
            self.__media_box.set_visible(True)
            self.__media_box.set_geometry(0, 0, 800, 480)
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.FULLSCREEN)

            self.render()


        elif (mode == self._VIEWMODE_LIBRARY):
            self.emit_event(msgs.UI_ACT_FREEZE)
            
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NO_STRIP)
            
            self.__side_tabs.set_pos(740 + 4, 0 + 4)
            self.__side_tabs.set_visible(True)
            self.__list.set_visible(False)
            self.__lib_list.set_visible(True)
            self.__media_box.set_visible(False)
            
            self.__update_toolbar()
            self.set_title("Media Library")
            
            self.emit_event(msgs.UI_ACT_THAW)
        
          

    def __on_toggle_fullscreen(self):
    
        if (self.__view_mode == self._VIEWMODE_PLAYER_FULLSCREEN):
            self.__set_view_mode(self._VIEWMODE_PLAYER_NORMAL)
        else:
            self.__set_view_mode(self._VIEWMODE_PLAYER_FULLSCREEN)
        







    def handle_event(self, msg, *args):
        """
        Handles incoming messages.
        """
    
        Viewer.handle_event(self, msg, *args)
        
        # watch for new storage devices
        if (msg == msgs.CORE_EV_DEVICE_ADDED):
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
        
        
        
        # the following messages are only accepted when the viewer is active
        if (not self.is_active()): return
        
        
        if (msg == msgs.HWKEY_EV_DOWN):
            w, h = self.__list.get_size()
            idx = self.__list.get_index_at(h)
            if (idx != -1):
                self.__list.scroll_to_item(min(len(self.__items), idx + 2))

            
        elif (msg == msgs.HWKEY_EV_UP):
            idx = self.__list.get_index_at(0)
            if (idx != -1):
                self.__list.scroll_to_item(max(0, idx - 2))
            #self.__list.impulse(0, -7.075)
        
        
        # load selected device or file
        if (msg == msgs.CORE_ACT_LOAD_ITEM):
            idx = args[0]
            if (self.__view_mode == self._VIEWMODE_BROWSER):
                dev = self.__device_items[idx]
                if (dev != self.__current_device):
                    self.__load_device(dev)
                    
            elif (self.__view_mode == self._VIEWMODE_PLAYER_NORMAL):
                item = self.__non_folder_items[idx]
                if (item != self.__current_file):
                    self.__load_file(item)

        # provide search-as-you-type
        elif (msg == msgs.CORE_ACT_SEARCH_ITEM):
            key = args[0]
            self.__search(key)



        # the following messages are only accepted when we have a media widget
        if (not self.__media_widget): return



        # watch FULLSCREEN hw key
        if (msg == msgs.HWKEY_EV_FULLSCREEN):
            if (self.__view_mode in \
              (self._VIEWMODE_PLAYER_NORMAL, self._VIEWMODE_PLAYER_FULLSCREEN)):
                self.__on_toggle_fullscreen()
                
        # watch INCREMENT hw key
        elif (msg == msgs.HWKEY_EV_INCREMENT):
            self.__media_widget.increment()
            
        # watch DECREMENT hw key
        elif (msg == msgs.HWKEY_EV_DECREMENT):
            self.__media_widget.decrement()



    def __on_lib_item_button(self, item, idx, button):
    
        if (idx == -1): return
    
        if (button == item.BUTTON_REMOVE):
            self.__lib_list.remove_item(idx)
            self.__lib_list.invalidate_buffer()
            self.__lib_list.render()
            self.__save_library()
        
        
    def __on_lib_item_set_types(self, item, idx, px, py):
    
        if (idx == -1): return

        if (px < 208):
            uri = item.get_path()
            mtypes = item.get_media_types()

            if (px < 82):    mtypes ^= 1
            elif (px < 146): mtypes ^= 2
            elif (px < 208): mtypes ^= 4
            item.set_media_types(mtypes)
            self.__lib_list.invalidate_buffer()
            self.__lib_list.render()
            self.__save_library()
        #end if
        

    def __on_item_button(self, item, idx, button):
        
        def on_child(f, items):
            if (f and f.mimetype != f.DIRECTORY):
                items.append(f)
            else:
                self.emit_event(msgs.PLAYLIST_ACT_APPEND, *items)
            return True

        if (idx == -1): return
        
        if (button == item.BUTTON_PLAY):
            entry = self.__items[idx - 1]
            self.__list.hilight(idx)
            gobject.idle_add(self.__load_file, entry)

        elif (button == item.BUTTON_ENQUEUE):
            if (idx == 0):
                path, list_offset = self.__path_stack[-1]
                path.get_children_async(on_child, [])
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
            self.__load_file(f)
            
        elif (button == item.BUTTON_OPEN):
            entry = self.__items[idx - 1]
            gobject.idle_add(self.__insert_folder, entry)
                        
            
    def __init_library(self):
        """
        Loads the library folders.
        """
        
        mediaroots = config.mediaroot()
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
            config.set_mediaroot(mediaroots)

        
    def __load_device(self, device):
        """
        Loads the given device.
        """

        self.__current_device = device
        
        root = device.get_root()
        self.set_title(device.get_name())
        self.__load_folder(root, self.__GO_NEW)



    def __load_file(self, f):
        """
        Loads the given file.
        """

        if (f.mimetype == f.DIRECTORY):
            gobject.timeout_add(250, self.__load_folder, f, self.__GO_CHILD)

        elif (f.mimetype == "audio/x-music-folder"):
            gobject.timeout_add(250, self.__load_folder, f, self.__GO_CHILD)
            
                
        else:
            self.__current_file = f
            self.set_title(f.name)

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
            self.__media_widget.connect_fullscreen_toggled(
                                                self.__on_toggle_fullscreen)
            logging.debug("using media widget [%s] for MIME type %s" \
                            % (str(self.__media_widget), f.mimetype))
            self.__media_box.add(self.__media_widget)

            if (not f.mimetype in mimetypes.get_audio_types()):
                self.__side_tabs.select_tab(1)

            self.emit_event(msgs.UI_ACT_RENDER)
            self.__media_widget.load(f)
            self.emit_event(msgs.MEDIA_EV_LOADED, self, f)


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
                # finished loading items; now create thumbnails
                self.__create_thumbnails(path, items_to_thumbnail)

            now = time.time()
            if (not f or len(entries) == 4 or \
                  now > self.__last_list_render_time + 0.5):
                self.__last_list_render_time = now
            #if (not f or len(entries) == 4 or len(entries) % 10 == 0):
                self.__list.invalidate_buffer()
                self.__list.render()
            
            return True

        self.__close_subfolder()
                   
        # clear items
        self.__items = []
        self.__non_folder_items = []
        self.__thumbnails = []
        self.__items_downloading_thumbnails.clear()

        # update path stack
        if (self.__path_stack):
            self.__path_stack[-1][1] = self.__list.get_offset()
        self.__path_stack.append([path, 0])
        print self.__path_stack

        self.__list.clear_items()        
        #if (direction == self.__GO_PARENT):
        #    self.__list.fx_slide_right()
        #elif (direction == self.__GO_CHILD):
        #    self.__list.fx_slide_left()


        header = HeaderItem(path.name)
        header.set_info("Retrieving...")
        self.__list.append_item(header)
    
        self.__update_toolbar()
        self.emit_event(msgs.UI_ACT_RENDER)
        
        gobject.timeout_add(0, path.get_children_async, on_child, path, [], [])



    def __insert_folder(self, path):

        def on_child(f, path, entries, items_to_thumbnail, insert_at):
            # abort if the user has changed the directory again
            if (self.__path_stack[-1][0] != path): return False

            if (f):
                self.__list.get_item(insert_at).set_info("Loading (%d items)" \
                                                         % len(entries))
                self.__add_file(f, items_to_thumbnail, insert_at + len(entries))
                entries.append(f)

            else:
                self.__list.get_item(insert_at).set_info("%d items" % len(entries))
                # finished loading items; now create thumbnails
                self.__create_thumbnails(path, items_to_thumbnail)

            now = time.time()
            self.__subfolder_range = (insert_at, insert_at + len(entries))
            if (not f or len(entries) == 4 or \
                  now > self.__last_list_render_time + 0.5):
                self.__last_list_render_time = now
            #if (not f or len(entries) == 4 or len(entries) % 10 == 0):
                self.__list.invalidate_buffer()
                self.__list.render()
            
            return True
    
        idx = self.__items.index(path)
        self.__list.scroll_to_item(idx + 1, force_on_top = True)
        self.__close_subfolder()
        idx = self.__items.index(path)
    
        # clear items
        self.__non_folder_items = []
        self.__thumbnails = []

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
        
        self.__subfolder_range = None


    def __add_file(self, entry, items_to_thumbnail, insert_at):
        """
        Adds the given file item to the list.
        """

        # lookup thumbnail        
        icon = self.call_service(msgs.MEDIASCANNER_SVC_GET_THUMBNAIL, entry)

        tn = FileThumbnail(icon, entry)
        if (entry.mimetype != entry.DIRECTORY):
            self.__thumbnails.append(tn)
        
        # determine available item buttons
        if (insert_at == -1):
            item = MediaItem(entry, icon)
        else:
            item = SubItem(entry)
        buttons = []
        
        if (entry.mimetype == entry.DIRECTORY):
            buttons.append((item.BUTTON_PLAY, theme.mb_item_btn_play))
            pass
        elif (entry.mimetype == "audio/x-music-folder"):    
            buttons.append((item.BUTTON_OPEN, theme.mb_item_btn_play))
        else:
            buttons.append((item.BUTTON_PLAY, theme.mb_item_btn_play))
            buttons.append((item.BUTTON_ENQUEUE, theme.mb_item_btn_enqueue))
            
        if (entry.can_delete):
            buttons.append((item.BUTTON_REMOVE, theme.mb_item_btn_remove))
        item.set_buttons(*buttons)

        # remember if thumbnail does not yet exist
        if (insert_at == -1 and not os.path.exists(icon) and entry.is_local):
            items_to_thumbnail.append((item, tn, entry))
            #self.__download_icon(item, entry)
        
        self.__list.set_frozen(True)
        if (insert_at == -1):
            self.__list.append_item(item)
            self.__items.append(entry)
        else:
            self.__list.insert_item(item, insert_at)
            self.__items.insert(insert_at, entry)
        self.__list.set_frozen(False)
        
        if (entry.mimetype != entry.DIRECTORY):
            self.__non_folder_items.append(entry)
            
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
        
        self.emit_event(msgs.MEDIA_EV_EOF)

        #try:
        #    idx = self.__items.index(self.__current_file)
        #except:
        #    return

        #if (idx < len(self.__items) - 1):
        #    new_item = self.__items[idx + 1]
        #    self.__list.hilight(idx + 1)
        #    gobject.idle_add(self.__load_item, new_item)


    def __on_media_volume(self, volume):
        """
        Reacts on changing the sound volume.
        """

        self.emit_event(msgs.MEDIA_EV_VOLUME_CHANGED, volume)


    def __on_btn_back(self):
        """
        Reacts on pressing the [Back] button.
        """
    
        if (len(self.__path_stack) > 1):
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
                self.__add_file(f, [])
                self.__list.render()


    def __on_download_thumbnail(self, d, a, t, f, data, path, items_to_thumbnail):
        """
        Callback for downloading a thumbnail image.
        """
    
        data[0] += d
        if (not d):
            item, tn = self.__items_downloading_thumbnails.get(f, (None, None))
            if (not item): return

            data = data[0]
            if (data):
                loader = gtk.gdk.PixbufLoader()
                loader.write(data)
                loader.close()
                pbuf = loader.get_pixbuf()
                
                thumbpath = self.call_service(msgs.MEDIASCANNER_SVC_SET_THUMBNAIL,
                                              f, pbuf)
                del pbuf
                item.set_icon(thumbpath)
                item.invalidate()
                self.__list.invalidate_buffer()
                self.__list.render()
                
                tn.set_thumbnail(thumbpath)
                tn.invalidate()
                if (self.__view_mode == self._VIEWMODE_PLAYER_NORMAL):
                    self.emit_event(msgs.CORE_ACT_RENDER_ITEMS)
            #end if
            
            gobject.idle_add(self.__create_thumbnails, path, items_to_thumbnail)
        #end if


    def __create_thumbnails(self, path, items_to_thumbnail):
        """
        Creates thumbnails for the given items.
        """

        def on_created(thumbpath, item, tn):
            item.set_icon(thumbpath)
            item.invalidate()
            self.__list.invalidate_buffer()
            self.__list.render()
            
            tn.set_thumbnail(thumbpath)
            tn.invalidate()
            
            if (self.__view_mode == self._VIEWMODE_PLAYER_NORMAL):
                self.emit_event(msgs.CORE_ACT_RENDER_ITEMS)

            # proceed to next thumbnail
            gobject.idle_add(self.__create_thumbnails, path, items_to_thumbnail)
            

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
            if (f.thumbnail):
                # a thumbnail URI is specified
                self.__items_downloading_thumbnails[f] = (item, tn)
                Downloader(f.thumbnail, self.__on_download_thumbnail, f, [""],
                           path, items_to_thumbnail)
            else:
                # create new thumbnail
                self.call_service(msgs.MEDIASCANNER_SVC_SCAN_FILE, f,
                                  on_created, item, tn)

            #end if
        #end if


    def __search(self, key):
    
        idx = 0
        for item in self.__items:
            if (key in item.name.lower()):
                self.__list.scroll_to_item(idx + 1)
                if (self.__view_mode == self._VIEWMODE_PLAYER_NORMAL):
                    self.emit_event(msgs.CORE_ACT_SCROLL_TO_ITEM, idx)                
                logging.info("search: found '%s' for '%s'" % (item.name, key))
                break
            idx += 1
        #end for



    def show(self):
    
        Viewer.show(self)
        self.emit_event(msgs.SSDP_ACT_SEARCH_DEVICES)

