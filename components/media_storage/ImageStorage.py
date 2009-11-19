from com import msgs
from storage import Device, File
from utils import urlquote
from utils import logging
from theme import theme

import os



class ImageStorage(Device):

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_IMAGE
    

    def __init__(self):
    
        # table: folder -> [list of names]
        self.__folders = {}
        
        self.__media_was_updated = False
    
        Device.__init__(self)
        
        
    def handle_MEDIASCANNER_EV_SCANNING_FINISHED(self):
    
        self.__media_was_updated = True


    def __update_media(self):

        self.__folders = {"All Pictures": []}
        media, nil, removed = self.call_service(msgs.MEDIASCANNER_SVC_GET_MEDIA,
                                                ["image/"])
        #print "removed", removed
        for f in media:
            parent = f.parent
            if (not parent in self.__folders):
                self.__folders[parent] = []
            self.__folders[parent].append(f)
            self.__folders["All Pictures"].append(f)        
        #end for
        
        self.__media_was_updated = False
          
        
    def get_prefix(self):
    
        return "images://"
        
        
    def get_name(self):
    
        return "Local Pictures"


    def get_icon(self):
    
        return theme.mb_device_image


    def __make_folder(self, folder_name):

        f = File(self)
        f.is_local = True
        f.path = "/" + urlquote.quote(folder_name, "")
        f.can_skip = True
        f.mimetype = "application/x-image-folder"
        f.resource = ""
        f.name = folder_name
        f.acoustic_name = "Folder: " + f.name
        f.info = "%d items" % len(self.__folders.get(folder_name, []))
        f.folder_flags = f.ITEMS_ENQUEUEABLE | \
                            f.ITEMS_SKIPPABLE | \
                            f.ITEMS_COMPACT

        return f


    def get_file(self, path):
    
        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)
        
        f = None
        if (len_parts == 0):
            f = File(self)
            f.is_local = True
            f.can_skip = True
            f.path = "/"
            f.mimetype = f.DEVICE_ROOT
            f.resource = ""
            f.name = self.get_name()
            f.info = "Browse your picture library"
            f.icon = self.get_icon().get_path()
            f.folder_flags = f.ITEMS_ENQUEUEABLE | f.ITEMS_COMPACT
            
        elif (len_parts == 1):
            folder_name = urlquote.unquote(parts[0])
            f = self.__make_folder(folder_name)

        return f


    def get_contents(self, folder, begin_at, end_at, cb, *args):

        def folder_cmp(a, b):
            if (a == "All Pictures"):
                return -1
            if (b == "All Pictures"):
                return 1
            else:
                return cmp(a, b)


        if (self.__media_was_updated):
            self.__update_media()

        parts = [ p for p in folder.path.split("/") if p ]
        len_parts = len(parts)
               
        items = []
        if (len_parts == 0):
            # list folders
            folders = self.__folders.keys()
            folders.sort(folder_cmp)
            for folder_name in folders:
                f = self.__make_folder(folder_name)
                if (f): items.append(f)
            #end for
            
        elif (len_parts == 1):
            # list images
            folder_name = urlquote.unquote(parts[0])
            images = self.__folders.get(folder_name, [])
            images.sort()
            for img in images:
                items.append(img)
            #end for
        #end if
            
        items.sort()
        
        cnt = -1
        for item in items:
            cnt += 1
            if (cnt < begin_at): continue
            if (end_at and cnt > end_at): break
            cb(item, *args)
        #end for
        cb(None, *args)
            
            
    def __find_image_in_folder(self, folder):
    
        imgs = self.__folders.get(folder)
        imgs.sort()
        if (imgs):
            return imgs[0].resource
        else:
            return ""
            


    def __get_name(self, uri):
    
        basename = os.path.basename(uri)
        name = os.path.splitext(basename)[0]
        name = name.replace("_", " ")
        
        return name
