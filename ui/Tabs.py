from HilightingWidget import HilightingWidget
from Pixmap import Pixmap, text_extents
import pixbuftools
from theme import theme


class Tabs(HilightingWidget):
    """
    Widget for tabs.
    """

    VERTICAL = 0
    HORIZONTAL = 1

    def __init__(self):
    
        self.__color_bg = theme.color_mb_background
        self.__color_bg_selected = theme.color_mb_background
        self.__tab_size = (0, 0)
        self.__tabs = []
        self.__tab_callbacks = []
        self.__tab_pmaps = []
        self.__current_tab = -1
        
        self.__is_prepared = False
        
        self.__orientation = self.VERTICAL
        
    
        HilightingWidget.__init__(self)
        self.set_size(100, 100)
        self.connect_button_pressed(self.__on_click)


    def _reload(self):
    
        HilightingWidget._reload(self)
    
        #self.__prepare_tabs()
        self.__is_prepared = False


    def set_orientation(self, orientation):
        """
        Sets the orientation of the tabs.
        @since: 0.97
        
        @param orientation: one of L{VERTICAL} or L{HORIZONTAL}
        """
    
        if (orientation != self.__orientation):
            self.__orientation = orientation
            self.__is_prepared = False


    def set_size(self, w, h):

        if ((w, h) != self.get_size()):
            need_prepare = True
        else:
            need_prepare = False

        HilightingWidget.set_size(self, w, h)


    def render_this(self):

        if (not self.__is_prepared):
            self.__prepare_tabs()

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        offset = 0
        for i in range(len(self.__tabs)):
            pmap = self.__tab_pmaps[i]
            if (self.__orientation == self.VERTICAL):
                screen.draw_pixmap(pmap, x, y + offset)
                offset += pmap.get_size()[1]
            else:
                screen.draw_pixmap(pmap, x + offset, y)
                offset += pmap.get_size()[0]
        #end for


    def __on_click(self, px, py):
        
        num_of_tabs = len(self.__tabs)

        if (self.__orientation == self.VERTICAL):
            h, w = self.get_size()
            tab_width = w / num_of_tabs
            idx = int(py / tab_width)
        else:
            w, h = self.get_size()
            tab_width = w / num_of_tabs
            idx = int(px / tab_width)

        self.select_tab(idx)
        
        
    def add_tab(self, icon, title, cb, *args):
        """
        Adds the given tab with icon and title. The callback is invoked whenever
        that tab gets selected.
        
        @param icon: icon pixbuf on the tab (currently unused)
        @param title: title text on the tab
        @param cb: callback handler to invoke when selecting the tab
        @param args: variable list of arguments to the callback handler
        """
    
        self.__tabs.append((icon, title))
        self.__tab_callbacks.append((cb, args))
        self.__tab_pmaps.append(None)
        
        self.__is_prepared = False
        #self.__prepare_tabs()
        #self.select_tab(0)
        
        
    def __prepare_tabs(self):
        """
        Prepares all tabs for rendering.
        """
    
        if (self.__orientation == self.VERTICAL):
            parts = pixbuftools.LEFT | pixbuftools.BOTTOM | pixbuftools.TOP
        else:
            parts = pixbuftools.LEFT | pixbuftools.BOTTOM | pixbuftools.RIGHT
            
        for i in range(len(self.__tabs)):
            self.__prepare_tab(i)

        if (self.__tab_pmaps):
            w, h = self.__tab_pmaps[0].get_size()
            self.__tab_size = (w, h)
            self.set_hilighting_box(
                  pixbuftools.make_frame(theme.mb_selection_frame, w, h, True,
                                         parts))
        
            if (self.__orientation == self.VERTICAL):
                self.place_hilighting_box(0, self.__current_tab * h)
            else:
                self.place_hilighting_box(self.__current_tab * w, 0)
        #end if

        self.__is_prepared = True


    def __prepare_tab(self, idx):
        """
        Prepares the given tab for rendering.
        """
    
        icon, text = self.__tabs[idx]
    
        if (self.__orientation == self.VERTICAL):
            h, w = self.get_size()
        else:
            w, h = self.get_size()
        
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
        
        # rotate pixmap for vertical layout
        if (self.__orientation == self.VERTICAL):
            pmap.rotate(270)

        self.__tab_pmaps[idx] = pmap


    def select_tab(self, idx):
        """
        Selects the given tab.
        """
    
        if (idx != self.__current_tab):
            tab_w, tab_h = self.__tab_size
            cb, args = self.__tab_callbacks[idx]
            if (self.__orientation == self.VERTICAL):
                self.move_hilighting_box(0, idx * tab_h)
            else:
                self.move_hilighting_box(idx * tab_w, 0)
            try:
                cb(*args)
            except:
                pass
            self.__current_tab = idx
        #end if


    def switch_tab(self):
        """
        Switches tabs.
        @since: 0.96.5
        """
        
        idx = self.__current_tab + 1
        if (idx == len(self.__tabs)):
            idx = 0
        self.select_tab(idx)

