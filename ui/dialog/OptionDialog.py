import gtk


class OptionDialog(gtk.Dialog):

    def __init__(self, title):
    
        self.__num_of_options = 0
        self.__choice = -1
    
        gtk.Dialog.__init__(self)
        self.set_title(title)
        

    def add_option(self, icon, label):
    
        def on_choice(src, i):
            self.__choice = i
            self.response(gtk.RESPONSE_ACCEPT)
    
        hbox = gtk.HBox()
        hbox.show()
        if (icon):
            img = gtk.Image()
            img.set_from_pixbuf(icon)
            img.show()
            hbox.add(img)
        #end if
        lbl = gtk.Label(label)
        lbl.show()
        hbox.add(lbl)

        btn = gtk.Button()
        btn.set_size_request(-1, 70)
        self.vbox.add(btn)
        btn.show()
        btn.add(hbox)
        btn.connect("clicked", on_choice, self.__num_of_options)
        self.__num_of_options += 1


    def get_choice(self):
    
        return self.__choice


    def run(self):
    
        self.show()
        resp = gtk.Dialog.run(self)
        self.destroy()
        
        if (resp == gtk.RESPONSE_ACCEPT):
            return 0
        else:
            return 1

