from ui.Widget import Widget
from ui.Image import Image
from ui.Pixmap import Pixmap, TEMPORARY_PIXMAP
from ui.Label import Label
from ui.layout import HBox
from ui import pixbuftools
from theme import theme

import gobject


class TitlePanel(Widget):

    def __init__(self):

        self.__bg_pmap = None

        self.__title_text = ""
        self.__title_timer = None

        self.__volume_timer = None
    
    
        Widget.__init__(self)

        self.__status_box = HBox()
        self.__status_box.set_spacing(8)
        self.add(self.__status_box)
        

        self.__title = Label("", theme.font_mb_plain,
                             theme.color_mb_panel_text)
        self.__title.set_alignment(self.__title.CENTERED)
        #self.__title.set_geometry(0, 5, 460, 30)
        self.add(self.__title)
        
        self.__info = Label("", theme.font_mb_plain,
                            theme.color_mb_panel_text)
        self.__info.set_alignment(self.__title.RIGHT)
        #self.__info.set_geometry(500, 5, 110, 30)
        self.add(self.__info)

        self.__buffer = Pixmap(None, 32, 32)

        self.__speaker = Image(theme.mb_speaker_volume)
        #self.__speaker.set_pos(520, 4)
        self.__speaker.set_visible(False)
        self.add(self.__speaker)
        
        self.__volume = Label("", theme.font_mb_plain,
                              theme.color_mb_panel_text)
        self.__volume.set_alignment(self.__title.RIGHT)
        #self.__volume.set_geometry(560, 5, 50, 30)
        self.__volume.set_visible(False)
        self.add(self.__volume)      
        

    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        self.__status_box.set_geometry(4, 4, 170, 32)
        self.__title.set_geometry(180, 5, w - 360, 0)
        self.__speaker.set_pos(w - 110, 4)
        self.__info.set_geometry(w - 140, 5, 130, 0)
        self.__volume.set_geometry(w - 140, 5, 130, 0)
        
        if (self.__bg_pmap):
            screen.draw_pixmap(self.__bg_pmap, x, y)


    def _reload(self):
    
        self.__bg_pmap = None
        w, h = self.get_size()
        self.set_size(w, h)


    def set_size(self, w, h):

        if (not self.__bg_pmap or (w, h) != self.get_size()):
            self.__bg_pmap = Pixmap(None, w, h)
            self.__bg_pmap.fill_area(0, 0, w, h, theme.color_mb_background)
            self.__bg_pmap.draw_frame(theme.mb_panel, 0, 0, w, h, True,
                                     Pixmap.LEFT | Pixmap.BOTTOM | Pixmap.RIGHT)
    
        Widget.set_size(self, w, h)
        

    def set_title(self, title):
    
        self.__title_text = title
        self.__title.set_text(title)


    def set_title_with_timeout(self, title, timeout):
    
        def f():
            self.__title.set_text(self.__title_text)
            self.__title_timer = None
    
        if (self.__title_timer):
            gobject.source_remove(self.__title_timer)
        self.__title_timer = gobject.timeout_add(timeout, f)
        self.__title.set_text(title)
        
        
    def set_info(self, info):
    
        self.__info.set_text(info)


    def set_volume(self, volume):
    
        if (not self.may_render()): return
    
        def f():
            screen = self.get_screen()
            x, y = self.__speaker.get_screen_pos()
            w, h = self.__speaker.get_size()
            
            self.__volume_timer = None
            self.__volume.set_text("")
            self.__volume.set_visible(False)
            self.__speaker.set_visible(False)
            screen.copy_pixmap(self.__buffer, 0, 0, x, y, w, h)
            self.__info.set_visible(True)
            self.__info.render()


        screen = self.get_screen()
        x, y = self.__speaker.get_screen_pos()
        w, h = self.__speaker.get_size()

        info = self.__info.get_text()
        self.__info.set_text("")
        self.__info.set_visible(False)

        if (self.__volume_timer):
            gobject.source_remove(self.__volume_timer)
            screen.copy_pixmap(self.__buffer, 0, 0, x, y, w, h)
        else:
            self.__buffer.copy_pixmap(screen, x, y, 0, 0, w, h)

        self.__speaker.set_visible(True)
        self.__speaker.render()

        self.__info.set_text(info)
        self.__volume.set_visible(True)
        self.__volume.set_text("%d %%" % volume)
        self.__volume_timer = gobject.timeout_add(500, f)


    def set_status_icon(self, w):
    
        known_icons = self.__status_box.get_children()
        
        if (not w in known_icons):
            self.__status_box.add(w, False)
            known_icons.append(w)
            
        idx = known_icons.index(w)
        known_icons[idx].set_visible(True)
        
        self.render()
        
        
    def unset_status_icon(self, w):
    
        known_icons = self.__status_box.get_children()
        
        try:
            idx = known_icons.index(w)
            known_icons[idx].set_visible(False)
        except ValueError:
            pass

        self.render()

