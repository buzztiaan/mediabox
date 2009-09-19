from com import msgs
from storage import Device, File
from utils import mimetypes
from theme import theme


class _BookmarkDevice(Device):

    CATEGORY = Device.CATEGORY_HIDDEN
    TYPE = Device.TYPE_GENERIC
    _PREFIX = ""


    def __init__(self):
    
        self.__items = []
        self.__current_folder = None

        Device.__init__(self)
        
        
        
    def get_prefix(self):
        
        return "bookmarks://" + self._PREFIX
        
        
    def get_name(self):
    
        return "Bookmarked Files"
        

    def get_icon(self):
    
        return theme.mb_device_bookmarks
        
        
    def get_root(self):
    
        f = File(self)
        f.name = self.get_name()
        f.info = self._INFO
        f.path = "/"
        f.mimetype = f.DIRECTORY
        f.folder_flags = f.ITEMS_DELETABLE | \
                         f.ITEMS_BULK_DELETABLE | \
                         f.ITEMS_ENQUEUEABLE | \
                         f.ITEMS_SKIPPABLE
        return f


    def get_file(self, path):
    
        return self.get_root()


    def delete_file(self, folder, idx):
    
        f = self.__items[idx]
        self.call_service(msgs.BOOKMARK_SVC_DELETE, f)
        


    def get_contents(self, path, begin_at, end_at, cb, *args):

        """
        if (self.TYPE == Device.TYPE_AUDIO):
            types = mimetypes.get_audio_types()
        elif (self.TYPE == Device.TYPE_VIDEO):
            types = mimetypes.get_video_types()
        elif (self.TYPE == Device.TYPE_IMAGE):
            types = mimetypes.get_image_types()
        else:
            types = mimetypes.get_audio_types() + \
                    mimetypes.get_video_types() + \
                    mimetypes.get_image_types()
        """

        bookmarks = self.call_service(msgs.BOOKMARK_SVC_LIST, [])
        bookmarks.sort(lambda a,b:cmp(a.name, b.name))
        
        self.__current_folder = path
        self.__items =[]
        for f in bookmarks:
            cb(f, *args)
            self.__items.append(f)
        cb(None, *args)


    def handle_BOOKMARK_EV_INVALIDATED(self):
    
        self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, self.__current_folder)


class GenericBookmarkDevice(_BookmarkDevice):
    TYPE = Device.TYPE_GENERIC
    _PREFIX = "generic"
    _INFO = "Browse your bookmarks"

class AudioBookmarkDevice(_BookmarkDevice):
    TYPE = Device.TYPE_AUDIO
    _PREFIX = "audio"
    _INFO = "Browse your audio bookmarks"

class VideoBookmarkDevice(_BookmarkDevice):
    TYPE = Device.TYPE_VIDEO
    _PREFIX = "video"
    _INFO = "Browse your video bookmarks"

class ImageBookmarkDevice(_BookmarkDevice):
    TYPE = Device.TYPE_IMAGE
    _PREFIX = "image"
    _INFO = "Browse your picture bookmarks"

