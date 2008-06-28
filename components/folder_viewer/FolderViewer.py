from com import Viewer, events
from DeviceThumbnail import DeviceThumbnail
from LocalDevice import LocalDevice
from ListItem import ListItem
from mediabox.TrackList import TrackList
from ui.ImageButton import ImageButton
from ui import dialogs
from mediabox.ThrobberDialog import ThrobberDialog
import mediaplayer
from utils import threads
import theme

import md5
import os
import time
import threading


class FolderViewer(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_folders
    ICON_ACTIVE = theme.viewer_folders_active
    PRIORITY = 0
    

    def __init__(self):
    
        # table of devices: id -> rootpath
        self.__devices = {"0": LocalDevice()}
        
        # the currently selected device and path stack
        self.__current_device = None
        self.__path_stack = []
        
        self.__device_items = []
        
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
        import gobject
        #gobject.idle_add(self.emit_event, events.CORE_EV_DEVICE_ADDED, 0, LocalDevice())
        
        
    def __add_device(self, ident, device):

        if (device.has_content_directory()):
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
    
        if (event == events.CORE_EV_DEVICE_ADDED):
            ident, device = args
            self.__add_device(ident, device)
            
        elif (event == events.CORE_EV_DEVICE_REMOVED):
            uuid = args[0]
            self.__remove_device(uuid)
            
        if (self.is_active()):
            if (event == events.CORE_ACT_LOAD_ITEM):
                idx = args[0]
                dev = self.__device_items[idx]
                if (dev):
                    self.__current_device = dev
                    root = dev.get_root()
                    self.__path_stack = [root]
                    self.__load(root)
                
                
    def __on_item_button(self, item, idx, button):
    
        if (button == item.BUTTON_PLAY):
            entry = self.__items[idx]
            if (entry.mimetype == entry.DIRECTORY):
                path = entry.path
                self.__path_stack.append(entry)
                self.__load(entry)
            else:
                uri = entry.resource
                player = mediaplayer.get_player_for_uri(uri)
                player.load_audio(uri)
            
    def __on_btn_back(self):
    
        if (len(self.__path_stack) > 1):
            self.__path_stack.pop()
            self.__load(self.__path_stack[-1])


    def __lookup_icon(self, entry):
    
        from mediabox import config
        import gtk
        m = md5.new(entry.path)
        path = os.path.join(config.thumbdir(), m.hexdigest() + ".jpg")
        
        if (os.path.exists(path)):
            icon = gtk.gdk.pixbuf_new_from_file(path)
        else:
            icon = None

        return icon


    def __load(self, path):
        
        def loader_thread(path, entries, finished):
            try:        
                entries += path.get_children()
            except:
                import traceback; traceback.print_exc()
                pass
            finished.set()

        
        def comparator(a, b):
            if (a.mimetype == a.DIRECTORY and
                b.mimetype != a.DIRECTORY):
                return -1
            elif (a.mimetype != a.DIRECTORY and
                  b.mimetype == a.DIRECTORY):
                return 1
            else:
                return cmp(a.name, b.name)

        self.__list.set_frozen(True)                
        self.__list.clear_items()

        self.__throbber.set_text("Retrieving Directory")
        self.__throbber.set_visible(True)
        self.__throbber.render()

        self.__items = []
        finished = threading.Event()
        entries = []
        threads.run_threaded(loader_thread, path, entries, finished)
        now = time.time()
        aborted = False
        while (not finished.isSet()):
            if (time.time() - now >= 30):
                aborted = True
                break
            self.__throbber.rotate()        
        #end while
        
        self.__throbber.set_text("Processing")
        entries.sort(comparator)
        
        for entry in entries:
            if (entry.mimetype == entry.DIRECTORY):
                icon = self.__lookup_icon(entry) or theme.filetype_folder
                info = "%d items" % entry.child_count
            else:                
                icon = self.__lookup_icon(entry) or theme.filetype_audio
                info = entry.info
        
            item = ListItem(icon, entry.name, info)
            item.set_emblem(entry.emblem)
            self.__list.append_item(item)
            self.__items.append(entry)
            
            self.__throbber.rotate()
        #end for

        self.__throbber.set_visible(False)
        self.__list.set_frozen(False)
        
        self.__list.fx_slide()
        #self.__list.render()
        
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
