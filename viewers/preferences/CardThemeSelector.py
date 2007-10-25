from PrefsCard import PrefsCard
from ui.Item import Item
from ui.ImageStrip import ImageStrip
from ui.KineticScroller import KineticScroller
from mediabox import config
import theme

import gtk


class CardThemeSelector(PrefsCard):

    def __init__(self, title):
    
        self.__mediaroots = config.mediaroot()
    
        PrefsCard.__init__(self, title)
    
        self.__strip = ImageStrip(600, 300, 80, 0)
        self.__strip.set_background(theme.background.subpixbuf(185, 0, 600, 400))
        self.__strip.set_wrap_around(False)
        self.__strip.show()        
        
        kscr = KineticScroller(self.__strip)
        kscr.add_observer(self.__on_observe_list)
        kscr.show()
        self.pack_start(kscr, True, True, 12)

        btn = gtk.Button("Add Folder")
        btn.connect("clicked", self.__on_add_folder)
        btn.show()
        self.pack_start(btn, False, False)
        
        self.__update_list()
        
        
    def __update_list(self):
    
        items = []
        for t, preview in theme.list_themes():
            item = Item(self, 600, 100, preview, t, "theme/default/item.png")
            items.append(item)
        #items = [ Item(self, 600, 80, "gfx/thumbnail.png", i, "gfx/item.png")
        #          for i in theme.list_themes() ]
        self.__strip.set_images(items)
        
        
    def __on_add_folder(self, src):
    
        dirchooser = gtk.FileChooserDialog("Choose a directory",
                               action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                               buttons = ("OK", gtk.RESPONSE_ACCEPT,
                                          "Cancel", gtk.RESPONSE_CANCEL))
        dirchooser.show()
        response = dirchooser.run()
        
        if (response == gtk.RESPONSE_ACCEPT):
            dirpath = dirchooser.get_filename()       
            self.__mediaroots.append(dirpath)
            config.set_mediaroot(self.__mediaroots)
            self.__update_list()

        dirchooser.destroy()            


    def __on_observe_list(self, src, cmd, *args):
    
        if (cmd == src.OBS_CLICKED):
            px, py = args
            idx = self.__strip.get_index_at(py)
            
            if (px > 400 and idx >= 0):
                del self.__mediaroots[idx]
                config.set_mediaroot(self.__mediaroots)
            
                self.__update_list()
            
