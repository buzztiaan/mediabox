from ui.Widget import Widget
from ui.HBox import HBox
from utils.Observable import Observable

import theme

import gtk
import pango


class ControlPanel(Widget, Observable):   

    def __init__(self):
    
        self.__known_sets = []
        self.__items = []
        self.__all_items = []
        
        self.__background = None
        
    
        Widget.__init__(self)
        self.__box = HBox()
        self.__box.set_spacing(8)
        self.__box.set_alignment(self.__box.ALIGN_RIGHT)
        self.add(self.__box)        


    def set_bg(self, bg):
    
        self.__background = bg
        self.render()


    def set_size(self, w, h):
    
        Widget.set_size(self, w, h)
        self.__box.set_size(w - 20, h)
        

    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        screen.draw_frame(theme.panel, x, y, w, h, True,
                          screen.TOP | screen.RIGHT)

 

    def set_toolbar_set(self, tbset):
        """
        Sets the given toolbar set on this panel.
        """
    
        if (tbset and not tbset in self.__known_sets):
            self.__known_sets.append(tbset)        
            for c in tbset.get_items():
                if (not c in self.__box.get_children()):
                    self.__box.add(c)
            #end for
        #end if
        
        for c in self.__items:
            c.set_visible(False)
            
        if (tbset == None):
            self.__items = []
        else:
            self.__items = tbset.get_items()
        
        for c in self.__items:
            c.set_visible(True)
        
        #print "set tbar", len(self.__items)
        #self.render()

