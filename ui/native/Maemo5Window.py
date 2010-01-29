from GtkWindow import Window as GtkWindow
from ui.Pixmap import Pixmap
from utils.MiniXML import MiniXML
from theme import theme

import gtk
import hildon


class Window(GtkWindow):

    def __init__(self, wtype):
    
        self.__wtype = wtype
    
        GtkWindow.__init__(self, wtype)
        self._init(wtype)
    
    
    def _init(self, wtype):
    
        if (wtype == self.TYPE_TOPLEVEL):
            self.__window = hildon.StackableWindow()
            
        elif (wtype == self.TYPE_DIALOG):
            self.__window = gtk.Dialog()
                
        self._set_gtk_window(self.__window)
        self._setup_gtk_events()
        self._setup_gtk_rendering()
        overlay = self._create_gtk_video_overlay()
        if (wtype == self.TYPE_TOPLEVEL):
            self.__window.add(overlay)
        else:
            self.__window.vbox.add(overlay)

        self.__window.realize()
        self.__set_portrait_property("_HILDON_PORTRAIT_MODE_SUPPORT", 1)

        # we need to notify Maemo5 that we want to use the volume keys
        self.__window.window.property_change("_HILDON_ZOOM_KEY_ATOM",
                                             "XA_INTEGER", 32,
                                             gtk.gdk.PROP_MODE_REPLACE,
                                             [1])


    def set_visible(self, v):
    
        if (v and self.__wtype == self.TYPE_DIALOG):
            self.__window.resize(gtk.gdk.screen_width(),
                                 gtk.gdk.screen_height() - 120)

        GtkWindow.set_visible(self, v)


    def __set_portrait_property(self, prop, value):

        self.__window.window.property_change(prop, "CARDINAL", 32,
                                             gtk.gdk.PROP_MODE_REPLACE,
                                             [value])


    def set_portrait_mode(self, v):
        
        if (v):
            self.__set_portrait_property("_HILDON_PORTRAIT_MODE_SUPPORT", 1)
            self.__set_portrait_property("_HILDON_PORTRAIT_MODE_REQUEST", 1)
        else:
            self.__set_portrait_property("_HILDON_PORTRAIT_MODE_SUPPORT", 1)
            self.__set_portrait_property("_HILDON_PORTRAIT_MODE_REQUEST", 0)


    def set_busy(self, value):
        
        hildon.hildon_gtk_window_set_progress_indicator(self.__window,
                                                        value and 1 or 0) 


    def set_menu_xml(self, xml, bindings):
    
        dom = MiniXML(xml).get_dom()        
        menu = hildon.AppMenu()
        
        for node in dom.get_children():
            name = node.get_name()
            if (name == "item"):
                item_id = node.get_attr("id")
                item_label = node.get_attr("label")
                callback = bindings.get(item_id)

                btn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
                btn.set_label(item_label)
                if (callback):
                    btn.connect("clicked",
                                lambda x, cb:cb(), callback)
                menu.append(btn)

            elif (name == "choice"):
                choice_id = node.get_attr("id")
                choice_selected = int(node.get_attr("selected") or "0")
                callback = bindings.get(choice_id)
 
                group = None
                cnt = 0
                for option in node.get_children():
                    item_label = option.get_attr("label")
                    item_icon = option.get_attr("icon")
                    
                    btn = hildon.GtkRadioButton(gtk.HILDON_SIZE_AUTO, group)
                    btn.set_mode(False)
                    
                    if (callback):
                        btn.connect("clicked",
                                    lambda x, i, cb:cb(i), cnt, callback)
                    if (item_label):
                        btn.set_label(item_label)
                    if (item_icon):
                        img = gtk.Image()
                        img.set_from_pixbuf(getattr(theme, item_icon))
                        btn.set_image(img)

                    if (cnt == choice_selected):
                        btn.set_active(True)

                    menu.add_filter(btn)
                    group = btn
                    cnt += 1
                #end for
            #end if
        #end for

        menu.show_all()            
        self.__window.set_app_menu(menu)

