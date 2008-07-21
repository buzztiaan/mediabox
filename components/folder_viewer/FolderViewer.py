from com import Viewer, msgs
from DeviceThumbnail import DeviceThumbnail
from PlayerPane import PlayerPane
from ListItem import ListItem
from FolderItem import FolderItem
from mediabox.TrackList import TrackList
from ui.ImageButton import ImageButton
from ui import dialogs
from mediabox.ThrobberDialog import ThrobberDialog
from utils import logging
from io import Downloader
from mediabox import viewmodes
import idtags
import theme

import os
import time
import urllib
import gtk
import gobject


_VIEWMODE_NO_PLAYER = 0
_VIEWMODE_PLAYER_NORMAL = 1
_VIEWMODE_PLAYER_FULLSCREEN = 2


class FolderViewer(Viewer):
    """
    Viewer component for browsing storage devices with style.
    """

    PATH = os.path.dirname(__file__)
    ICON = theme.mb_viewer_folder
    ICON_ACTIVE = theme.mb_viewer_folder_active
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
    
        # table: url -> item receiving the thumbnail
        self.__items_downloading_thumbnails = {}
    
        self.__view_mode = _VIEWMODE_NO_PLAYER
    
        Viewer.__init__(self)
        
        self.__list = TrackList()
        self.__list.set_geometry(0, 40, 560, 370)
        self.add(self.__list)
        
        self.__list.connect_item_clicked(self.__on_item_clicked)
        self.__list.connect_button_clicked(self.__on_item_button)

        self.__throbber = ThrobberDialog()
        self.__throbber.set_throbber(theme.throbber)
        self.__throbber.set_visible(False)
        self.add(self.__throbber)
        
        # player pane
        self.__player_pane = PlayerPane()
        self.add(self.__player_pane)
        self.__player_pane.connect_toggled(self.__on_toggle_player_pane)
        
        
        # toolbar
        self.__btn_back = ImageButton(theme.btn_previous_1,
                                      theme.btn_previous_2)
        self.__btn_back.connect_clicked(self.__on_btn_back)

        self.__navigation_tbset = self.new_toolbar_set(self.__btn_back)


        self.__set_view_mode(_VIEWMODE_NO_PLAYER)


    def __set_view_mode(self, mode):
    
        thin_mode = False
        if (mode == _VIEWMODE_NO_PLAYER):
            self.__list.set_visible(True)
            self.__list.set_geometry(0, 40, 560, 370)
            self.__player_pane.set_geometry(580, 40, 40, 370)
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NORMAL)
            self.set_toolbar_set(self.__navigation_tbset)
            if (self.__current_device):
                self.set_title(self.__current_device.get_name())

        elif (mode == _VIEWMODE_PLAYER_NORMAL):
            self.__list.set_visible(True)        
            self.__list.set_geometry(10, 40, 160, 370)
            self.__player_pane.set_geometry(180, 32, 620, 388)
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NO_STRIP)
            self.set_toolbar_set(self.__player_pane.get_controls())
            if (self.__current_file):
                self.set_title(self.__current_file.name)
            thin_mode = True            

        elif (mode == _VIEWMODE_PLAYER_FULLSCREEN):                        
            self.__list.set_visible(False)
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.FULLSCREEN)
            self.__player_pane.set_geometry(0, 0, 800, 480)
        
        for item in self.__list.get_items():
            item.set_thin_mode(thin_mode)
            item.invalidate()
        
        self.__view_mode = mode
        
        if (mode == _VIEWMODE_PLAYER_FULLSCREEN):
            # a full render is not needed when going fullscreen, so we can
            # speed it up
            self.__player_pane.render()
        else:
            self.emit_event(msgs.CORE_ACT_RENDER_ALL)


    def __on_toggle_player_pane(self):
            
        if (self.__view_mode == _VIEWMODE_NO_PLAYER):
            self.__set_view_mode(_VIEWMODE_PLAYER_NORMAL)
        else:
            self.__set_view_mode(_VIEWMODE_NO_PLAYER)
            

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
    
        items = []
        self.__device_items = []
        for ident, dev in self.__devices.items():
            tn = DeviceThumbnail(dev)            
            items.append(tn)
            self.__device_items.append(dev)
        #end for
        #items.sort(lambda a,b:cmp(a.name, b.name))
    
        self.set_collection(items)


    def handle_event(self, event, *args):
    
        if (event == msgs.CORE_EV_DEVICE_ADDED):
            ident, device = args
            self.__add_device(ident, device)
            
        elif (event == msgs.CORE_EV_DEVICE_REMOVED):
            uuid = args[0]
            self.__remove_device(uuid)
            
        if (self.is_active()):
            if (event == msgs.CORE_ACT_LOAD_ITEM):
                idx = args[0]
                dev = self.__device_items[idx]
                if (dev):
                    self.__current_device = dev
                    root = dev.get_root()
                    self.__path_stack = [[root, 0]]
                    self.set_title(dev.get_name())
                    self.__load(root, self.__GO_NEW)
                
            elif (event == msgs.CORE_ACT_SEARCH_ITEM):
                key = args[0]
                self.__search(key)                
                
                
    def __on_item_clicked(self, item, idx, px, py):

        w, h = self.__player_pane.get_size()    
        if (px >= 80 and w > 100):
            self.__on_item_button(item, idx, item.BUTTON_PLAY)
            
                            
                
    def __on_item_button(self, item, idx, button):
    
        if (button == item.BUTTON_PLAY):
            entry = self.__items[idx]
            self.__list.hilight(idx)

            if (entry.mimetype == entry.DIRECTORY):
                # only enter directories in full list view
                if (self.__view_mode == _VIEWMODE_NO_PLAYER):
                    path = entry.path
                    self.__path_stack[-1][1] = self.__list.get_offset()
                    self.__path_stack.append([entry, 0])
                    gobject.timeout_add(250, self.__load, entry, self.__GO_CHILD)
            else:
                self.__current_file = entry

                # get media widget
                media_widget = self.call_service(
                               msgs.MEDIAWIDGETREGISTRY_SVC_GET_WIDGET,
                               self, entry.mimetype)
                media_widget.connect_media_position(self.__on_media_position)
                media_widget.connect_fullscreen_toggled(
                                                 self.__on_toggle_fullscreen)
                logging.debug("using media widget [%s] for MIME type %s" \
                              % (str(media_widget), entry.mimetype))
                self.add(media_widget)
                self.__player_pane.set_media_widget(media_widget)                
                self.__set_view_mode(_VIEWMODE_PLAYER_NORMAL)
                self.emit_event(msgs.CORE_ACT_RENDER_ALL)

                if (entry.mimetype.startswith("audio/")):
                    fd = entry.get_fd()
                    entry.tags = idtags.read_fd(fd)
                    fd.close()

                media_widget.load(entry)


        elif (button == item.BUTTON_ENQUEUE):
            entry = self.__items[idx]
            self.emit_event(msgs.PLAYLIST_ACT_APPEND, entry)


    def __on_media_position(self, info):
        """
        Reacts when the media playback position has changed.
        """
    
        self.set_info(info)


    def __on_btn_back(self):
        """
        Reacts on pressing the [Back] button.
        """
    
        if (len(self.__path_stack) > 1):
            self.__path_stack.pop()
            path, list_offset = self.__path_stack[-1]
            self.__load(path, self.__GO_PARENT)


    def __on_download_thumbnail(self, d, a, t, url, data):
        """
        Callback for downloading a thumbnail image.
        """
    
        data[0] += d
        if (not d):
            f, item = self.__items_downloading_thumbnails.get(url, (None, None))
            if (not item): return

            data = data[0]
            print "DOWNLOADED", len(data)
            loader = gtk.gdk.PixbufLoader()
            loader.write(data)
            loader.close()
            pbuf = loader.get_pixbuf()
            
            thumbpath = self.call_service(msgs.MEDIASCANNER_SVC_SET_THUMBNAIL,
                                          f, pbuf)
            del pbuf
            item.set_icon(thumbpath)
            item.render()

            self.__list.render()
        #end if
         
         
    def __download_icon(self, item, f):
        """
        Downloads an icon for the given file.
        """

        url = f.thumbnail
        self.__items_downloading_thumbnails[url] = (f, item)
        Downloader(url, self.__on_download_thumbnail, url, [""])


    def __lookup_icon(self, entry):
        """
        Queries the media scanner for an icon for the given file.
        """

        return self.call_service(msgs.MEDIASCANNER_SVC_GET_THUMBNAIL, entry)


    def __add_file(self, entry):
        """
        Adds the given file item to the list.
        """

        if (entry.mimetype == entry.DIRECTORY):
            icon = self.__lookup_icon(entry)
            info = "%d items" % entry.child_count
            item = FolderItem(entry, icon)
        else:                
            #if (not entry.thumbnail):
            #    self.emit_event(msgs.MEDIASCANNER_ACT_SCAN_FILE, entry)
            icon = self.__lookup_icon(entry)
            info = entry.info   
            item = ListItem(entry, icon)
            
        
        self.__list.append_item(item)
        self.__items.append(entry)
        
        if (self.__view_mode == _VIEWMODE_PLAYER_NORMAL):
            item.set_thin_mode(True)
        else:
            item.set_thin_mode(False)

        if (entry.thumbnail and not os.path.exists(icon)):
            self.__download_icon(item, entry)


    def __load(self, path, direction):
        """
        Loads the given path and displays its contents.
        """
        
        def on_child(f, path, entries):
            # abort if the user has changed the directory again
            if (self.__path_stack[-1][0] != path): return False

            entries.append(f)
            self.__add_file(f)
            
            return True
        

        self.__items = []
        self.__items_downloading_thumbnails.clear()
                        
        self.__list.set_frozen(True)
        self.__list.clear_items()
        self.__list.set_frozen(False)
        
        #if (direction == self.__GO_PARENT):
        #    self.__list.fx_slide_right()
        #elif (direction == self.__GO_CHILD):
        #    self.__list.fx_slide_left()
        self.__list.render()

        entries = []
        try:
            path.get_children_async(on_child, path, entries)
        except:
            pass



    def __search(self, key):
    
        idx = 0
        for item in self.__items:
            if (key in item.name.lower()):
                self.__list.scroll_to_item(idx)
                logging.info("search: found '%s' for '%s'" % (item.name, key))
                break
            idx += 1
        #end for

