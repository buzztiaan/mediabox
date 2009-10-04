from com import msgs
from storage import Device, File
from theme import theme


class RootDevice(Device):
    """
    Device for uniting all devices in one directory list.
    """

    CATEGORY = Device.CATEGORY_INDEX
    TYPE = Device.TYPE_GENERIC


    def __init__(self):
    
        # table: id -> device
        self.__devices = {}
        
        # table: type -> list of devices
        self.__device_lists = {
            Device.TYPE_GENERIC: [],
            Device.TYPE_AUDIO:   [],
            Device.TYPE_VIDEO:   [],
            Device.TYPE_IMAGE:   []
        }
    
        Device.__init__(self)
        
        
        
    def get_prefix(self):
        
        return "media://"
        
        
    def get_name(self):
    
        return "MediaBox"
        
        
    def get_icon(self):
    
        return theme.mb_device_n800
        
        
    def get_root(self):
    
        f = File(self)
        f.name = self.get_name()
        f.path = "/"
        f.mimetype = f.DEVICE_ROOT
        f.folder_flags = f.ITEMS_COMPACT
        return f


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
            ("Music", "Browse Music Library", "/audio", theme.mb_device_audio),
            ("Videos", "Browse Video Library", "/video", theme.mb_device_video),
            ("Pictures", "Browse Picture Library", "/image", theme.mb_device_image)
        ]:
            f = File(self)
            f.name = name
            f.info = info
            f.path = path
            f.mimetype = f.DIRECTORY
            f.icon = icon.get_path()
            out.append(f)
        #end for
        
        return out


    def __list_favorites(self):

        # get bookmarks
        bookmarks = self.call_service(msgs.BOOKMARK_SVC_LIST, [])
        bookmarks.sort(lambda a,b:cmp(a.name, b.name))
        
        return bookmarks
        


    def get_contents(self, path, begin_at, end_at, cb, *args):
    
    
        items = []
    
        if (path.path == "/"):
            items += self.__list_devices(Device.TYPE_GENERIC)
            items += self.__list_categories()
            items += self.__list_favorites()

        elif (path.path == "/audio"):
            items += self.__list_devices(Device.TYPE_AUDIO)

        elif (path.path == "/video"):
            items += self.__list_devices(Device.TYPE_VIDEO)

        elif (path.path == "/image"):
            items += self.__list_devices(Device.TYPE_IMAGE)

        
        cnt = 0
        for f in items:
            if (cnt < begin_at): continue
            if (end_at > 0 and cnt > end_at): break
            
            cb(f, *args)
        #end for
        cb(None, *args)       

    
    def handle_CORE_EV_DEVICE_ADDED(self, ident, device):

        if (device != self):
            self.__devices[ident] = device

            if (device.TYPE in self.__device_lists):
                self.__device_lists[device.TYPE].append(device)
            
            self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, self.get_root())
        #end if


    def handle_CORE_EV_DEVICE_REMOVED(self, ident):

        device = self.__devices.get(ident)
        if (device):
            del self.__devices[ident]

            if (device.TYPE in self.__device_lists):
                self.__device_lists[device.TYPE].remove(device)

            self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, self.get_root())

        #end if
