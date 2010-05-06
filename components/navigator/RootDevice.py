from com import msgs
from storage import Device, File
from utils import logging
from theme import theme


_TYPE_MAP = {
    Device.TYPE_SYSTEM:  "/",
    Device.TYPE_GENERIC: "/storage",
    Device.TYPE_AUDIO:   "/audio",
    Device.TYPE_VIDEO:   "/video",
    Device.TYPE_IMAGE:   "/image"
}


class RootDevice(Device):
    """
    Storage device for uniting all devices in one directory list.
    """

    CATEGORY = Device.CATEGORY_INDEX
    TYPE = Device.TYPE_GENERIC


    def __init__(self):
    
        # table: id -> device
        self.__devices = {}
        
        # list of favorited files
        self.__favorites = []
        
        # table: type -> list of devices
        self.__device_lists = {
            Device.TYPE_SYSTEM:  [],
            Device.TYPE_GENERIC: [],
            Device.TYPE_AUDIO:   [],
            Device.TYPE_VIDEO:   [],
            Device.TYPE_IMAGE:   []
        }
    
        Device.__init__(self)
        
        
        
    def get_prefix(self):
        
        return "media://"
        
        
    def get_name(self):
    
        return "Shelf"
        
        
    def get_icon(self):
    
        return None
          

    def __device_comparator(self, a, b):

        return cmp((a.TYPE, a.CATEGORY, a.get_name()),
                    (b.TYPE, b.CATEGORY, b.get_name()))


    def __list_devices(self, dtype):
    
        devs = self.__device_lists[dtype]
        devs.sort(self.__device_comparator)
        
        return [ dev.get_root() for dev in devs
                 if not dev.CATEGORY == dev.CATEGORY_HIDDEN]


    def __list_categories(self):
    
        out = []
        for name, info, path, icon in [
            ("Music", "Browse Music Library", "/audio", theme.mb_folder_audio),
            ("Videos", "Browse Video Library", "/video", theme.mb_folder_video),
            ("Pictures", "Browse Picture Library", "/image", theme.mb_folder_image),
            ("Storage & Network", "Browse storage and network", "/storage", theme.mb_folder_storage),
        ]:
            f = File(self)
            f.name = name
            f.info = info
            f.path = path
            f.mimetype = f.DIRECTORY
            f.icon = icon.get_path()
            f.folder_flags = f.ITEMS_COMPACT
            out.append(f)
        #end for
        
        return out


    def __list_favorites(self):

        # get bookmarks
        self.__favorites = self.call_service(msgs.BOOKMARK_SVC_LIST, [])
        self.__favorites.sort(lambda a,b:cmp((a.device_id, a.name),
                                             (b.device_id, b.name)))
        print "shelfed items", self.__favorites
        return self.__favorites


    def get_file(self, path):

        f = None    
        if (path == "/"):
            f = File(self)
            f.name = self.get_name()
            f.path = "/"
            f.mimetype = f.DEVICE_ROOT
            f.folder_flags = f.ITEMS_COMPACT
        
        else:
            for c in self.__list_categories():
                if (c.path == path):
                    f = c
                    break
            #end fir
        #end if

        return f
        

    def get_contents(self, path, begin_at, end_at, cb, *args):

        items = []
    
        if (path.path == "/"):
            items += self.__list_categories()
            items += self.__list_devices(Device.TYPE_SYSTEM)
            items += self.__list_favorites()

        elif (path.path == "/audio"):
            items += self.__list_devices(Device.TYPE_AUDIO)

        elif (path.path == "/video"):
            items += self.__list_devices(Device.TYPE_VIDEO)

        elif (path.path == "/image"):
            items += self.__list_devices(Device.TYPE_IMAGE)

        elif (path.path == "/storage"):
            items += self.__list_devices(Device.TYPE_GENERIC)

        
        cnt = 0
        for f in items:
            if (cnt < begin_at): continue
            if (end_at > 0 and cnt > end_at): break
            
            cb(f, *args)
        #end for
        cb(None, *args)       


    def __on_add_to_playlist(self, folder, f):
    
        self.emit_message(msgs.PLAYLIST_ACT_APPEND, "", f)


    def __on_remove_from_shelf(self, folder, f):
    
        logging.debug("removing from shelf: %s", f.name)
        f.bookmarked = False
        self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, self.get_root())


    def get_file_actions(self, folder, f):
    
        options = []
        if (f in self.__favorites):
            if (not f.full_path.startswith("playlist://")):
                options.append((None, "Add to Playlist",
                                self.__on_add_to_playlist))
            options.append((None, "Remove from Shelf",
                            self.__on_remove_from_shelf))

        return options

    
    def handle_CORE_EV_DEVICE_ADDED(self, ident, device):

        if (device != self):
            self.__devices[ident] = device

            if (device.TYPE in self.__device_lists):
                self.__device_lists[device.TYPE].append(device)

            folder = self.get_file(_TYPE_MAP[device.TYPE])
            print "invalidating", folder, "due to", device
            self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, folder)
        #end if


    def handle_CORE_EV_DEVICE_REMOVED(self, ident):

        device = self.__devices.get(ident)
        if (device):
            del self.__devices[ident]

            if (device.TYPE in self.__device_lists):
                self.__device_lists[device.TYPE].remove(device)

            folder = self.get_file(_TYPE_MAP[device.TYPE])
            self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, folder)
        #end if
