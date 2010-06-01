from com import msgs
from storage import Device, File
from ui.dialog import OptionDialog
from utils import mimetypes
from utils import logging
from theme import theme

import os
import commands
import gobject


# some beautifications of places (table: path -> (name, info, icon))
_BEAUTIFUL_PLACES = {
    "/media/mmc1": ("SD card", "Folder", theme.mb_folder_microsd),
    "/home/user/MyDocs": ("My Documents", "Folder", theme.mb_folder_mydocs),
    "/media/mmc1/DCIM": ("Camera Folder", "Folder", theme.mb_folder_dcim),
    "/home/user/MyDocs/DCIM": ("Camera Folder", "Folder", theme.mb_folder_dcim),
    "/home/user/MyDocs/.sounds": ("Audio Clips", "Folder", theme.mb_folder_audioclips),
    "/home/user/MyDocs/.videos": ("Video Clips", "Folder", theme.mb_folder_videoclips),
    "/home/user/MyDocs/.images": ("Pictures", "Folder", theme.mb_folder_imageclips),
}


_DOTTED_WHITELIST = [".sounds", ".videos", ".images"]


class LocalDevice(Device):
    """
    Storage device for browsing the local filesystem.
    """

    CATEGORY = Device.CATEGORY_LOCAL
    TYPE = Device.TYPE_GENERIC
    

    def __init__(self):
    
        self.__name = "Filesystem" #commands.getoutput("hostname")
        Device.__init__(self)
        
        
    def __get_child_count(self, path):
    
        try:
            files = [ f for f in os.listdir(path)
                     if not f.startswith(".") ]
        except:
            files = []

        return len(files)
        
        
    def get_prefix(self):
    
        return "file://"
        
        
    def get_name(self):
    
        return self.__name


    def get_icon(self):
    
        return theme.mb_folder_device


    def get_root(self):
    
        f = File(self)
        f.is_local = True
        f.path = "/"
        f.mimetype = f.DEVICE_ROOT
        f.resource = ""
        f.name = self.__name
        f.info = "Browse the filesystem"
        f.icon = self.get_icon().get_path()
        f.folder_flags = f.ITEMS_ENQUEUEABLE # | f.ITEMS_COMPACT

        return f
    

    def __on_add_to_playlist(self, folder, f):
    
        self.emit_message(msgs.PLAYLIST_ACT_APPEND, "", f)


    def __on_delete_file(self, folder, f):
    
        dlg = OptionDialog("Really delete this file?")
        dlg.add_option(None, "Yes, delete from device")
        dlg.add_option(None, "No, keep it")
        ret = dlg.run()
        if (ret == 0):
            choice = dlg.get_choice()
            if (choice == 0):
                try:
                    os.unlink(f.resource)
                    self.emit_message(msgs.FILEINDEX_SVC_REMOVE, f.resource)
                except:
                    pass
                self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, folder)
            #end if
        #end if


    def __on_add_to_file_index(self, folder, f):
    
        self.emit_message(msgs.FILEINDEX_ACT_SCAN_FOLDER, f.resource)


    def get_file_actions(self, folder, f):
    
        actions = Device.get_file_actions(self, folder, f)

        if (f.mimetype == f.DIRECTORY):
            actions.append((None, "Scan for Media", self.__on_add_to_file_index))
        else:
            actions.append((None, "Delete File", self.__on_delete_file))
        
        return actions

        
    def get_file(self, path):

        item = File(self)
        item.is_local = True
        item.path = path
        item.resource = path
        item.mtime = os.path.getmtime(path)
        item.parent = os.path.basename(os.path.dirname(path))
        if (os.path.isdir(item.resource)):
            item.name = os.path.basename(path)
            item.acoustic_name = item.name + ", Folder"
            item.mimetype = item.DIRECTORY
            item.info = "Folder"
            item.folder_flags = item.ITEMS_ENQUEUEABLE
            
        else:
            item.name = os.path.splitext(os.path.basename(path))[0]
            item.acoustic_name = os.path.splitext(item.name)[0]
            ext = os.path.splitext(path)[-1].lower()
            item.mimetype = mimetypes.lookup_ext(ext)
            item.info = mimetypes.mimetype_to_name(item.mimetype) + " file"
        
        if (item.resource in _BEAUTIFUL_PLACES):
            name, info, icon = _BEAUTIFUL_PLACES[item.resource]
            item.name = name
            item.info = info
            item.icon = icon.get_path()
        
        return item
    
    
    def get_contents(self, folder, begin_at, end_at, cb, *args):

        def comp(a, b):
            if (a.mimetype != b.mimetype):
                if (a.mimetype == a.DIRECTORY):
                    return -1
                elif (b.mimetype == b.DIRECTORY):
                    return 1
                else:
                    return cmp(a.name.lower(), b.name.lower())
            else:
                return cmp(a.name.lower(), b.name.lower())


        try:
            files = [ f for f in os.listdir(folder.path)
                      if not f.startswith(".") or f in _DOTTED_WHITELIST ]
        except:
            files = []
            
        items = []
        for f in files:
            try:
                item = self.get_file(os.path.join(folder.path, f))
            except:
                continue

            if (item.mimetype.startswith("audio/") or
                item.mimetype.startswith("image/") or
                item.mimetype.startswith("video/") or
                item.mimetype == item.DIRECTORY):
                items.append(item)
        #end for
        
        items.sort(comp)
        
        cnt = -1
        for item in items:
            cnt += 1
            if (cnt < begin_at): continue
            if (end_at and cnt > end_at): break
            cb(item, *args)
        #end for
        cb(None, *args)
        
        
    def load(self, f, maxlen, cb, *args):
    
        def on_data(fd, read_size, total_size):
            data = fd.read(0xffff)
            read_size[0] += len(data)
            
            try:
                cb(data, read_size[0], total_size, *args)
            except:
                fd.close()
                return False
                
            if (data and maxlen > 0 and read_size[0] >= maxlen):
                try:
                    cb("", read_size[0], total_size, *args)
                except:
                    pass
                fd.close()
                return False

            elif (not data):
                fd.close()
                return False
            
            return True
        

        fd = open(f.resource, "r")
        fd.seek(0, 2)
        total_size = fd.tell()
        fd.seek(0)
        
        gobject.timeout_add(50, on_data, fd, [0], total_size)

