from ui.Widget import Widget
from ui.RadioButtons import RadioButtons
from ui.layout import HBox
from ui.Pixmap import Pixmap
from theme import theme

import gtk
import pango


class ControlPanel(Widget):

    def __init__(self):
    
        self.__bg_pmap = None
        self.__item_sets = []
    

        Widget.__init__(self)
        self.__box = HBox()
        self.__box.set_spacing(0)
        self.__box.set_halign(self.__box.HALIGN_LEFT)
        self.__box.set_valign(self.__box.VALIGN_CENTER)
        self.add(self.__box)
        
        self.__radio_buttons = RadioButtons()
        self.__box.add(self.__radio_buttons, False)


    def _reload(self):
    
        self.__bg_pmap = None
        w, h = self.get_size()
        self.set_size(w, h)


    def set_size(self, w, h):

        if (not self.__bg_pmap or (w, h) != self.get_size()):
            self.__bg_pmap = Pixmap(None, w, h)
            self.__bg_pmap.fill_area(0, 0, w, h, theme.color_mb_background)
            self.__bg_pmap.draw_frame(theme.mb_panel, 0, 0, w, h, True,
                                      Pixmap.LEFT | Pixmap.TOP | Pixmap.RIGHT)
    
            self.__box.set_size(w - 20, h)

        Widget.set_size(self, w, h)
        

        

    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        if (self.__bg_pmap):
            screen.draw_pixmap(self.__bg_pmap, x, y)
        #screen.draw_pixbuf(theme.mb_btn_turn, x + 10, y + 4)
 
 
    def __on_select(self, idx):
    
        self.__show_item_set(idx)
        
        
    def __show_item_set(self, idx):
    
        print "SHOW SET", idx
        i = 0
        for s in self.__item_sets:
            for c in s:
                if (idx == i):
                    c.set_visible(True)
                else:
                    c.set_visible(False)
            #end for
            i += 1
        #end for
        
        self.render()
        
 

    def set_toolbar(self, tbset):
        """
        Sets the given toolbar on this panel.
        """

        for c in self.__box.get_children():
            self.__box.remove(c)
        
        for c in tbset:
            self.__box.add(c, False)
            c.set_visible(True)

        self.render()
        
        
    def set_toolbar_sets(self, sets):
        """
        Sets the given toolbar sets on this panel.
        """    
        
        self.__radio_buttons.clear()
        
        for s in self.__item_sets:
            for c in s:
                self.__box.remove(c)
            #end for
        #end for
        self.__item_sets = []
        
        idx = 0
        for icon, items in sets:
            if (icon):
                self.__radio_buttons.append(icon, self.__on_select, idx)
                
            for c in items:
                self.__box.add(c)
            #end for
            
            self.__item_sets.append(items)
            idx += 1
        #end for
        
        self.__show_item_set(0)
