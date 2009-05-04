from ui.ThumbableList import ThumbableList
from ui.KineticScroller import KineticScroller
from ui.DragSorter import DragSorter
from theme import theme

import time


class TrackList(ThumbableList):

    EVENT_BUTTON_CLICKED = "button-clicked"
    EVENT_ITEM_CLICKED = "item-clicked"
    EVENT_ITEMS_SWAPPED = "items-swapped"


    def __init__(self, with_drag_sort = False):
    
        self.__kscr = None
        self.__with_drag_sort = with_drag_sort
    
        # ignore clicks until the given time was reached
        self.__ignore_click_until = 0
        
        self.__open_item = -1
    
        ThumbableList.__init__(self, 110, 0)
        self.set_caps(theme.mb_list_top, theme.mb_list_bottom)
        self.set_bg_color(theme.color_mb_background)
        #self.set_arrows(theme.arrows)
               
        self.__kscr = KineticScroller(self)
        self.__kscr.add_observer(self.__on_observe_scroller)
        
        if (with_drag_sort):
            self.__dragsorter = DragSorter(self)
            self.__dragsorter.add_observer(self.__on_drag_sort)
            self.set_drag_sort_enabled(True)


    def __update_touch_area(self):

        if (not self.__kscr): return
        
        w, h = self.get_size()
        if (self.__with_drag_sort):
            self.__kscr.set_touch_area(80, w - 100)
        else:
            self.__kscr.set_touch_area(0, w - 100)


    def stop_scrolling(self):
    
        self.__kscr.stop_scrolling()


    def set_size(self, w, h):
    
        ThumbableList.set_size(self, w, h)
        self.__update_touch_area()

    
    def set_drag_sort_enabled(self, v):
    
        self.__dragsorter.set_enabled(v)
        self.__with_drag_sort = v
        self.__update_touch_area()


        
    def __on_drag_sort(self, src, cmd, *args):
    
        if (cmd == src.OBS_SWAPPED):
            idx1, idx2 = args
            #self.update_observer(self.OBS_SWAPPED, idx1, idx2)
            self.send_event(self.EVENT_ITEMS_SWAPPED, idx1, idx2)
        
        
    def __on_observe_scroller(self, src, cmd, *args):

        handled = False
        need_render = False
        
        if (self.__with_drag_sort):
            if (cmd == src.OBS_SCROLLING):
                self.__dragsorter.set_enabled(False)

            elif (cmd == src.OBS_STOPPED):
                if (self.__with_drag_sort):
                    self.__dragsorter.set_enabled(True)
        
        if (cmd == src.OBS_CLICKED and time.time() > self.__ignore_click_until):
            self.__ignore_click_until = time.time() + 0.4
            
            x, y = args
            
            #if (self.slider_is_active()):
            #    return
                
            idx = self.get_index_at(y)
            item = self.get_item(idx)
            button = item.get_button_at(x)

            if (self.__open_item >= 0):
                open_item = self.get_item(self.__open_item)                
                open_item.close_menu()
                self.invalidate_image(self.__open_item)
                self.__open_item = -1
                need_render = True

            if (button == item.BUTTON_MENU):
                item.open_menu()
                self.invalidate_image(idx)
                self.__open_item = idx
                need_render = True
                
            elif (button):
                self.__kscr.stop_scrolling()
                self.send_event(self.EVENT_BUTTON_CLICKED, item, idx, button)

            else:
                self.send_event(self.EVENT_ITEM_CLICKED, item, idx, x, y)
                
            if (button): handled = True
                
        #end if

        if (need_render):
            #self.invalidate_buffer()
            self.render()
        if (handled): self.__kscr.stop_scrolling()

        return handled


    def connect_button_clicked(self, cb, *args):
    
        self._connect(self.EVENT_BUTTON_CLICKED, cb, *args)
        
    def connect_item_clicked(self, cb, *args):
        
        self._connect(self.EVENT_ITEM_CLICKED, cb, *args)
        
        
    def connect_items_swapped(self, cb, *args):
    
        self._connect(self.EVENT_ITEMS_SWAPPED, cb, *args)

