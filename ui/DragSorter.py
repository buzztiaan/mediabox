"""
Decorator for drag-sortable lists.
"""

from utils.Observable import Observable

import gobject


class DragSorter(Observable):
    """
    Decorator class for drag-sorting a list. The list must implement
    get_index_at(y), swap(index1, index2), and float_item(index, y)
    methods.
    """
    
    OBS_SWAPPED = 0
    
    
    def __init__(self, child):
    
        self.__is_enabled = True
    
        self.__child = child
        self.__is_dragging = False
        self.__drag_index = -1
        
        self.__auto_scroller = None
        self.__auto_scroll_direction = 0
        
        self.__render_handler_id = None
        self.__need_render = False
        
        # callback for working around bad touch screens
        self.__workaround_handler = None
        
        child.connect_button_pressed(self.__on_drag_start)
        child.connect_button_released(self.__on_drag_stop)
        child.connect_pointer_moved(self.__on_drag)


    def set_enabled(self, v):
    
        self.__is_enabled = v

    
    def __auto_scroll_on(self, direction):
    
        self.__auto_scroll_direction = direction
        if (not self.__auto_scroller):
            self.__auto_scroller = gobject.timeout_add(50, self.__auto_scroll)


    def __auto_scroll_off(self):
        
        if (self.__auto_scroller):
            gobject.source_remove(self.__auto_scroller)
            self.__auto_scroller = None


    def __auto_scroll(self):
    
        if (self.__auto_scroll_direction > 0):
            self.__child.move(0, 20)
        elif (self.__auto_scroll_direction < 0):
            self.__child.move(0, -20)
        self.__auto_scroller = gobject.timeout_add(20, self.__auto_scroll)
    
                

        
    def __on_drag_start(self, px, py):
    
        if (px < 40 and self.__is_enabled and not self.__is_dragging):
            self.__drag_index = self.__child.get_index_at(py)
            if (self.__drag_index >= 0):
                self.__is_dragging = True
            
                
        
    def __on_drag_stop(self, px, py):
    
        def f():
            self.__is_dragging = False
            self.__child.float_item(-1)
            self.__child.render()
            self.__auto_scroll_off()        
        
        # work around bad touch screens (e.g. Nokia 770)
        #if (self.__workaround_handler):
        #    gobject.source_remove(self.__workaround_handler)
        #self.__workaround_handler = gobject.timeout_add(0, f)
        f()

        
    def __on_drag(self, px, py):

        if (self.__is_dragging and self.__drag_index >= 0):
            idx = self.__child.get_index_at(py)
            self.__child.float_item(idx, py)
            if (idx >= 0 and idx != self.__drag_index):
                # swap
                self.update_observer(self.OBS_SWAPPED, idx, self.__drag_index)
                self.__child.swap(idx, self.__drag_index)
                self.__drag_index = idx

            if (py < 40):
                self.__auto_scroll_on(-1)
            elif (py > self.__child.get_size()[1] - 40):
                self.__auto_scroll_on(1)
            else:
                self.__auto_scroll_off()
                
            self.__child.render()

