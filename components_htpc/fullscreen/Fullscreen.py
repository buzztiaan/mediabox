from com import Widget, msgs

import gtk


class Fullscreen(Widget):

    def __init__(self):
    
        Widget.__init__(self)
        
        

    def handle_message(self, msg, *args):
    
        if (msg == msgs.COM_EV_APP_STARTED):
            win = self.get_window()
            #win.set_decorated(False)
            win.get_gtk_window().fullscreen()

            pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, 8, 8)
            pbuf.fill(0x00000000)
            csr = gtk.gdk.Cursor(gtk.gdk.display_get_default(), pbuf, 0, 0)
            win.get_gtk_window().window.set_cursor(csr)
            
            self.emit_message(msgs.INPUT_EV_FULLSCREEN)

