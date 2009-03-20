from com import msgs

from storage import Device, File
from utils import logging
from theme import theme


class VideoStorage(Device):

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_VIDEO
    

    def __init__(self):
    
        self.__folders = {}
        self.__media_was_updated = False
    
        Device.__init__(self)
        
        
    def handle_message(self, msg, *args):
    
        if (msg == msgs.MEDIASCANNER_EV_SCANNING_FINISHED):
            #self.__update_media()
            self.__media_was_updated = True


    def __update_media(self):

        self.__folders = {"All Videos": []}
        media, nil, nil = self.call_service(msgs.MEDIASCANNER_SVC_GET_MEDIA,
                                            ["video/"])
        for f in media:
            parent = f.parent
            if (not parent in self.__folders):
                self.__folders[parent] = []
            self.__folders[parent].append(f)
            self.__folders["All Videos"].append(f)
        #end for
        
        self.__media_was_updated = False
          
        
    def get_prefix(self):
    
        return "library://video"
        
        
    def get_name(self):
    
        return "Local Videos"


    def get_icon(self):
    
        return theme.mb_device_video


    def get_root(self):
    
        f = File(self)
        f.is_local = True
        f.can_skip = True
        f.path = "/"
        f.mimetype = f.DIRECTORY
        f.resource = ""
        f.name = self.get_name()
        f.info = "Browse your video library"
        
        return f
          
    
    
    def ls_async(self, path, cb, *args):
    
        def folder_cmp(a, b):
            if (a == "All Videos"):
                return -1
            if (b == "All Videos"):
                return 1
            else:
                return cmp(a, b)
    
        if (self.__media_was_updated):
            self.__update_media()        
    
        if (path == "/"):
            folders = self.__folders.keys()
            folders.sort(folder_cmp)
            for folder in folders:
                f = File(self)
                f.is_local = True
                f.can_skip = True
                f.path = "/" + folder
                f.mimetype = f.DIRECTORY
                f.resource = ""
                f.name = folder
                f.info = "%d items" % len(self.__folders.get(folder, []))
                cb(f, *args)
                
        else:
            videos = self.__folders.get(path[1:], [])
            videos.sort()
            for video in videos:
                cb(video, *args)
            #end for
        
        cb(None, *args)

