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

        if (wtype == self.TYPE_TOPLEVEL):
            self.__window = hildon.Window()
            self.__window.fullscreen()            
        else:
            self.__window = gtk.Window(gtk.WINDOW_POPUP)
            self.__window.set_decorated(False)
            self.__window.set_default_size(800, 240)
            self.__window.move(0, 480 - 240)
            self.__window.set_modal(True)

        self._set_gtk_window(self.__window)
        self._setup_gtk_events()
        self._setup_gtk_rendering()
        overlay = self._create_gtk_video_overlay()
        self.__window.add(overlay)


    def show_menu(self):
    
        if (self.__menu):
            self.__menu.show_all()


    def set_menu_xml(self, xml, bindings):

        def click_cb(src, cb, *args):
            self.__menu.hide()
            cb(*args)

        def click_choice_cb(src, choice_buttons, cb, *args):
            print choice_buttons
            #for c in choice_buttons:
            #    if (c != src):
            #        c.set_active(False)
            self.__menu.hide()
            cb(*args)

        def dismiss(src):
            print "DISMISS"
            #self.__menu.destroy()

        dom = MiniXML(xml).get_dom()        
        if (self.__menu):
            self.__menu.destroy()
        self.__menu = gtk.Window(gtk.WINDOW_POPUP)
        self.__menu.set_flags(gtk.CAN_FOCUS)
        self.__menu.set_default_size(600, 300)
        self.__menu.move((800 - 600) / 2, 0)
        self.__menu.set_border_width(3)
        self.__menu.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#000000"))
        self.__menu.connect("focus-out-event", dismiss)
        vbox = gtk.VBox(spacing = 3)
        self.__menu.add(vbox)
        
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
                
                choice_buttons = []
                for option in node.get_children():
                    item_label = option.get_attr("label")
                    item_icon = option.get_attr("icon")
                    
                    btn = gtk.RadioButton()
                    choice_buttons.append(btn)
                    
                    if (callback):
                        btn.connect("clicked",
                                    click_choice_cb, choice_buttons, callback, cnt)
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

