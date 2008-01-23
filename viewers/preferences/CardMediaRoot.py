from PrefsCard import PrefsCard
from ui.Item import Item
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
        self.__list.set_graphics(theme.item, theme.item_active)        
        self.__list.set_font(theme.font_plain)
        self.__list.set_arrows(theme.arrows)
        self.__list.set_pos(10, 0)
        self.__list.set_size(600, 270)
        self.add(self.__list)

        kscr = KineticScroller(self.__list)
        kscr.add_observer(self.__on_observe_list)

        btn = Button(esens, theme.button_1,
                            theme.button_2)
        btn.set_pos(10, 270)
        btn.set_size(600, 80)
        btn.connect(btn.EVENT_BUTTON_RELEASE, self.__on_add_folder)        
        self.add(btn)
        
        hbox = HBox(esens)
        btn.add(hbox)                
        
        lbl = Label(esens, "Add Folder", theme.font_plain, theme.color_fg_item)
        hbox.add(lbl)
        
        self.__build_list()
        
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x + 10, y + 280, 600, 70, "#dddddd")
        

        
    def __build_list(self):
    
        self.__list.clear_items()
        for mroot in self.__mediaroots:
            if (mroot.startswith("/media/mmc")):
                idx = self.__list.append_item(mroot)
            else:
                idx = self.__list.append_item(mroot)
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
            self.__mediaroots.append(dirpath)
            config.set_mediaroot(self.__mediaroots)
            if (dirpath.startswith("/media/mmc")):
                idx = self.__list.append_item(dirpath)
            else:
                idx = self.__list.append_item(dirpath)
            self.__list.overlay_image(idx, theme.remove, 540, 24)

        dirchooser.destroy()            


    def __on_observe_list(self, src, cmd, *args):
    
        if (cmd == src.OBS_CLICKED):
            px, py = args
            idx = self.__list.get_index_at(py)
            
            if (px >= 540 and idx >= 0):
                del self.__mediaroots[idx]
                config.set_mediaroot(self.__mediaroots)
                self.__list.remove_item(idx)
            
