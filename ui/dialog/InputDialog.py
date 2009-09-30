import gtk


class InputDialog(gtk.Dialog):

    def __init__(self, title):
    
        self.__inputs = []
    
        gtk.Dialog.__init__(self)
        self.set_title(title)
        
        btn = gtk.Button("OK")
        btn.connect("clicked", lambda x: self.response(gtk.RESPONSE_ACCEPT))
        btn.show()
        self.action_area.add(btn)


    def add_input(self, label, default):
    
        hbox = gtk.HBox()
        hbox.show()
        self.vbox.add(hbox)
        
        lbl = gtk.Label(label)
        lbl.show()
        hbox.add(lbl)
        
        entry = gtk.Entry()
        entry.show()
        hbox.add(entry)
        
        self.__inputs.append(entry)
        
        
    def get_values(self):
    
        return [ i.get_text() for i in self.__inputs ]


    def run(self):
    
        self.show()
        resp = gtk.Dialog.run(self)
        self.destroy()
        
        if (resp == gtk.RESPONSE_ACCEPT):
            return 0
        else:
            return 1

