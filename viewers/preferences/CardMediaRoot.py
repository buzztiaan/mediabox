from PrefsCard import PrefsCard
from ui.Item import Item
from ui.ItemList import ItemList
from ui.KineticScroller import KineticScroller
from mediabox import config
import theme

import gtk
try:
    import hildon
except:
    pass


class CardMediaRoot(PrefsCard):

    def __init__(self, title):
    
        self.__mediaroots = config.mediaroot()
    
        PrefsCard.__init__(self, title)
    
        #box = gtk.HBox()
        #box.show()
        #self.pack_start(box, True, True)                
    
        self.__list = ItemList(600, 80)
        self.__list.set_background(theme.background.subpixbuf(185, 32, 600, 368))
        self.__list.set_arrows(theme.arrows)
        self.__list.set_wrap_around(False)
        self.__list.show()
        
        box = gtk.HBox()
        box.show()
        self.pack_start(box, True, True)
        
        kscr = KineticScroller(self.__list)
        kscr.add_observer(self.__on_observe_list)
        kscr.show()
        box.pack_start(kscr, True, True, 12)

        hbox = gtk.HBox()
        hbox.show()
        icon = gtk.Image()
        icon.set_from_pixbuf(theme.prefs_folder)
        icon.show()
        hbox.pack_start(icon, False, False, 12)
        lbl = gtk.Label("Add Folder")
        lbl.modify_font(theme.font_plain)
        lbl.show()
        hbox.pack_start(lbl, False, False, 12)

        btn = gtk.Button()
        btn.add(hbox)
        btn.connect("clicked", self.__on_add_folder)
        btn.show()
        self.pack_start(btn, False, False, 12)
        
        self.__build_list()
        
        
    def __build_list(self):
    
        self.__list.clear_items()
        for mroot in self.__mediaroots:
            idx = self.__list.append_item(mroot, theme.mmc, theme.item)
            self.__list.overlay_image(idx, theme.remove, 540, 16)
                    
        
    def __on_add_folder(self, src):
    
        try:
            # Maemo
            dirchooser = hildon.FileChooserDialog(self.get_toplevel(),
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
            idx = self.__list.append_item(dirpath, theme.mmc, theme.item)
            self.__list.overlay_image(idx, theme.remove, 540, 16)            

        dirchooser.destroy()            


    def __on_observe_list(self, src, cmd, *args):
    
        if (cmd == src.OBS_CLICKED):
            px, py = args
            idx = self.__list.get_index_at(py)
            
            if (px >= 540 and idx >= 0):
                del self.__mediaroots[idx]
                config.set_mediaroot(self.__mediaroots)
                self.__list.remove_item(idx)
            
