from HilightingWidget import HilightingWidget
from Pixmap import Pixmap, text_extents
import pixbuftools
import theme


class SideTabs(HilightingWidget):
    """
    Widget for vertical side tabs.
    """

    def __init__(self):
    
        self.__color_bg = theme.color_mb_background
        self.__color_bg_selected = theme.color_mb_background
        self.__tab_size = (0, 0)
        self.__tabs = []
        self.__tab_callbacks = []
        self.__tab_pmaps = []
    
        HilightingWidget.__init__(self)
        self.set_size(100, 100)
        self.connect_button_pressed(self.__on_click)


    def _reload(self):
    
        HilightingWidget._reload(self)
    
        self.__prepare_tabs()


    def set_size(self, w, h):

        if ((w, h) != self.get_size()):
            need_prepare = True
        else:
            need_prepare = False

        HilightingWidget.set_size(self, w, h)

        if (need_prepare):
            self.__prepare_tabs()


    def render_this(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        offset = 0
        for i in range(len(self.__tabs)):
            pmap = self.__tab_pmaps[i]
            screen.draw_pixmap(pmap, x, y + offset)
            offset += pmap.get_size()[1]
        #end for

        
    def __on_click(self, px, py):
        
        h, w = self.get_size()
        num_of_tabs = len(self.__tabs)
        tab_width = w / num_of_tabs
        
        idx = int(py / tab_width)
        self.select_tab(idx)
        
        
    def add_tab(self, icon, title, cb, *args):
        """
        Adds the given tab with icon and title. The callback is invoked whenever
        that tab gets selected.
        """
    
        self.__tabs.append((icon, title))
        self.__tab_callbacks.append((cb, args))
        self.__tab_pmaps.append(None)
        
        self.__prepare_tabs()
        self.select_tab(0)
        
        
    def __prepare_tabs(self):
        """
        Prepares all tabs for rendering.
        """
    
        for i in range(len(self.__tabs)):
            self.__prepare_tab(i)
            
        if (self.__tab_pmaps):
            w, h = self.__tab_pmaps[0].get_size()
            self.__tab_size = (w, h)
            self.set_hilighting_box(
                  pixbuftools.make_frame(theme.mb_selection_frame, w, h, True))
        #end if


    def __prepare_tab(self, idx):
        """
        Prepares the given tab for rendering.
        """
    
        icon, text = self.__tabs[idx]
    
        h, w = self.get_size()
        
        num_of_tabs = len(self.__tabs)
        tab_width = w / num_of_tabs        

        pmap = Pixmap(None, tab_width, h)
        
        pmap.fill_area(0, 0, tab_width, h, self.__color_bg)
                    
        if (icon):
            pmap.draw_pixbuf(icon, 8, (h - icon.get_height()) / 2)
        
        font = theme.font_mb_plain
        text_w, text_h = text_extents(text, font)
        pmap.draw_text(text, font,
                       max(0, (tab_width - text_w) / 2),
                       max(0, (h - text_h) / 2),
                       theme.color_mb_listitem_text)
        
        pmap.rotate(270)
        self.__tab_pmaps[idx] = pmap


    def select_tab(self, idx):
        """
        Selects the given tab.
        """
    
        tab_w, tab_h = self.__tab_size
        cb, args = self.__tab_callbacks[idx]
        self.move_hilighting_box(0, idx * tab_h, cb, *args)

