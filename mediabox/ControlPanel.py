from Panel import Panel
from ui.ImageButton import ImageButton
from ui.ProgressBar import ProgressBar
import panel_actions
import theme
import caps

import gtk
import pango


class ControlPanel(Panel):   

    def __init__(self):
    
        Panel.__init__(self)                

        self.__btn_play = self._create_button(theme.btn_play_1,        
                                              theme.btn_play_2,
                     lambda x,y:self.update_observer(panel_actions.PLAY_PAUSE))

        self.__btn_pause = self._create_button(theme.btn_pause_1,        
                                               theme.btn_pause_2,
                     lambda x,y:self.update_observer(panel_actions.PLAY_PAUSE))
        
        self.__btn_record = self._create_button(theme.btn_record_1,        
                                                theme.btn_record_2,
                     lambda x,y:self.update_observer(panel_actions.PLAY_PAUSE))
        
        ebox = gtk.Layout()
        ebox.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.BUTTON_RELEASE_MASK)        
        ebox.set_size_request(560, 80)
        ebox.connect("button-release-event", self.__on_set_position)                
        ebox.show()
        
        bg = gtk.Image()
        bg.set_from_pixbuf(theme.panel_bg)
        bg.show()
        ebox.put(bg, 0, 0)
        
        vbox = gtk.VBox()
        vbox.set_size_request(560, 80)
        vbox.show()
        ebox.put(vbox, 0, 0)
        self.box.pack_start(ebox, False, False, 6)

        hbox = gtk.HBox()
        hbox.show()
        vbox.pack_start(hbox, False, False, 8)
        
        self.__title = gtk.Label("")
        self.__title.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        self.__title.set_alignment(0.0, 0.0)
        self.__title.modify_font(theme.font_plain)
        self.__title.modify_fg(gtk.STATE_NORMAL, theme.panel_foreground)
        self.__title.show()
        hbox.pack_start(self.__title, True, True)

        self.__time = gtk.Label("11:24")
        self.__time.modify_font(theme.font_plain)
        self.__time.modify_fg(gtk.STATE_NORMAL, theme.panel_foreground)
        self.__time.show()
        hbox.pack_start(self.__time, False, False)
                
        self.__progress = ProgressBar()
        self.__progress.show()
        vbox.pack_start(self.__progress, True, True, 8)


    def __on_set_position(self, src, ev):
    
        w, h = src.window.get_size()
        x, y = src.get_pointer()
        pos = max(0, min(99.9, x / float(w) * 100))
        self.update_observer(panel_actions.SET_POSITION, pos)                     
                
        
    def set_capabilities(self, capabilities):
    
        if (capabilities & caps.PLAYING):
            self.__btn_play.show()
            self.__btn_pause.hide()
        else:
            self.__btn_play.hide()
            self.__btn_pause.hide()

        if (capabilities & caps.POSITIONING or capabilities & caps.TUNING):
            self.__progress.show()
            self.__time.show()
        else:
            self.__progress.hide()
            self.__time.hide()
            
        if (capabilities & caps.RECORDING):
            self.__btn_record.show()
        else:
            self.__btn_record.hide()


    def set_playing(self, value):
    
        if (value):
            self.__btn_play.hide()
            self.__btn_pause.show()
        else:
            self.__btn_pause.hide()
            self.__btn_play.show()


    def set_title(self, title):

        self.__title.set_text(title)


    def set_position(self, pos, total):
    
        self.__progress.set_position(pos, total)
        pos_m = pos / 60
        pos_s = pos % 60
        total_m = total / 60
        total_s = total % 60
        self.__time.set_text("%d:%02d / %d:%02d" % 
                             (pos_m, pos_s, total_m, total_s))            
            

