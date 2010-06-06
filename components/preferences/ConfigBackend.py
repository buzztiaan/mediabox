from com import Configurator, msgs
from ui.itemview import ThumbableGridView
from BackendListItem import BackendListItem
from theme import theme
import mediaplayer

import os


class ConfigBackend(Configurator):
    """
    Configurator for mapping media backends to media file types.
    """

    ICON = theme.prefs_icon_backend
    TITLE = "Media Player Backends"
    DESCRIPTION = "Choose the player backend for each media format"


    def __init__(self):
    
        Configurator.__init__(self)

        self.__list = ThumbableGridView()
        self.add(self.__list)
                  
        self.__update_list()


    def __on_item_clicked(self, item, idx):

        backends = mediaplayer.get_backends()
        backends.sort()

        mediatype = item.get_media_type()
        backend = item.get_backend()
        try:
            i = backends.index(backend)
        except:
            i = 0
        i += 1
        i %= len(backends)
        item.set_backend(backends[i])
        item.set_backend_icon(mediaplayer.get_backend_icon(backends[i]))

        self.__list.invalidate_item(idx)
        #self.__list.fx_cycle_item(idx)
        self.__list.render()
            
        mediaplayer.set_backend_for(mediatype, backends[i])
        mediaplayer.write_user_mapping()        


    def __update_list(self):
    
        mediatypes = mediaplayer.get_media_types()
        mediatypes.sort()
        idx = 0
        for mt in mediatypes:
            backend = mediaplayer.get_backend_for(mt)
            if (backend != "dummy"):
                item = BackendListItem(mt, backend)
                item.set_backend_icon(mediaplayer.get_backend_icon(backend))
                #item.set_size(w, 80)
                self.__list.append_item(item)
                item.connect_clicked(self.__on_item_clicked, item, idx)
                idx += 1
        #end for

