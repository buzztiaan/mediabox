import platforms

import gtk
import gobject


class InputDialog(gtk.Dialog):

    def __init__(self, title):
    
        self.__inputs = []
        
        # list of value retrieving functions
        self.__retrievers = []
    
        gtk.Dialog.__init__(self)
        self.set_title(title)
        
        btn = gtk.Button("OK")
        btn.connect("clicked", lambda x: self.response(gtk.RESPONSE_ACCEPT))
        btn.show()
        self.action_area.add(btn)

        self.realize()
        self.window.property_change("_HILDON_PORTRAIT_MODE_SUPPORT",
                                    "CARDINAL", 32,
                                    gtk.gdk.PROP_MODE_REPLACE,
                                    [1])


    def add_input(self, label, default):
    
        vbox = gtk.VBox()
        vbox.show()
        self.vbox.add(vbox)
        
        lbl = gtk.Label(label)
        lbl.show()
        vbox.add(lbl)
        
        entry = gtk.Entry()
        entry.show()
        vbox.add(entry)
        
        self.__retrievers.append(lambda :entry.get_text())


    def add_range(self, label, min_value, max_value, preset):

        vbox = gtk.VBox()
        vbox.show()
        self.vbox.add(vbox)

        lbl = gtk.Label(label)
        lbl.show()
        vbox.add(lbl)
    
        if (platforms.PLATFORM == platforms.MAEMO5):    
            import hildon
            scale = hildon.HScale()
        else:
            scale = gtk.HScale()

        scale.set_range(min_value, max_value)
        scale.set_value(preset)
        scale.show()
        vbox.add(scale)
        self.__retrievers.append(lambda :scale.get_value())


        
    def get_values(self):
    
        return [ r() for r in self.__retrievers ]


    def run(self):
    
        self.show()
        resp = gtk.Dialog.run(self)
        gobject.idle_add(self.destroy)
        
        if (resp == gtk.RESPONSE_ACCEPT):
            return 0
        else:
            return 1

