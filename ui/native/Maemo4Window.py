from GtkWindow import Window as GtkWindow
from ui.Pixmap import Pixmap
from utils.MiniXML import MiniXML
from theme import theme

import gtk
import hildon


class Window(GtkWindow):

    def __init__(self, wtype):

        GtkWindow.__init__(self, wtype)
        self._init(wtype)    


    def _init(self, wtype):

        self.__window = hildon.Window()
        self.__window.fullscreen()            

        self._set_gtk_window(self.__window)
        self._setup_gtk_events()
        self._setup_gtk_rendering()
        overlay = self._create_gtk_video_overlay()
        self.__window.add(overlay)


    def show_menu(self):
    
        if (self.__menu):
            self.__menu.show_all()
            self.__menu.run()


    def set_menu_xml(self, xml, bindings):

        def click_cb(src, cb, *args):
            self.__menu.hide()
            cb(*args)

        dom = MiniXML(xml).get_dom()        
        self.__menu = gtk.Dialog()
        self.__menu.set_title("")
        vbox = self.__menu.vbox
        
        for node in dom.get_children():
            name = node.get_name()
            if (name == "item"):
                item_id = node.get_attr("id")
                item_label = node.get_attr("label")
                callback = bindings.get(item_id)

                btn = gtk.Button(item_label)
                btn.set_size_request(300, 80)
                if (callback):
                    btn.connect("clicked",
                                click_cb, callback)
                                #lambda x, cb:cb(), callback)
                vbox.add(btn)

            elif (name == "choice"):
                choice_id = node.get_attr("id")
                choice_selected = int(node.get_attr("selected") or "0")
                callback = bindings.get(choice_id)
 
                group = None
                hbox = gtk.HBox()
                vbox.add(hbox)
                cnt = 0
                for option in node.get_children():
                    item_label = option.get_attr("label")
                    item_icon = option.get_attr("icon")
                    
                    btn = gtk.ToggleButton()
                    
                    if (callback):
                        btn.connect("clicked",
                                    click_cb, callback, cnt)
                                    #lambda x, i, cb:cb(i), cnt, callback)
                    if (item_label):
                        btn.set_label(item_label)
                    if (item_icon):
                        img = gtk.Image()
                        img.set_from_pixbuf(getattr(theme, item_icon))
                        btn.set_image(img)

                    if (cnt == choice_selected):
                        btn.set_active(True)

                    hbox.add(btn)
                    group = btn
                    cnt += 1
                #end for
            #end if
        #end for

