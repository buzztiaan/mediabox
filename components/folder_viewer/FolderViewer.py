from com import Viewer, events
from DeviceThumbnail import DeviceThumbnail
from LocalDevice import LocalDevice
from ListItem import ListItem
from mediabox.TrackList import TrackList
from mediascanner.MediaItem import MediaItem
from ui.ImageButton import ImageButton
from ui import dialogs
from mediabox.ThrobberDialog import ThrobberDialog
import mediaplayer
from utils import threads
import theme

import os
import time
import threading


class FolderViewer(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_folders
    ICON_ACTIVE = theme.viewer_folders_active
    PRIORITY = 0
    

    def __init__(self):
    
        # table of UPnP devices: uuid -> device
        self.__devices = {"0": LocalDevice()}
        
        # the currently selected device and path stack
        self.__current_device = None
        self.__path_stack = []
        
        # items of the current directory
        self.__items = []
    
        Viewer.__init__(self)
        
        self.__list = TrackList()
        self.__list.set_geometry(0, 40, 610, 370)
        self.add(self.__list)
        
        self.__list.connect_button_clicked(self.__on_item_button)

        self.__throbber = ThrobberDialog()
        self.__throbber.set_throbber(theme.throbber)
        self.__throbber.set_visible(False)
        self.add(self.__throbber)
        
        # toolbar
        self.__btn_back = ImageButton(theme.btn_previous_1,
                                      theme.btn_previous_2)
        self.__btn_back.connect_clicked(self.__on_btn_back)

        tbset = self.new_toolbar_set(self.__btn_back)
        self.set_toolbar_set(tbset)
              
        self.__update_device_list()  
        
    def __add_device(self, uuid, device):

        if (device.has_content_directory()):
            self.__devices[uuid] = device
            self.__update_device_list()
        
        
    def __remove_device(self, uuid):
    
        try:
            del self.__devices[uuid]
        except:
            pass
        self.__update_device_list()


    def __update_device_list(self):
    
        items = []
        for uuid, dev in self.__devices.items():
            tn = DeviceThumbnail(dev)
            item = MediaItem()
            item.name = dev.get_name()
            item.uri = uuid
            item.thumbnail_pmap = tn
            items.append(item)
        #end for
        items.sort(lambda a,b:cmp(a.name, b.name))
    
        self.set_collection(items)


    def handle_event(self, event, *args):
    
        if (event == events.CORE_EV_DEVICE_ADDED):
            uuid, device = args
            self.__add_device(uuid, device)
            
        elif (event == events.CORE_EV_DEVICE_REMOVED):
            uuid = args[0]
            self.__remove_device(uuid)
            
        if (self.is_active()):
            if (event == events.CORE_ACT_LOAD_ITEM):
                item = args[0]
                uuid = item.uri
                dev = self.__devices.get(uuid)
                if (dev):
                    self.__current_device = dev
                    self.__path_stack = [dev.get_root()]
                    self.__load(dev, dev.get_root())
                
                
    def __on_item_button(self, item, idx, button):
    
        if (button == item.BUTTON_PLAY):
            entry = self.__items[idx]
            if (entry.filetype == entry.DIRECTORY):
                path = entry.path
                self.__path_stack.append(path)
                self.__load(self.__current_device, path)
            else:
                uri = entry.path
                player = mediaplayer.get_player_for_uri(uri)
                player.load_audio(uri)
            
    def __on_btn_back(self):
    
        if (self.__path_stack and self.__path_stack[-1] != "0"):
            self.__path_stack.pop()
            self.__load(self.__current_device, self.__path_stack[-1])
            
        
    def __load(self, dev, path):
        
        def loader_thread(dev, path, entries, finished):
            try:        
                entries += dev.ls(path)
            except:
                import traceback; traceback.print_exc()
                pass
            finished.set()

        
        def comparator(a, b):
            if (a.filetype == a.DIRECTORY and
                b.filetype != a.DIRECTORY):
                return -1
            elif (a.filetype != a.DIRECTORY and
                  b.filetype == a.DIRECTORY):
                return 1
            else:
                return cmp(a.name, b.name)

                        
        self.__list.clear_items()
        self.__list.set_frozen(True)

        self.__throbber.set_text("Retrieving Directory")
        self.__throbber.set_visible(True)
        self.__throbber.render()

        self.__items = []
        finished = threading.Event()
        entries = []
        threads.run_threaded(loader_thread, dev, path, entries, finished)
        now = time.time()
        aborted = False
        while (not finished.isSet()):
            if (time.time() - now >= 10):
                aborted = True
                break
            self.__throbber.rotate()        
        #end while
        
        self.__throbber.set_text("Processing")
        entries.sort(comparator)
        
        for entry in entries:
            if (entry.filetype == entry.DIRECTORY):
                icon = theme.filetype_folder
                info = "%d items" % entry.child_count
            else:
                icon = theme.filetype_audio
                info = entry.info
        
            item = ListItem(icon, entry.name, info)
            self.__list.append_item(item)
            self.__items.append(entry)
            
            self.__throbber.rotate()
        #end for

        self.__throbber.set_visible(False)
        self.__list.set_frozen(False)
        self.__list.render()
        
        if (aborted):
            dialogs.error("Timeout", "Connection timed out.")
        
        
    def search(self, key):
    
        idx = 0
        for item in self.__items:
            if (key in item.name.lower()):
                self.__list.scroll_to_item(idx)
                print "found", item.name, "for", key
                break
            idx += 1
        #end for        
