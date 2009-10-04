from com import Configurator, msgs
from ui.itemview import ThumbableGridView
from LibItem import LibItem
from mediabox import config
from utils import logging
from theme import theme


class Library(Configurator):

    ICON = theme.mb_device_folders
    TITLE = "Media Library"
    DESCRIPTION = "Configure your media library"
    

    def __init__(self):
    
        Configurator.__init__(self)
        
        self.__list = ThumbableGridView()
        self.add(self.__list)
        
        self.__update_list()
        
        
    def __update_list(self):
    
        self.__list.clear_items()
        for mediaroot, mtypes in config.mediaroot():
            item = LibItem(mediaroot, mtypes)
            self.__list.append_item(item)
        #end for
        
        
    def render_this(self):
    
        w, h = self.get_size()
        self.__list.set_geometry(0, 0, w, h)


    def handle_LIBRARY_ACT_ADD_MEDIAROOT(self, f):
    
        mediaroots = config.mediaroot()
        mediaroots.append((f.full_path, config.MEDIA_VIDEO |
                                        config.MEDIA_AUDIO |
                                        config.MEDIA_IMAGE))
        config.set_mediaroot(mediaroots)
        self.__update_list()
        logging.info("added '%s' to library", f.full_path)

