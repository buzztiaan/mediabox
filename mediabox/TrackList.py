from utils.Observable import Observable
from ui.ItemList import ItemList
from ui.KineticScroller import KineticScroller
from ui.DragSorter import DragSorter
import theme

import time


class TrackList(ItemList, Observable):

    EVENT_BUTTON_CLICKED = "button-clicked"
    EVENT_ITEM_CLICKED = "item-clicked"
    #EVENT_ITEM_SELECTED = "item-selected"

    OBS_ITEM_BUTTON = 0
    OBS_ADD_ALBUM = 0
    OBS_PLAY_TRACK = 1
    OBS_ADD_TRACK = 2
    OBS_REMOVE_TRACK = 3
    OBS_REMOVE_PRECEEDING_TRACKS = 4
    OBS_REMOVE_FOLLOWING_TRACKS = 5
    OBS_EDIT_TRACK = 6

    OBS_SWAPPED = 7
    

    def __init__(self, with_drag_sort = False, with_header = False):
    
        # ignore clicks until the given time was reached
        self.__ignore_click_until = 0
        
        self.__open_item = -1
        self.__has_header = with_header
    
        ItemList.__init__(self, 90, 20)
        self.set_caps(theme.list_top, theme.list_bottom)
        self.set_bg_color(theme.color_bg)
        #self.set_arrows(theme.arrows)
               
        self.__kscr = KineticScroller(self)
        self.__kscr.add_observer(self.__on_observe_scroller)
        
        if (with_drag_sort):
            self.__kscr.set_touch_area(80, 800)
            dragsorter = DragSorter(self)
            dragsorter.add_observer(self.__on_drag_sort)


        
    def __on_drag_sort(self, src, cmd, *args):
    
        if (cmd == src.OBS_SWAPPED):
            idx1, idx2 = args
            self.update_observer(self.OBS_SWAPPED, idx1, idx2)
        
        
    def __on_observe_scroller(self, src, cmd, *args):

        handled = False
        need_render = False
        if (cmd == src.OBS_CLICKED and time.time() > self.__ignore_click_until):
            self.__ignore_click_until = time.time() + 0.4
            
            x, y = args
            idx = self.get_index_at(y)
            item = self.get_item(idx)
            button = item.get_button_at(x)

            if (self.__open_item >= 0):
                open_item = self.get_item(self.__open_item)                
                open_item.close_menu()
                self.__open_item = -1
                need_render = True

            if (button == item.BUTTON_MENU):
                item.open_menu()
                self.__open_item = idx
                need_render = True
                
            elif (button):
                self.__kscr.stop_scrolling()
                self.send_event(self.EVENT_BUTTON_CLICKED, item, idx, button)

            else:
                self.send_event(self.EVENT_ITEM_CLICKED, item, idx, x, y)
                
            if (button): handled = True
                
        #end if

        if (need_render): self.render()
        if (handled): self.__kscr.stop_scrolling()

        return handled


    def connect_button_clicked(self, cb, *args):
    
        self._connect(self.EVENT_BUTTON_CLICKED, cb, *args)
        
    def connect_item_clicked(self, cb, *args):
        
        self._connect(self.EVENT_ITEM_CLICKED, cb, *args)
   
        
    #def connect_item_selected(self, cb, *args):
    # 
    #    self._connect(self.EVENT_ITEM_SELECTED, cb, *args)

