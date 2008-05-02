from utils.Observable import Observable
from ui.ItemList import ItemList
from ui.KineticScroller import KineticScroller
from ui.DragSorter import DragSorter
import theme

import time


class TrackList(ItemList, Observable):

    OBS_ITEM_BUTTON = 0
    OBS_ADD_ALBUM = 0
    OBS_PLAY_TRACK = 1
    OBS_ADD_TRACK = 2
    OBS_REMOVE_TRACK = 3
    OBS_REMOVE_PRECEEDING_TRACKS = 4
    OBS_REMOVE_FOLLOWING_TRACKS = 5
    OBS_EDIT_TRACK = 6

    OBS_SWAPPED = 7
    

    def __init__(self, esens, with_drag_sort = False, with_header = False):
    
        # ignore clicks until the given time was reached
        self.__ignore_click_until = 0
        
        self.__open_item = -1
        self.__has_header = with_header
    
        ItemList.__init__(self, esens, 80)
        self.set_caps(theme.list_top, theme.list_bottom)
        self.set_bg_color(theme.color_bg)
        self.set_scrollbar(theme.list_scrollbar)
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

            if (button == "menu"):
                item.open_menu()
                self.__open_item = idx
                handled = True
                need_render = True
                
            elif (button == "add"):
                if (idx == 0):
                    self.update_observer(self.OBS_ADD_ALBUM)
                else:
                    if (self.__has_header):
                        self.update_observer(self.OBS_ADD_TRACK, idx - 1)
                    else:
                        self.update_observer(self.OBS_ADD_TRACK, idx)
                handled = True
                    
            elif (button == "play"):
                if (self.__has_header):            
                    self.update_observer(self.OBS_PLAY_TRACK, idx - 1)
                else:
                    self.update_observer(self.OBS_PLAY_TRACK, idx)
                handled = True

            elif (button == "remove"):
                if (self.__has_header):            
                    self.update_observer(self.OBS_REMOVE_TRACK, idx - 1)
                else:
                    self.update_observer(self.OBS_REMOVE_TRACK, idx)
                handled = True
                
            elif (button == "remove-preceeding"):
                self.update_observer(self.OBS_REMOVE_PRECEEDING_TRACKS, idx)
                handled = True
                
            elif (button == "remove-following"):
                self.update_observer(self.OBS_REMOVE_FOLLOWING_TRACKS, idx)
                handled = True

            #end if
        #end if

        if (need_render): self.render()
        if (handled): self.__kscr.stop_scrolling()

        return handled

