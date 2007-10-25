from utils.Observable import Observable
from ui.ProgressBar import ProgressBar
from ui.ImageButton import ImageButton
import theme
import caps

import gtk
import gobject
import pango


class ControlBar(gtk.Fixed, Observable):

    OBS_PLAY_PAUSE = 0
    OBS_PREVIOUS = 1
    OBS_NEXT = 2
    
    OBS_SET_POSITION = 3
    
    OBS_TAB_SELECTED = 4    
    

    def __init__(self):
    
        self.__panels = []
        self.__current_panel = 0
    
        self.__bg = theme.panel
        self.__active_tab_bg = theme.active_tab
        self.__active_tab = None
    
        gtk.Fixed.__init__(self)
        self.set_app_paintable(True)        
        self.set_size_request(800, 80)
        self._bgpbuf = self.__bg
        
        bg = gtk.Image()
        bg.set_from_pixbuf(self.__bg)
        bg.show()
        self.put(bg, 0, 0)
       
       
        # message panel
        self.__message_panel = gtk.HBox()
        self.__message_panel.set_size_request(800, 80)
        self.put(self.__message_panel, 0, 0)
        
        self.__message_label = gtk.Label("")
        self.__message_label.modify_font(theme.font_plain)
        self.__message_label.modify_fg(gtk.STATE_NORMAL, theme.panel_foreground)
        self.__message_label.show()
        self.__message_panel.add(self.__message_label)

        # volume panel
        self.__volume_panel = gtk.Fixed()
        self.__volume_panel.set_size_request(800, 80)
        self.put(self.__volume_panel, 0, 0)
        
        self.__volume = gtk.Image()
        self.__volume.set_from_pixbuf(theme.speaker_volume)
        self.__volume.show()
        self.__volume_panel.put(self.__volume, 40, 8)
                       
                
        # panel I
        panel = gtk.HBox()
        panel.set_size_request(800, 80)
        panel.show()
        self.__panels.append(panel)
        self.put(panel, 0, 0)
                                
        btn = ImageButton(theme.btn_turn_1, theme.btn_turn_2, theme.panel)
        btn.set_size_request(80, -1)
        btn.connect("button-release-event", lambda x,y:self.next_panel())
        btn.show()
        panel.pack_start(btn, False, False)

        spacing = gtk.HBox()
        spacing._bgpbuf = self.__bg
        spacing.show()
        panel.pack_start(spacing, True, True)

        # section tabs
        self.__tabbox = gtk.HBox(spacing = 12)
        self.__tabbox.show()
        panel.pack_start(self.__tabbox, False, False)


        # panel II
        panel = gtk.HBox()
        panel.set_size_request(800, 80)
        panel.show()
        self.__panels.append(panel)
        self.put(panel, 800, 0)

        btn = ImageButton(theme.btn_turn_1, theme.btn_turn_2, theme.panel)
        btn.set_size_request(80, -1)
        btn.connect("button-release-event", lambda x,y:self.next_panel())
        btn.show()
        panel.pack_start(btn, False, False)

        btn = ImageButton(theme.btn_play_1, theme.btn_play_2, theme.panel)        
        btn.set_size_request(80, -1)
        btn.connect("button-release-event",
                    lambda x,y:self.update_observer(self.OBS_PLAY_PAUSE))
        #btn.show()
        panel.pack_start(btn, False, False)
        self.__btn_play = btn

        btn = ImageButton(theme.btn_record_1, theme.btn_record_2, theme.panel)        
        btn.set_size_request(80, -1)
        #btn.connect("button-release-event",
        #            lambda x,y:self.update_observer(self.OBS_PLAY_PAUSE))
        #btn.show()
        panel.pack_start(btn, False, False)
        self.__btn_record = btn


        vbox = gtk.VBox()
        vbox.show()
        panel.pack_start(vbox, True, True, 6)

        hbox = gtk.HBox()
        hbox.show()
        vbox.pack_start(hbox, False, False, 8)
        
        self.__title = gtk.Label("")        
        self.__title.modify_font(theme.font_plain)
        self.__title.modify_fg(gtk.STATE_NORMAL, theme.panel_foreground)
        self.__title.show()
        hbox.pack_start(self.__title, False, False)

        spacing = gtk.HBox()
        spacing.show()        
        hbox.pack_start(spacing, True, True)

        self.__time = gtk.Label("11:24")
        self.__time.modify_font(theme.font_plain)
        self.__time.modify_fg(gtk.STATE_NORMAL, theme.panel_foreground)
        self.__time.show()
        hbox.pack_start(self.__time, False, False)
                
        self.__progress = ProgressBar()
        self.__progress.set_size_request(250, -1)
        self.__progress.connect("button-release-event", self.__on_set_position)
        self.__progress.show()
        vbox.pack_start(self.__progress, True, True, 8)
        
        #btn = ImageButton("gfx/thumbnail.png", "gfx/btn-play-2.png")
        #btn.set_size_request(80, -1)
        #btn.show()
        #panel.pack_start(btn, False, False)

        
        

    def __on_expose(self, src, ev):
           
        area = ev.area
        src.window.draw_pixbuf(src.window.new_gc(),
                               src._bgpbuf,
                               area.x, area.y, area.x, area.y,
                               area.width, area.height)


    def __on_set_position(self, src, ev):
    
        w, h = src.window.get_size()
        x, y = src.get_pointer()
        pos = max(0, min(99.9, x / float(w) * 100))
        self.update_observer(self.OBS_SET_POSITION, pos)


    def __on_select_tab(self, src, ev, name):
    
        if (self.__active_tab):
            self.__active_tab._bgpbuf = self.__bg
            self.__active_tab.queue_draw()
            
        src._bgpbuf = self.__active_tab_bg
        src.queue_draw()
        self.__active_tab = src
        
        self.update_observer(self.OBS_TAB_SELECTED, name)
        

    def __create_tab(self, icon, name):
        
        tab = gtk.EventBox()
        tab.set_app_paintable(True)
        tab.set_size_request(80, -1)
        tab._bgpbuf = self.__bg
        tab.connect("expose-event", self.__on_expose)
        tab.connect("button-press-event", self.__on_select_tab, name)
        
        img = gtk.Image()
        img.set_from_pixbuf(icon)
        img.show()
        tab.add(img)
        
        return tab


    def set_capabilities(self, capabilities):
    
        if (capabilities & caps.PLAYING):
            self.__btn_play.show()
        else:
            self.__btn_play.hide()

        if (capabilities & caps.POSITIONING):
            self.__progress.show()
            self.__time.show()
        else:
            self.__progress.hide()
            self.__time.hide()
            
        if (capabilities & caps.RECORDING):
            self.__btn_record.show()
        else:
            self.__btn_record.hide()        
            


    def next_panel(self):
    
        panel1 = self.__panels[self.__current_panel]
        idx = (self.__current_panel + 1) % len(self.__panels)
        panel2 = self.__panels[idx]
        self.move(panel2, 0, 0)
        panel1.hide()
        panel2.show()
        self.__current_panel = idx


    def add_tab(self, icon, name):
    
        tab = self.__create_tab(icon, name)
        tab.show()
        self.__tabbox.pack_start(tab, False, False)        
        
        
    def set_position(self, pos, total):
    
        self.__progress.set_position(pos, total)
        pos_m = pos / 60
        pos_s = pos % 60
        total_m = total / 60
        total_s = total % 60
        self.__time.set_text("%d:%02d / %d:%02d" % 
                             (pos_m, pos_s, total_m, total_s))


    def set_title(self, title):
    
        self.__title.set_text(title)


    def set_volume(self, percent):
    
        width = 64 + int(700 * (percent / 100.0))
        self.__volume.set_from_pixbuf(theme.speaker_volume.subpixbuf(0, 0, width, 64))
        self.__panels[self.__current_panel].hide()
        self.__volume_panel.show()
        
        def f():
            self.__volume_panel.hide()
            self.__panels[self.__current_panel].show()
        gobject.timeout_add(500, f)
            


    def show_message(self, message):
    
        self.__message_label.set_text(message)
        self.__panels[self.__current_panel].hide()
        self.__message_panel.show()
        
        
    def show_panel(self):
    
        self.__message_panel.hide()
        self.__panels[self.__current_panel].show()
        
