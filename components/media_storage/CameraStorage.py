from com import msgs
from storage import Device, File
from utils import urlquote
from utils import logging
from theme import theme

import os


_MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December"
]


class CameraStorage(Device):
    """
    Storage device for browsing camera pictures.
    """

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_IMAGE
    

    def __init__(self):
    
        Device.__init__(self)
         
        
    def get_prefix(self):
    
        return "dcim://"
        
        
    def get_name(self):
    
        return "Camera Pictures"


    def get_icon(self):
    
        return theme.mb_folder_dcim


    def __make_folder(self, month, year):

        f = File(self)
        f.is_local = True
        f.path = File.pack_path("/months", str(month), str(year))
        f.mimetype = "application/x-image-folder"
        f.resource = ""
        f.name = "%s %d" % (_MONTHS[month - 1], year)
        f.acoustic_name = "Folder: " + f.name
        f.comparable = 0 - ((year * 100) + month)
        #f.info = "%d items" % len(self.__folders.get(folder_name, []))
        f.folder_flags = f.ITEMS_ENQUEUEABLE | \
                            f.ITEMS_COMPACT

        return f



    def get_file(self, path):
    
        parts = File.unpack_path(path)
        prefix = parts[0]
            
        f = None
        if (prefix == "/"):
            f = File(self)
            f.is_local = True
            f.path = "/"
            f.mimetype = f.DEVICE_ROOT
            f.resource = ""
            f.name = self.get_name()
            f.info = "Browse your camera pictures"
            f.icon = self.get_icon().get_path()
            f.folder_flags = f.ITEMS_ENQUEUEABLE | f.ITEMS_COMPACT
            
        elif (prefix == "/months"):
            month, year = parts[1:]
            month = int(month)
            year = int(year)
            f = self.__make_folder(month, year)

        return f


    def get_contents(self, folder, begin_at, end_at, cb, *args):

        parts = File.unpack_path(folder.path)
        prefix = parts[0]
               
        items = []
        if (prefix == "/"):
            # list months
            query = "Image.Month, Image.Year of File.Type='image'"
            res = self.call_service(msgs.FILEINDEX_SVC_QUERY, query)
            #res.sort()
            
            print res
            for month, year in res:
                f = self.__make_folder(month, year)
                if (f): items.append(f)
            #end for
        
        elif (prefix == "/months"):
            month, year = parts[1:]
            month = int(month)
            year = int(year)
            query = "File.Path of and and File.Type='image' Image.Month=%d Image.Year=%d" \
                    % (month, year)
            res = self.call_service(msgs.FILEINDEX_SVC_QUERY, query)
            for path, in res:
                f = self.call_service(msgs.CORE_SVC_GET_FILE, path)
                if (f):
                    items.append(f)
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

