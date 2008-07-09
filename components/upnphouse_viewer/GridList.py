#from utils.Observable import Observable
from ui.ItemList import ItemList
#from ui.KineticScroller import KineticScroller
#from ui.DragSorter import DragSorter
from RowItem import RowItem
import theme

import time


class GridList(ItemList):

    def __init__(self, arrows, arrows_off, items_per_row = 4): #item_per_row should be at least 2. Having a gridlist of 1 item per row doesnt make sense.
        
        self.__last_rowitem = None
        self.__items_per_row = items_per_row

        self.__ignore_click_until = 0

        ItemList.__init__(self, 178, 10)
        #self.set_caps(theme.list_top, theme.list_bottom)
        self.set_bg_color(theme.color_bg)
        #self.set_scrollbar(theme.list_scrollbar)

        self.set_arrows (arrows, arrows_off)
        
        self.connect_button_released(self.__on_button_release)

    def append_button(self, grid_button):

        if ( self.__last_rowitem ):
            if (self.__last_rowitem.get_button_list().__len__() < self.__items_per_row) :
                self.__last_rowitem.append_button ( grid_button )
                return

        rowitem = RowItem ( self )
        self.append_item (rowitem)
        self.__last_rowitem = rowitem
            
        rowitem.append_button ( grid_button )
       
 
    def add_button (self, grid_button, index, position):

        item = self.get_item (index)

        if ( not item ):
            self.append_button (grid_button)
            return

        item.add_button (grid_button, position)    

        rec_index = index + 1

        while ( item.get_button_list().__len__() > self.__items_per_row ):

            removed_button, empty = item.remove_button ( self.__items_per_row )

            next_item = self.get_item (rec_index)

            if ( not next_item ):
                self.append_button (removed_button)
                return

            next_item.add_button (removed_button,0)

            item = next_item
            rec_index += 1

        #end while
    

    def remove_button (self, index, position):

        item = self.get_item(index)
        
        if ( not item ): return

        removed_button, empty = item.remove_button ( position )

        if ( not removed_button ): return

        if ( empty):
            self.remove_item ( index )
            return

        rec_index = index + 1
        next_item = self.get_item (rec_index)

        while ( next_item ):

            first_from_next_item_button, empty = next_item.remove_button ( 0 )
            item.append_button (first_from_next_item_button)

            if ( empty ):
                self.remove_item ( rec_index )
                return

            item = next_item
            rec_index += 1
            next_item = self.get_item (rec_index)

        #end while


    def __on_button_release(self, x, y):

            handled = False
            #if (time.time() > self.__ignore_click_until):
            #self.__ignore_click_until = time.time() + 0.4
            
            idx = self.get_index_at(y)
            item = self.get_item(idx)
            button = item.get_button_at(x)

            if (button) :        
                button.button_clicked ()
                handled = True
                self.render()

            else:

                xpos, ypos = self.get_screen_pos()
                w, h = self.get_size()
                arrow_up, arrow_down, nil, nil = self.get_arrows()

                if ( x > xpos + w - arrow_up.get_width() ):

                    idx = self.get_index_at (ypos) #this is the top most index in screen
                    
                    if ( y < ypos + arrow_up.get_height() and idx > 0 ):

                        if (idx == 1): idx +=1
                        self.scroll_to_item ( idx - 2 )
                        
                    elif ( y > ypos + h - arrow_down.get_height() ):

                        self.scroll_to_item ( idx + 3 )
            #endif

            #if (handled): self.__kscr.stop_scrolling()

            return handled

