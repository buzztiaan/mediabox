import theme

import gtk
import time


class Dialog(gtk.Dialog):

    def __init__(self):
    
        self.__response = None
    
        self.__entries = []    
    
        gtk.Dialog.__init__(self) #, gtk.WINDOW_POPUP)
        self.set_title(" ")
        self.set_modal(True)
        self.set_border_width(12)
        #self.set_decorated(False)
        self.set_size_request(600, -1)
        self.move(100, -1000)
        #self.set_flags(gtk.CAN_FOCUS)
        
        #self.vbox = gtk.VBox()
        #self.vbox.show()
        #self.add(self.vbox)
        
        #self.action_area = gtk.HBox()
        #self.action_area.show()
        #self.vbox.pack_end(self.action_area, False, False)
        
        btn = gtk.Button("OK")
        btn.get_children()[0].modify_font(theme.font_headline)
        btn.connect("clicked", lambda x: self.response(gtk.RESPONSE_ACCEPT))
        #btn.connect("clicked", self.__on_close)
        btn.show()
        self.action_area.pack_start(btn, True, True, 12)

        btn = gtk.Button("Cancel")
        btn.get_children()[0].modify_font(theme.font_headline)
        btn.connect("clicked", lambda x: self.response(gtk.RESPONSE_CANCEL))
        btn.show()
        self.action_area.pack_start(btn, True, True, 12)


    def response(self, response):
    
        self.__response = response
        
        
    def run(self):
    
        while (self.__response == None):
            time.sleep(0.01)
            while (gtk.events_pending()): gtk.main_iteration()
            
        return self.__response
        
        
    def __on_close(self, src):
    
        self.response(gtk.RESPONSE_ACCEPT)
        
        
    def add_entry(self, name, value = ""):
    
        hbox = gtk.HBox(spacing = 6)
        hbox.show()
    
        lbl = gtk.Label(name)
        lbl.modify_font(theme.font_headline)
        lbl.show()
        hbox.pack_start(lbl, False, False)
    
        entry = gtk.Entry()
        #entry.set_flags(gtk.CAN_FOCUS)
        entry.modify_font(theme.font_headline)
        if (value): entry.set_text(value)
        entry.show()
        hbox.pack_start(entry, True, True)
        
        self.vbox.pack_start(hbox, False, False, 6)
        
        self.__entries.append(entry)
        
        
        
    def get_values(self):
    
        values = [ e.get_text() for e in self.__entries ]
        return values
        
        
        
    def wait_for_values(self):
    
        # this has no effect on maemo, unless window positioning has been
        # enabled on the window manager, in which case this is required to
        # have the window appear on screen (easy-chroot-debian is known to
        # switch on window positioning)
        self.move(0, 0)
                
        self.show()
        #self.__slide_in()
        response = self.run()
        #self.__slide_out()
        if (response == gtk.RESPONSE_ACCEPT):
            values = self.get_values()
        else:
            values = []            
        self.destroy()
        while (gtk.events_pending()): gtk.main_iteration()
        
        return values
        
        
        
    def __slide_in(self):
    
        nil, nil, w, h = self.get_allocation()
        for y in range(-h, 0, 10):
            now = time.time()
            self.move(100, y)
            while (gtk.events_pending()): gtk.main_iteration()
            then = time.time()            
            delay = max(0, (now + 0.01) - then)
            time.sleep(delay)
            
            
    def __slide_out(self):
    
        nil, nil, w, h = self.get_allocation()
        for y in range(0, -h, -10):
            now = time.time()
            self.move(100, y)
            while (gtk.events_pending()): gtk.main_iteration()
            then = time.time()            
            delay = max(0, (now + 0.01) - then)
            time.sleep(delay)
    
