from Widget import Widget
from Pixmap import Pixmap, text_extents
import theme


class SideTabs(Widget):
    """
    Widget for vertical side tabs.
    """

    def __init__(self):
    
        self.__color_bg = theme.color_bg
        self.__color_bg_selected = theme.color_bg
        self.__tabs = []
        self.__tab_callbacks = []
        self.__tab_pmaps = []
        self.__hilighted_tab = 0
    
        Widget.__init__(self)
        self.set_size(100, 100)
        self.connect_button_pressed(self.__on_click)


    def _reload(self):
    
        self.__prepare_tabs()


    def set_size(self, w, h):
    
        if ((w, h) != self.get_size()):
            need_prepare = True
        else:
            need_prepare = False
    
        Widget.set_size(self, w, h)

        if (need_prepare):
            self.__prepare_tabs()


    def render_this(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        offset = 0
        for i in range(len(self.__tabs)):
            pmap1, pmap2 = self.__tab_pmaps[i]
            if (i == self.__hilighted_tab):
                screen.draw_pixmap(pmap2, x, y + offset)
            else:
                screen.draw_pixmap(pmap1, x, y + offset)
            offset += pmap1.get_size()[1]
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
        
        
    def __prepare_tabs(self):
        """
        Prepares all tabs for rendering.
        """
    
        for i in range(len(self.__tabs)):
            self.__prepare_tab(i)
        
        
    def __prepare_tab(self, idx):
        """
        Prepares the given tab for rendering.
        """
    
        icon, text = self.__tabs[idx]
    
        h, w = self.get_size()
        
        num_of_tabs = len(self.__tabs)
        tab_width = w / num_of_tabs        

        pmap1 = Pixmap(None, tab_width, h)
        pmap2 = Pixmap(None, tab_width, h)
        
        pmap1.fill_area(0, 0, tab_width, h, self.__color_bg)
        pmap2.fill_area(0, 0, tab_width, h, self.__color_bg_selected)
        pmap2.draw_frame(theme.mb_selection_frame, 0, 0, tab_width, h, True)
                    
        if (icon):
            pmap1.draw_pixbuf(icon, 8, (h - icon.get_height()) / 2)
            pmap2.draw_pixbuf(icon, 8, (h - icon.get_height()) / 2)
        
        font = theme.font_plain
        text_w, text_h = text_extents(text, font)
        pmap1.draw_text(text, font,
                        max(0, (tab_width - text_w) / 2),
                        max(0, (h - text_h) / 2),
                        theme.color_fg_item)
        pmap2.draw_text(text, font,
                        max(0, (tab_width - text_w) / 2),
                        max(0, (h - text_h) / 2),
                        theme.color_fg_item)

        
        pmap1.rotate(270)
        pmap2.rotate(270)
        self.__tab_pmaps[idx] = (pmap1, pmap2)


    def __hilight_tab(self, idx):
        """
        Hilights the given tab.
        """
    
        #prev = self.__hilighted_tab
        self.__hilighted_tab = idx

        #self.__prepare_tab(prev)
        #self.__prepare_tab(idx)
        
        self.render()


    def select_tab(self, idx):
        """
        Selects the given tab.
        """
    
        if (idx != self.__hilighted_tab):
            self.__hilight_tab(idx)
            cb, args = self.__tab_callbacks[idx]
            try:
                cb(*args)
            except:
                pass
        #end if

