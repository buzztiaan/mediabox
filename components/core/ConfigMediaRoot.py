from com import Configurator, msgs
from MediaListItem import MediaListItem
from ui.ItemList import ItemList
from ui.KineticScroller import KineticScroller
from ui.Label import Label
from ui.HBox import HBox
from ui.Button import Button
from ui.ImageButton import ImageButton
from mediabox import config
import theme

import gtk
try:
    import hildon
except:
    pass


class ConfigMediaRoot(Configurator):

    ICON = theme.prefs_folder
    TITLE = "Media Collection"
    

    def __init__(self):
       
        self.__mediaroots = config.mediaroot()
    
        Configurator.__init__(self)
    
        self.__list = ItemList(80)
        self.__list.set_caps(theme.list_top, theme.list_bottom)
        self.__list.set_bg_color(theme.color_bg)
        self.__list.set_scrollbar(theme.list_scrollbar)
        #self.__list.set_arrows(theme.arrows)
        self.__list.set_geometry(0, 0, 610, 290)
        self.add(self.__list)

        kscr = KineticScroller(self.__list)
        kscr.set_touch_area(192, 540)
        kscr.add_observer(self.__on_observe_list)

        btn_add = Button(theme.button_1, theme.button_2)
        btn_add.set_pos(10, 290)
        btn_add.set_size(300, 80)
        btn_add.connect_clicked(self.__on_add_folder)        
        self.add(btn_add)

        hbox = HBox()
        hbox.set_size(300, 80)
        btn_add.add(hbox)
        lbl = Label("Add Folder", theme.font_plain, theme.color_fg_item)
        hbox.add(lbl)


        btn_rescan = Button(theme.button_1, theme.button_2)
        btn_rescan.set_pos(310, 290)
        btn_rescan.set_size(300, 80)
        btn_rescan.connect_clicked(self.__on_rescan)        
        self.add(btn_rescan)

        hbox = HBox()
        hbox.set_size(300, 80)
        btn_rescan.add(hbox)
        lbl = Label("Refresh", theme.font_plain, theme.color_fg_item)
        hbox.add(lbl)
                
        self.__build_list()


    def __build_list(self):
    
        self.__list.clear_items()
        for mroot, mtypes in self.__mediaroots:
            item = MediaListItem(610, 80, mroot)
            item.set_mediatypes(mtypes)
            if (mroot.startswith("/media/mmc")):
                idx = self.__list.append_item(item)
            else:
                idx = self.__list.append_item(item)
            #self.__list.overlay_image(idx, theme.remove, 540, 24)


    def __on_add_folder(self):
    
        try:
            # Maemo
            dirchooser = hildon.FileChooserDialog(self.get_window(),
                               action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
            dirchooser.set_title("Choose a directory")
        except:     
            # GNOME                                    
            dirchooser = gtk.FileChooserDialog("Choose a directory",
                               action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                               buttons = ("OK", gtk.RESPONSE_OK,
                                          "Cancel", gtk.RESPONSE_CANCEL))
        dirchooser.show()
        response = dirchooser.run()
        
        if (response == gtk.RESPONSE_OK):
            dirpath = dirchooser.get_filename()       
            self.__mediaroots.append((dirpath, 7))
            config.set_mediaroot(self.__mediaroots)
            item = MediaListItem(610, 80, dirpath)
            item.set_mediatypes(7)
            if (dirpath.startswith("/media/mmc")):
                idx = self.__list.append_item(item)
            else:
                idx = self.__list.append_item(item)
            self.__list.render()
        dirchooser.destroy()            


    def __on_rescan(self):
    
        self.emit_event(msgs.CORE_ACT_SCAN_MEDIA, True)


    def __on_observe_list(self, src, cmd, *args):
    
        if (cmd == src.OBS_CLICKED):
            px, py = args
            idx = self.__list.get_index_at(py)            
            if (idx == -1): return

            uri, mtypes = self.__mediaroots[idx]
            if (px < 208):
                if (px < 82):    mtypes ^= 1
                elif (px < 146): mtypes ^= 2
                elif (px < 208): mtypes ^= 4
                item = self.__list.get_item(idx)
                item.set_mediatypes(mtypes)
                self.__mediaroots[idx] = (uri, mtypes)
                self.render()
                config.set_mediaroot(self.__mediaroots)
            
            elif (px >= 540):
                del self.__mediaroots[idx]
                self.__list.remove_item(idx)            
                self.__list.render()
                config.set_mediaroot(self.__mediaroots)

