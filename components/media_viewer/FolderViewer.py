from com import msgs
from GenericDevice import GenericDevice
from mediabox.MediaViewer import MediaViewer
from mediabox.TrackList import TrackList
from LibItem import LibItem
from storage import Device
from mediabox import config as mb_config
from theme import theme


class FolderViewer(MediaViewer):

    ICON = theme.mb_viewer_folder
    PRIORITY = 0

    def __init__(self):

        # whether the library has been changed
        self.__lib_is_dirty = False
        

        MediaViewer.__init__(self, GenericDevice(), "Browser", "Player")
        self.get_browser().connect_file_added_to_library(self.__on_add_to_library)

        # library list
        self.__lib_list = TrackList()
        self.__lib_list.set_visible(False)
        self.add(self.__lib_list)
        self.__lib_list.connect_button_clicked(self.__on_lib_item_button)
        self.__lib_list.connect_item_clicked(self.__on_lib_item_set_types)


        self.add_tab("Library", self.__lib_list, self.__on_tab_library)


    def __on_tab_library(self):

        if (not self.__lib_list.get_items()):
            self.__init_library()


    def __on_add_to_library(self, f):

        self.call_service(msgs.NOTIFY_SVC_SHOW_INFO,
                          u"adding \xbb%s\xab to library" % f.name)

        item = LibItem(f)
        item.set_media_types(7)
        self.__lib_list.append_item(item)
        self.__save_library()


    def __init_library(self):
        """
        Loads the library folders.
        """
        
        mediaroots = mb_config.mediaroot()
        self.__lib_list.clear_items()
        
        for mroot, mtypes in mediaroots:
            f = self.call_service(msgs.CORE_SVC_GET_FILE, mroot)
            if (f):
                item = LibItem(f)
                item.set_media_types(mtypes)
                self.__lib_list.append_item(item)
        #end for

        
    def __save_library(self):
        """
        Saves the current library folders.
        """
        
        mediaroots = []
        for item in self.__lib_list.get_items():
            uri = item.get_path()
            mtypes = item.get_media_types()
            mediaroots.append((uri, mtypes))
            mb_config.set_mediaroot(mediaroots)
        self.__lib_is_dirty = True


    def __on_lib_item_button(self, item, idx, button):
    
        if (idx == -1): return
    
        if (button == item.BUTTON_REMOVE):
            self.__lib_list.remove_item(idx)
            self.__lib_list.invalidate_buffer()
            self.__lib_list.render()
            self.__save_library()


    def __on_lib_item_set_types(self, item, idx, px, py):
    
        if (idx == -1): return

        if (px < 196):
            uri = item.get_path()
            mtypes = item.get_media_types()

            if (px < 68):    mtypes ^= 1
            elif (px < 132): mtypes ^= 2
            elif (px < 196): mtypes ^= 4
            item.set_media_types(mtypes)
            self.__lib_list.invalidate_buffer()
            self.__lib_list.render()
            self.__save_library()
        #end if


    def show(self):
    
        MediaViewer.show(self)
        
        # search for UPnP devices
        self.emit_message(msgs.SSDP_ACT_SEARCH_DEVICES)


    def hide(self):
    
        # rescan media if the library has changed
        if (self.__lib_is_dirty):
            self.emit_message(msgs.CORE_ACT_SCAN_MEDIA, False)
            self.__lib_is_dirty = False
        MediaViewer.hide(self)

