from com import msgs
from storage import Device, File
from ui.dialog import OptionDialog
from utils import mimetypes
from utils import logging
from theme import theme

import os
import commands


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


    def __on_delete_file(self, folder, *files):
    
        if (len(files) == 1):
            dlg = OptionDialog("Really delete this entry?")
            dlg.add_option(None, "Yes, delete from device")
            dlg.add_option(None, "No, keep it")
        else:
            dlg = OptionDialog("Really delete %d entries?" % len(files))
            dlg.add_option(None, "Yes, delete from device")
            dlg.add_option(None, "No, keep them")
        
        ret = dlg.run()
        if (ret == 0):
            choice = dlg.get_choice()
            if (choice == 0):
                fail_cnt = 0
                for f in files:
                    try:
                        if (f.mimetype == f.DIRECTORY):
                            os.rmdir(f.resource)
                        else:
                            os.unlink(f.resource)
                        self.emit_message(msgs.FILEINDEX_SVC_REMOVE, f.resource)
                    except:
                        fail_cnt += 1
                #end for
                self.emit_message(msgs.CORE_EV_FOLDER_INVALIDATED, folder)
                if (fail_cnt > 0):
                    self.emit_message(msgs.UI_ACT_SHOW_INFO,
                                      "Could not remove %d entries" % fail_cnt)
            #end if
        #end if


    def __on_add_to_file_index(self, folder, f):
    
        self.emit_message(msgs.FILEINDEX_ACT_SCAN_FOLDER, f.resource)


    def get_file_actions(self, folder, f):
    
        actions = Device.get_file_actions(self, folder, f)

        if (f.mimetype == f.DIRECTORY):
            actions.append((None, "Scan for Media", self.__on_add_to_file_index))

        actions.append((None, "Delete", self.__on_delete_file))
        
        return actions


    def get_bulk_actions(self, folder):
    
        actions = Device.get_bulk_actions(self, folder)
        actions.append((None, "Delete", self.__on_delete_file))
        
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
            item.mimetype = mimetypes.ext_to_mimetype(ext)
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

