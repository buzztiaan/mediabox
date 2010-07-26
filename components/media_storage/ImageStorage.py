from com import msgs
from storage import Device, File
from utils import urlquote
from utils import logging
from theme import theme

import os



class ImageStorage(Device):
    """
    Storage device for browsing image folders.
    """

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_IMAGE
    

    def __init__(self):
    
        Device.__init__(self)
         
        
    def get_prefix(self):
    
        return "images://"
        
        
    def get_name(self):
    
        return "Local Pictures"


    def get_icon(self):
    
        return theme.mb_folder_image


    def __make_folder(self, folder_name):

        f = File(self)
        f.is_local = True
        f.path = "/" + urlquote.quote(folder_name, "")
        f.mimetype = "application/x-image-folder"
        f.resource = ""
        f.name = folder_name
        f.acoustic_name = "Folder: " + f.name
        #f.info = "%d items" % len(self.__folders.get(folder_name, []))
        f.folder_flags = f.ITEMS_ENQUEUEABLE | \
                            f.ITEMS_COMPACT

        return f


    def get_file(self, path):
    
        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)
        
        f = None
        if (len_parts == 0):
            f = File(self)
            f.is_local = True
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
            if (a.name == "All Pictures"):
                return -1
            if (b.name == "All Pictures"):
                return 1
            else:
                return cmp(a.name, b.name)


        parts = [ p for p in folder.path.split("/") if p ]
        len_parts = len(parts)
               
        items = []
        if (len_parts == 0):
            # list folders
            res = self.call_service(msgs.FILEINDEX_SVC_QUERY,
                                    "File.Folder of File.Type='image'")
            res.add(("All Pictures",))
            for folder_name, in res:
                f = self.__make_folder(folder_name)
                if (f): items.append(f)
            #end for
            
        elif (len_parts == 1):
            # list images
            folder_name = urlquote.unquote(parts[0])
            if (folder_name == "All Pictures"):
                query = "File.Path of File.Type='image'"
                query_args = ()
            else:
                query = "File.Path of and File.Type='image' File.Folder='%s'"
                query_args = (folder_name,)
                
            res = self.call_service(msgs.FILEINDEX_SVC_QUERY,
                                    query, *query_args)
            for path, in res:
                f = self.call_service(msgs.CORE_SVC_GET_FILE, path)
                if (f):
                    items.append(f)
            #end if
        #end if

        items.sort(folder_cmp)
        
        cnt = -1
        for item in items:
            cnt += 1
            if (cnt < begin_at): continue
            if (end_at and cnt > end_at): break
            cb(item, *args)
        #end for
        cb(None, *args)         

