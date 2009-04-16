from com import msgs
from storage import Device, File
from theme import theme


class VideoDevice(Device):

    CATEGORY = Device.CATEGORY_INDEX
    TYPE = Device.TYPE_VIDEO


    def __init__(self):
    
        # table: id -> device
        self.__devices = {}
    
        Device.__init__(self)
        
        
        
    def get_prefix(self):
        
        return "videodevs://"
        
        
    def get_name(self):
    
        return "Videos"
        
        
    def get_icon(self):
    
        return theme.mb_device_n800
        
        
    def get_root(self):
    
        f = File(self)
        f.name = self.get_name()
        f.path = "/"
        f.mimetype = f.DIRECTORY
        return f


    def ls_async(self, path, cb, *args):
    
        if (path == "/"):
            self.__ls_devices(cb, *args)
    
    
    def __ls_devices(self, cb, *args):
    
        def device_comparator(a, b):
            return cmp((a.TYPE, a.CATEGORY, a.get_name()),
                       (b.TYPE, b.CATEGORY, b.get_name()))
    
        devs = self.__devices.values()
        devs.sort(device_comparator)
        for device in devs:
            f = device.get_root()
            f.mimetype = "application/x-device-folder"
            try:
                f.icon = device.get_icon().get_path()
            except:
                pass
            cb(f, *args)
        #end for
        cb(None, *args)
        
    
        
    def handle_message(self, msg, *args):
    
        if (msg == msgs.CORE_EV_DEVICE_ADDED):
            ident, device = args
            if (device != self and device.TYPE == device.TYPE_VIDEO):
                self.__devices[ident] = device

        
