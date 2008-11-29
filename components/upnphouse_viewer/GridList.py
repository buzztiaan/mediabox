#from utils.Observable import Observable
from ui.ItemList import ItemList
#from ui.ImageStrip import ImageStrip
#from ui.KineticScroller import KineticScroller
#from ui.DragSorter import DragSorter
from RowItem import RowItem
import theme

import time


def get_last (this_list):
    return this_list[ len(this_list) -1 ]


class GridList(ItemList):

    def __init__(self, arrows, arrows_off, items_per_row = 4): #item_per_row should be at least 2. Having a gridlist of 1 item per row doesnt make sense.
        
        self.__items_list = []
        self.__items_per_row = items_per_row

        #self.__ignore_click_until = 0

        self.__dialog = None
        self.__receptive = True

        ItemList.__init__(self, 178, 10)
        self.set_bg_color(theme.color_mb_background)
        
        self.set_arrows (arrows, arrows_off)
        
        self.connect_button_released(self.__on_button_release)


    def set_dialog (self, dialog):

        if (self.__dialog):
            self.remove (dialog)  #taking out the previous dialog if it was there

        self.__receptive = False
        self.__dialog = dialog
        self.add(dialog)


    def remove_dialog (self):

        if (self.__dialog):
            self.__receptive = True
            self.remove (self.__dialog)
            self.__dialog = None

    def remove_dialog_by_uuid (self, uuid):

        if (self.__dialog) and (self.__dialog.uuid == uuid):
            self.remove_dialog()


    def open_dialog (self, dialog):
    
        if ( dialog == None ):
            self.close_dialog()
        else:
            self.set_dialog (dialog)
            self.render()


    def close_dialog (self):

        self.remove_dialog ()
        self.render()


    def append_button(self, grid_button):

        if ( len (self.__items_list) > 0 ):
            last_row_item = get_last (self.__items_list)
            if ( last_row_item.get_button_list().__len__() < self.__items_per_row) :
                last_row_item.append_button ( grid_button )
                return

        rowitem = RowItem ( self )
        self.append_item (rowitem)
        self.__items_list.append (rowitem)
            
        rowitem.append_button ( grid_button )
       
 
    def add_button (self, grid_button, index, position):

        try:
            item = self.__items_list[index]
        except IndexError:
            self.append_button (grid_button)
            return

        item.add_button (grid_button, position)    

        rec_index = index + 1

        while ( item.get_button_list().__len__() > self.__items_per_row ):

            removed_button, empty = item.remove_button_from_position ( self.__items_per_row )

            try:
                next_item = self.__items_list [rec_index]
            except IndexError: #no more items in the list, have to create a new one to place the button
                self.append_button (removed_button)
                return

            next_item.add_button (removed_button,0)

            item = next_item
            rec_index += 1

        #end while
    

    def get_button_index_and_position_by_uuid (self, uuid):

        for index, rowitem in enumerate(self.__items_list) :

            position = rowitem.get_button_position_by_uuid ( uuid )

            if ( position >= 0 ) :

                return ( index, position )

        return ( -1, -1)


    def gridlist_remove_item (self, index):

        self.remove_item ( index )
        self.__items_list.pop ( index )


    def remove_button_from_postion (self, index, position):

        try:
            item = self.__items_list[index]
        except IndexError:
            return

        removed_button, empty = item.remove_button_from_position ( position )

        if ( not removed_button ): return

        if ( empty):
            self.gridlist_remove_item (index)
            return

        rec_index = index + 1
        try:
            next_item = self.__items_list [rec_index]
        except IndexError:
            next_item = None

        while ( next_item ):

            first_from_next_item_button, empty = next_item.remove_button_from_position ( 0 )
            item.append_button (first_from_next_item_button)

            if ( empty ):
                self.gridlist_remove_item ( rec_index )
                return

            item = next_item
            rec_index += 1
            try:
                next_item = self.__items_list [rec_index]
            except IndexError:
                next_item = None

        #end while

        self.render()


    def __on_button_release(self, x, y):

            if self.__receptive == False : return (True)

            handled = False
            #if (time.time() > self.__ignore_click_until):
            #self.__ignore_click_until = time.time() + 0.4
            
            idx, relative_y = self.get_index_at_and_relpos(y)
            if (idx < 0): return handled
            try :
                item = self.__items_list [idx]
            except:
                print 'DEBUG: this should not happen'
                return (True)
            button, side_button_hit = item.get_button_at(x)

            if (button) :

                if (side_button_hit) and (relative_y < 0.78) and (relative_y > 0.56) :
                    button.dialog_button_clicked()
                else:
                    button.button_clicked ()

                handled = True

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

            return handled #is this needed?

