from PrefsCard import PrefsCard
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


class CardMediaRoot(PrefsCard):

    def __init__(self, esens, title):
    
        self.__toplevel = esens.get_toplevel()
    
        self.__mediaroots = config.mediaroot()
    
        PrefsCard.__init__(self, esens, title)          
    
        self.__list = ItemList(esens, 600, 80)
        self.__list.set_background(theme.background.subpixbuf(185, 32, 600, 350))
        self.__list.set_arrows(theme.arrows)
        self.__list.set_pos(10, 0)
        self.__list.set_size(600, 270)
        self.add(self.__list)

        kscr = KineticScroller(self.__list)
        kscr.set_touch_area(192, 540)
        kscr.add_observer(self.__on_observe_list)

        btn_add = Button(esens, theme.button_1, theme.button_2)
        btn_add.set_pos(10, 270)
        btn_add.set_size(300, 80)
        btn_add.connect(btn_add.EVENT_BUTTON_RELEASE, self.__on_add_folder)        
        self.add(btn_add)

        hbox = HBox(esens)
        btn_add.add(hbox)
        lbl = Label(esens, "Add Folder", theme.font_plain, theme.color_fg_item)
        hbox.add(lbl)


        btn_rescan = Button(esens, theme.button_1, theme.button_2)
        btn_rescan.set_pos(310, 270)
        btn_rescan.set_size(300, 80)
        btn_rescan.connect(btn_rescan.EVENT_BUTTON_RELEASE, self.__on_rescan)        
        self.add(btn_rescan)

        hbox = HBox(esens)
        btn_rescan.add(hbox)
        lbl = Label(esens, "Refresh", theme.font_plain, theme.color_fg_item)
        hbox.add(lbl)
                
        self.__build_list()
        
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x + 10, y + 280, 600, 70, "#dddddd")
        

        
    def __build_list(self):
    
        self.__list.clear_items()
        for mroot, mtypes in self.__mediaroots:
            item = MediaListItem(600, 80, mroot)
            item.set_mediatypes(mtypes)
            if (mroot.startswith("/media/mmc")):
                idx = self.__list.append_custom_item(item)
            else:
                idx = self.__list.append_custom_item(item)
            self.__list.overlay_image(idx, theme.remove, 540, 24)


    def __on_add_folder(self, x, y):
    
        try:
            # Maemo
            dirchooser = hildon.FileChooserDialog(self.__toplevel,
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
            item = MediaListItem(600, 80, dirpath)
            item.set_mediatypes(7)
            if (dirpath.startswith("/media/mmc")):
                idx = self.__list.append_custom_item(item)
            else:
                idx = self.__list.append_custom_item(item)

        dirchooser.destroy()            


    def __on_rescan(self, src, cmd, *args):
    
        self.update_observer(self.OBS_SCAN_MEDIA)


    def __on_observe_list(self, src, cmd, *args):
    
        if (cmd == src.OBS_CLICKED):
            px, py = args
            idx = self.__list.get_index_at(py)            
            if (idx == -1): return

            uri, mtypes = self.__mediaroots[idx]
            if (px < 192):
                if (px < 64):    mtypes ^= 1
                elif (px < 128): mtypes ^= 2
                elif (px < 192): mtypes ^= 4
                item = self.__list.get_item(idx)
                item.set_mediatypes(mtypes)
                self.__mediaroots[idx] = (uri, mtypes)
            
            elif (px >= 540):
                del self.__mediaroots[idx]
                self.__list.remove_item(idx)
            
            self.__list.render()
            config.set_mediaroot(self.__mediaroots)

