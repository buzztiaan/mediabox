from com import Configurator, msgs
from ui.Label import Label
from ui.VBox import VBox
from mediabox.TrackList import TrackList
from BackendListItem import BackendListItem
from theme import theme
import mediaplayer

import os


class ConfigBackend(Configurator):

    ICON = theme.mb_viewer_audio
    TITLE = "Media Formats"
    DESCRIPTION = "Choose the player backend for each media format"


    def __init__(self):
    
        Configurator.__init__(self)

        self.__vbox = VBox()
        self.add(self.__vbox)

        self.__list = TrackList()
        self.__list.connect_button_clicked(self.__on_item_button)
        self.__vbox.add(self.__list)

        lbl = Label("Be careful when changing these settings!",
                    theme.font_mb_plain, theme.color_mb_listitem_text)
        self.__vbox.add(lbl)
                  
        self.__update_list()

        

    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        self.__vbox.set_geometry(12, 0, w - 24, h)
        self.__list.set_geometry(0, 0, w - 24, h - 32)
        screen.fill_area(x, y, w, h, theme.color_mb_background)



    def __on_item_button(self, item, idx, btn):

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

        item.invalidate()
        self.__list.fx_cycle_item(idx)
        
        #self.__list.invalidate_buffer()
        #self.__list.render()

        mediaplayer.set_backend_for(mediatype, backends[i])
        mediaplayer.write_user_mapping()        


    def __update_list(self):
    
        mediatypes = mediaplayer.get_media_types()
        mediatypes.sort()
        for mt in mediatypes:
            backend = mediaplayer.get_backend_for(mt)
            if (backend != "dummy"):
                item = BackendListItem(mt, backend)
                item.set_backend_icon(mediaplayer.get_backend_icon(backend))
                self.__list.append_item(item)
        #end for

