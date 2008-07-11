from com import Viewer, msgs
from DeviceThumbnail import DeviceThumbnail
from PlayerPane import PlayerPane
from ListItem import ListItem
from mediabox.TrackList import TrackList
from ui.ImageButton import ImageButton
from ui import dialogs
from mediabox.ThrobberDialog import ThrobberDialog
from utils import threads
from utils import logging
from utils.Downloader import Downloader
from mediabox import viewmodes
import theme

import md5
import os
import time
import threading
import urllib
import gtk
import gobject


class FolderViewer(Viewer):
    """
    Viewer component for browsing storage devices with style.
    """

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_folders
    ICON_ACTIVE = theme.viewer_folders_active
    PRIORITY = 0
    
    __GO_PARENT = 0
    __GO_CHILD = 1
    __GO_NEW = 2
    

    def __init__(self):
    
        # table of devices: id -> rootpath
        self.__devices = {}
        
        # the currently selected device and path stack
        self.__current_device = None
        self.__path_stack = []
        
        self.__device_items = []
        
        # file items of the current directory
        self.__items = []
    
        # table: url -> item receiving the thumbnail
        self.__items_downloading_thumbnails = {}
    
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
        self.__player_pane.connect_clicked(self.__on_click_player_pane)
        self.__set_show_player(False)
        
        
        # toolbar
        self.__btn_back = ImageButton(theme.btn_previous_1,
                                      theme.btn_previous_2)
        self.__btn_back.connect_clicked(self.__on_btn_back)

        tbset = self.new_toolbar_set(self.__btn_back)
        self.set_toolbar_set(tbset)


    
    def __set_show_player(self, value):
    
        w, h = self.__player_pane.get_size()

        if (value):
            self.__list.set_geometry(10, 40, 160, 370)
            self.__player_pane.set_geometry(180, 0, 620, 480)
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NO_STRIP)
        else:
            self.__list.set_geometry(0, 40, 560, 370)
            self.__player_pane.set_geometry(580, 0, 40, 480)
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NORMAL)

        for item in self.__list.get_items():
            item.set_thin_mode(value)

        self.emit_event(msgs.CORE_ACT_RENDER_ALL)


    def __on_click_player_pane(self):
            
        w, h = self.__player_pane.get_size()    
        if (w > 100):
            self.__set_show_player(False)
        else:
            self.__set_show_player(True)
        

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
                    self.__load(root, self.__GO_NEW)
                
                
    def __on_item_clicked(self, item, idx, px, py):

        w, h = self.__player_pane.get_size()    
        if (px >= 80 and w > 100):
            self.__on_item_button(item, idx, item.BUTTON_PLAY)
            
                            
                
    def __on_item_button(self, item, idx, button):
    
        if (button == item.BUTTON_PLAY):
            entry = self.__items[idx]
            self.__list.hilight(idx)

            if (entry.mimetype == entry.DIRECTORY):
                path = entry.path
                self.__path_stack[-1][1] = self.__list.get_offset()
                self.__path_stack.append([entry, 0])
                gobject.timeout_add(250, self.__load, entry, self.__GO_CHILD)
            else:
                uri = entry.get_resource()
                
                # get media widget
                media_widget = self.call_service(
                               msgs.MEDIAWIDGETREGISTRY_SVC_GET_WIDGET,
                               0, entry.mimetype)
                logging.debug("using media widget [%s] for MIME type %s" \
                              % (str(media_widget), entry.mimetype))
                self.add(media_widget)
                self.__player_pane.set_media_widget(media_widget)
                self.__set_show_player(True)
                media_widget.load(uri)


    def __on_btn_back(self):
    
        if (len(self.__path_stack) > 1):
            self.__path_stack.pop()
            path, list_offset = self.__path_stack[-1]
            self.__load(path, self.__GO_PARENT)


    def __on_download_thumbnail(self, cmd, url, *args):
    
        if (cmd == Downloader().DOWNLOAD_FINISHED):
            f, item = self.__items_downloading_thumbnails.get(url)
            if (not item): return

            data = args[0]
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

        url = f.thumbnail
        self.__items_downloading_thumbnails[url] = (f, item)
        downloader = Downloader()
        downloader.get_async(url, self.__on_download_thumbnail)


    def __lookup_icon(self, entry):

        return self.call_service(msgs.MEDIASCANNER_SVC_GET_THUMBNAIL, entry)


    def __item_loader(self, path, items):
    
        # abort if the user has changed the directory again
        if (self.__path_stack[-1][0] != path): return
        
        entry = items.pop(0)
        self.__add_file(entry)
        
        if (items):
            gobject.idle_add(self.__item_loader, path, items)
        else:
            #self.__list.set_offset(self.__path_stack[-1][1])
            pass


    def __add_file(self, entry):
        """
        Adds the given file item to the list.
        """

        if (entry.mimetype == entry.DIRECTORY):
            icon = self.__lookup_icon(entry)
            info = "%d items" % entry.child_count
        else:                
            icon = self.__lookup_icon(entry)
            info = entry.info
    
        item = ListItem(entry, icon)
        self.__list.append_item(item)
        self.__items.append(entry)
        
        if (entry.thumbnail):
            self.__download_icon(item, entry)
    
    


    def __load(self, path, direction):
        
        def loader_thread(path, entries, finished):
            try:        
                entries += path.get_children()
            except:
                import traceback; traceback.print_exc()
                pass
            finished.set()

        
        def comparator(a, b):
            # place directories on top
            if (a.mimetype == a.DIRECTORY and
                b.mimetype != a.DIRECTORY):
                return -1
            elif (a.mimetype != a.DIRECTORY and
                  b.mimetype == a.DIRECTORY):
                return 1
            else:
                return cmp(a.name, b.name)

        self.__list.set_frozen(True)                
        self.__throbber.set_text("Retrieving Directory")
        self.__throbber.set_visible(True)
        self.__throbber.render()

        self.__items = []
        self.__items_downloading_thumbnails.clear()
        
        finished = threading.Event()
        entries = []
        threads.run_threaded(loader_thread, path, entries, finished)
        now = time.time()
        aborted = False
        while (not finished.isSet()):
            if (time.time() - now >= 20):
                aborted = True
                break
            self.__throbber.rotate()        
        #end while
        
        #self.__throbber.set_text("Processing")
        self.__throbber.set_visible(False)
        self.__list.set_frozen(False)
        self.__list.render()

        entries.sort(comparator)
        
        # add the first 5 items at once and the rest in the background
        entries1 = entries[:5]
        entries2 = entries[5:]

        self.__list.set_frozen(True)
        self.__list.clear_items()
        for entry in entries1:
            self.__add_file(entry)
        self.__list.set_frozen(False)

        if (aborted):
            dialogs.error("Timeout", "Connection timed out.")

        else:
            if (direction == self.__GO_PARENT):
                self.__list.fx_slide_right()
            elif (direction == self.__GO_CHILD):
                self.__list.fx_slide_left()
            else:
                self.__list.render()
                                
            if (entries2):
                gobject.idle_add(self.__item_loader, path, entries2)


    def search(self, key):
    
        idx = 0
        for item in self.__items:
            if (key in item.name.lower()):
                self.__list.scroll_to_item(idx)
                logging.info("search: found '%s' for '%s'" % (item.name, key))
                break
            idx += 1
        #end for

