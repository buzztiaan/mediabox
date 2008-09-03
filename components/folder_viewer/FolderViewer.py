from com import Viewer, msgs
from DeviceThumbnail import DeviceThumbnail
from FileThumbnail import FileThumbnail
from HeaderItem import HeaderItem
from ListItem import ListItem
from FolderItem import FolderItem
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


_VIEWMODE_NONE = -1
_VIEWMODE_NO_PLAYER = 0
_VIEWMODE_PLAYER_NORMAL = 1
_VIEWMODE_PLAYER_FULLSCREEN = 2
_VIEWMODE_LIBRARY = 3


class FolderViewer(Viewer):
    """
    Viewer component for browsing storage devices with style.
    """

    PATH = os.path.dirname(__file__)
    ICON = theme.mb_viewer_folder
    PRIORITY = 0
    
    __GO_PARENT = 0
    __GO_CHILD = 1
    __GO_NEW = 2
    

    def __init__(self):
    
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
    
        # table: file -> item receiving the thumbnail
        self.__items_downloading_thumbnails = {}
    
        self.__view_mode = _VIEWMODE_NONE
        
        # the current media widget
        self.__media_widget = None
    
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
        self.__side_tabs.add_tab(None, "Browser",
                                 self.__set_view_mode, _VIEWMODE_NO_PLAYER)
        self.__side_tabs.add_tab(None, "Player",
                                 self.__set_view_mode, _VIEWMODE_PLAYER_NORMAL)
        self.__side_tabs.add_tab(None, "Library",
                                 self.__set_view_mode, _VIEWMODE_LIBRARY)
        self.add(self.__side_tabs)

        self.__throbber = ThrobberDialog()
        self.__throbber.set_throbber(theme.throbber)
        self.__throbber.set_visible(False)
        self.add(self.__throbber)


        
        # toolbar
        self.__btn_back = ImageButton(theme.mb_btn_dir_up_1,
                                      theme.mb_btn_dir_up_2)
        self.__btn_back.connect_clicked(self.__on_btn_back)

        self.__navigation_tbset = [self.__btn_back]


        self.__set_view_mode(_VIEWMODE_NO_PLAYER)
        gobject.idle_add(self.__init_library)


    def __set_view_mode(self, mode):
    
        if (mode == self.__view_mode): return
        self.__view_mode = mode
    
        if (mode == _VIEWMODE_NO_PLAYER):
            self.__side_tabs.set_pos(560 + 4, 0 + 4)
            self.__side_tabs.set_visible(True)
            self.__list.set_visible(True)
            self.__media_box.set_visible(False)
            #if (self.__media_widget):
            #    self.__media_widget.set_visible(False)
            self.__lib_list.set_visible(False)
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NORMAL)
            
            self.set_toolbar(self.__navigation_tbset)
            if (self.__current_device):
                self.set_title(self.__current_device.get_name())

            self.__update_device_list()

            #if (mode != self.__view_mode):
            if (self.__current_file in self.__items):
                idx = self.__items.index(self.__current_file)
                self.__list.hilight(idx + 1)
                self.__list.scroll_to_item(idx + 1)

            self.emit_event(msgs.CORE_ACT_RENDER_ALL)

        elif (mode == _VIEWMODE_PLAYER_NORMAL):
            self.__side_tabs.set_pos(560 + 4, 0 + 4)
            self.__side_tabs.set_visible(True)
            if (self.__media_widget):
            #    self.__media_widget.set_visible(True)
            #    self.__media_widget.set_geometry(2, 2, 560 - 14, 370 - 4)
                tbset = self.__media_widget.get_controls()
            else:
                tbset = []
            self.__list.set_visible(False)
            self.__lib_list.set_visible(False)
            self.__media_box.set_visible(True)
            self.__media_box.set_geometry(2, 2, 560 - 4, 370 - 4)
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NORMAL)

            self.set_toolbar(tbset)
            if (self.__current_file):
                self.set_title(self.__current_file.name)

            #if (mode != self.__view_mode):
            self.set_collection(self.__thumbnails)
            if (self.__current_file in self.__non_folder_items):
                idx = self.__non_folder_items.index(self.__current_file)
                self.emit_event(msgs.CORE_ACT_SELECT_ITEM, idx)

            self.emit_event(msgs.CORE_ACT_RENDER_ALL)

        elif (mode == _VIEWMODE_PLAYER_FULLSCREEN):                        
            #if (self.__media_widget):
            #    self.__media_widget.set_geometry(0, 0, 800, 480)
            self.__side_tabs.set_visible(False)
            self.__list.set_visible(False)
            self.__lib_list.set_visible(False)
            self.__media_box.set_visible(True)
            self.__media_box.set_geometry(0, 0, 800, 480)
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.FULLSCREEN)

            self.render()
            
        elif (mode == _VIEWMODE_LIBRARY):
            self.__side_tabs.set_pos(740 + 4, 0 + 4)
            self.__side_tabs.set_visible(True)
            self.__list.set_visible(False)
            #if (self.__media_widget):
            #    self.__media_widget.set_visible(False)
            self.__lib_list.set_visible(True)
            self.__media_box.set_visible(False)

            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NO_STRIP)
            
            self.set_toolbar([])
            self.set_title("Media Library")
            self.emit_event(msgs.CORE_ACT_RENDER_ALL)
        
          

    def __on_toggle_fullscreen(self):
    
        if (self.__view_mode == _VIEWMODE_PLAYER_FULLSCREEN):
            self.__set_view_mode(_VIEWMODE_PLAYER_NORMAL)
        else:
            self.__set_view_mode(_VIEWMODE_PLAYER_FULLSCREEN)
        

    def __add_device(self, ident, device):

        self.__devices[ident] = device
        self.__update_device_list()
        
        
    def __remove_device(self, uuid):
    
        try:
            del self.__devices[uuid]
        except:
            pass
        self.__update_device_list()


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
            self.emit_event(msgs.CORE_ACT_SELECT_ITEM, idx)


    def handle_event(self, event, *args):
    
        # watch for new storage devices
        if (event == msgs.CORE_EV_DEVICE_ADDED):
            ident, device = args
            self.__add_device(ident, device)
            
        # remove gone storage devices
        elif (event == msgs.CORE_EV_DEVICE_REMOVED):
            uuid = args[0]
            self.__remove_device(uuid)
            
        elif (event == msgs.MEDIA_ACT_STOP):
            if (self.__media_widget):
                self.__media_widget.stop()
            
        if (self.is_active()):
            # load selected device or file
            if (event == msgs.CORE_ACT_LOAD_ITEM):
                idx = args[0]
                if (self.__view_mode == _VIEWMODE_NO_PLAYER):
                    dev = self.__device_items[idx]
                    if (dev != self.__current_device):
                        self.__current_device = dev
                        root = dev.get_root()
                        self.__path_stack = [[root, 0]]
                        self.set_title(dev.get_name())
                        self.__load(root, self.__GO_NEW)
                        
                elif (self.__view_mode == _VIEWMODE_PLAYER_NORMAL):
                    item = self.__non_folder_items[idx]
                    if (item != self.__current_file):
                        self.__load_item(item)

            # provide search-as-you-type
            elif (event == msgs.CORE_ACT_SEARCH_ITEM):
                key = args[0]
                self.__search(key)                

            if (self.__media_widget):
                # watch FULLSCREEN hw key
                if (event == msgs.HWKEY_EV_FULLSCREEN):
                    if (self.__view_mode in \
                      (_VIEWMODE_PLAYER_NORMAL, _VIEWMODE_PLAYER_FULLSCREEN)):
                        self.__on_toggle_fullscreen()
                # watch INCREMENT hw key
                elif (event == msgs.HWKEY_EV_INCREMENT):
                    self.__media_widget.increment()
                # watch DECREMENT hw key
                elif (event == msgs.HWKEY_EV_DECREMENT):
                    self.__media_widget.decrement()
            #end if
            
        #end if



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
            gobject.idle_add(self.__load_item, entry)

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

        


    def __load_item(self, f):
    
        if (f.mimetype == f.DIRECTORY):
            # only enter directories in full list view
            if (self.__view_mode == _VIEWMODE_NO_PLAYER):
                path = f.path
                self.__path_stack[-1][1] = self.__list.get_offset()
                self.__path_stack.append([f, 0])
                gobject.timeout_add(250, self.__load, f, self.__GO_CHILD)
        else:
            self.__current_file = f
            self.set_title(f.name)

            # get media widget
            if (self.__media_widget):
                self.__media_box.remove(self.__media_widget)
                
            self.__media_widget = self.call_service(
                            msgs.MEDIAWIDGETREGISTRY_SVC_GET_WIDGET,
                            self, f.mimetype)
            self.set_toolbar(self.__media_widget.get_controls())
            self.__media_widget.set_visible(True)
            self.__media_widget.connect_media_position(self.__on_media_position)
            self.__media_widget.connect_media_eof(self.__on_media_eof)
            self.__media_widget.connect_media_volume(self.__on_media_volume)
            self.__media_widget.connect_fullscreen_toggled(
                                                self.__on_toggle_fullscreen)
            logging.debug("using media widget [%s] for MIME type %s" \
                            % (str(self.__media_widget), f.mimetype))
            self.__media_box.add(self.__media_widget)
            self.__side_tabs.select_tab(1)
            self.emit_event(msgs.CORE_ACT_RENDER_ALL)

            if (f.mimetype in mimetypes.get_audio_types()):
                try:
                    fd = f.get_fd()
                    f.tags = idtags.read_fd(fd)
                    fd.close()
                except:
                    pass                

            self.__media_widget.load(f)
            if (f.mimetype in mimetypes.get_audio_types() +
                              mimetypes.get_video_types()):
                self.emit_event(msgs.MEDIA_EV_LOADED, self, f)


    def __on_media_position(self, info):
        """
        Reacts when the media playback position has changed.
        """
    
        self.set_info(info)
        
        
    def __on_media_eof(self):
        """
        Reacts on media EOF.
        """
        
        try:
            idx = self.__items.index(self.__current_file)
        except:
            return

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
            path, list_offset = self.__path_stack[-1]
            self.__load(path, self.__GO_PARENT)


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
            self.emit_event(msgs.CORE_ACT_RENDER_ITEMS)
            
            gobject.idle_add(self.__create_thumbnails, path, items_to_thumbnail)
            

        # abort if the user has changed the directory again
        if (self.__path_stack[-1][0] != path): return
    
        if (items_to_thumbnail):
            item, tn, f = items_to_thumbnail.pop(0)
            if (f.thumbnail):
                self.__items_downloading_thumbnails[f] = (item, tn)
                Downloader(f.thumbnail, self.__on_download_thumbnail, f, [""],
                           path, items_to_thumbnail)
            else:
                self.call_service(msgs.MEDIASCANNER_SVC_SCAN_FILE, f,
                                  on_created, item, tn)
                #item.set_icon(thumbpath)
                #item.invalidate()
                #self.__list.invalidate_buffer()
                #self.__list.render()
            #gobject.idle_add(self.__create_thumbnails, path, items_to_thumbnail)
        #end if

         
    def __add_file(self, entry, items_to_thumbnail):
        """
        Adds the given file item to the list.
        """

        icon = self.call_service(msgs.MEDIASCANNER_SVC_GET_THUMBNAIL, entry)

        tn = FileThumbnail(icon, entry)
        if (entry.mimetype != entry.DIRECTORY):
            self.__thumbnails.append(tn)
        
        if (entry.mimetype == entry.DIRECTORY):
            info = "%d items" % entry.child_count
            item = FolderItem(entry, icon)
        else:                
            info = entry.info   
            item = ListItem(entry, icon)

            if (not os.path.exists(icon)):
                items_to_thumbnail.append((item, tn, entry))
                #self.__download_icon(item, entry)
        
        self.__list.set_frozen(True)
        self.__list.append_item(item)
        self.__list.set_frozen(False)
        self.__items.append(entry)
        
        if (entry.mimetype != entry.DIRECTORY):
            self.__non_folder_items.append(entry)
        



        

    def __load(self, path, direction):
        """
        Loads the given path and displays its contents.
        """
        
        def on_child(f, path, entries, items_to_thumbnail):
            # abort if the user has changed the directory again
            if (self.__path_stack[-1][0] != path): return False

            if (f):
                self.__list.get_item(0).set_info("Loading (%d)..." % len(self.__items))
                entries.append(f)
                self.__add_file(f, items_to_thumbnail)
            else:
                self.__list.get_item(0).set_info("%d items" % len(self.__items))
                # finished loading items; now create thumbnails
                self.__create_thumbnails(path, items_to_thumbnail)
            
            if (not f or len(entries) == 4 or len(entries) % 10 == 0):
                self.__list.invalidate_buffer()
                self.__list.render()
            
            return True
        

        self.__items = []
        self.__non_folder_items = []
        self.__thumbnails = []
        self.__items_downloading_thumbnails.clear()
                        
        self.__list.clear_items()        
        #if (direction == self.__GO_PARENT):
        #    self.__list.fx_slide_right()
        #elif (direction == self.__GO_CHILD):
        #    self.__list.fx_slide_left()

        header = HeaderItem(path.name)
        header.set_info("Connecting...")
        self.__list.append_item(header)
        
        gobject.timeout_add(0, path.get_children_async, on_child, path, [], [])



    def __search(self, key):
    
        idx = 0
        for item in self.__items:
            if (key in item.name.lower()):
                self.__list.scroll_to_item(idx + 1)
                logging.info("search: found '%s' for '%s'" % (item.name, key))
                break
            idx += 1
        #end for



    def show(self):
    
        Viewer.show(self)
        self.emit_event(msgs.SSDP_ACT_SEARCH_DEVICES)

