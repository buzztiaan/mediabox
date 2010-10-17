from ui.Widget import Widget


class _ItemSet(object):
    
    def __init__(self):
        
        self.items = []
        self.cursor = -1
        self.hilight = -1


class ItemView(Widget):
    """
    Abstract base class for item views.
    @since: 0.97
    """

    EVENT_ITEM_SHIFTED = "item-shifted"
    

    def __init__(self):
    
        # table: set_id -> set
        self.__item_sets = {}
    
        # id of the current set
        self.__current_set = self
    
        self.__items = []
        self.__cursor_pos = -1
        self.__hilighted_pos = -1
        
        # filtering function
        self.__filter_func = None
        self.__filter_cache = []
    
        Widget.__init__(self)

    
    def connect_item_shifted(self, cb, *args):
    
        self._connect(self.EVENT_ITEM_SHIFTED, cb, *args)


    def get_set_id(self):
        """
        Returns the set ID of the current set.
        
        @return: set ID
        """
        
        return self.__current_set

        
    def switch_item_set(self, set_id):
        """
        Switches the current item set. If the target set does not yet exist,
        it will be created.
        
        @param set_id: id of the target item set
        """

        old_set = self.__item_sets.get(self.__current_set, _ItemSet())
        old_set.items = self.__items[:]
        old_set.cursor = self.__cursor_pos
        old_set.hilight = self.__hilighted_pos
        self.__item_sets[self.__current_set] = old_set
        
        new_set = self.__item_sets.get(set_id, _ItemSet())
        self.__items = new_set.items[:]
        self.__cursor_pos = new_set.cursor
        self.__hilighted_pos = new_set.hilight
        
        self.__current_set = set_id
        self.__filter_cache = []


    def clear_items(self):
        """
        Clears the current set of items.
        """
    
        self.__items = []
        self.__cursor_pos = -1
        self.__hilighted_pos = -1
        self.__filter_cache = []
                
        
    def append_item(self, item):
        """
        Appends the given item to the current set.
        
        @param item: the item to append
        """
    
        self.__items.append(item)
        #self.__filter_cache = []
        
        
    def insert_item(self, item, before_position):
        """
        Inserts the given item into the the current set of items before the
        given position.
        
        @param item: the item to insert
        @param before_position: the position where to insert
        """
    
        pass
        
        
    def replace_item(self, item, position):
        """
        Replaces the item at the given position in the current set.
        
        @param item: the new item
        @param position: the position of the item to replace
        """
    
        self.__items[position] = item
        self.__filter_cache = []


    def remove_item(self, position):
        """
        Removes the item at the given position.
        
        @param position: the position of the item to remove
        """
    
        self.__items.pop(position)
        self.__filter_cache = []


    def shift_item(self, pos, amount):
        """
        Shifts the item at the given position by the given amount. This triggers
        an ITEM_SHIFTED event. The shifting amount may be positive or negative.
        
        @param pos: position of the item to shift
        @param amount: shifting amount
        """
        
        if (self.__filter_func):
            items = self.get_items()
            item = items[pos]
            other_item = items[pos + amount]

            # pos is on filtered list, find origpos
            orig_pos = self.__items.index(item)
            orig_amount = self.__items.index(other_item) - orig_pos
        else:
            orig_pos = pos
            orig_amount = amount

        item = self.__items.pop(orig_pos)
        self.__items.insert(orig_pos + orig_amount, item)

        # manipulate the cache instead of invalidating; this will perform better
        # with looooong lists
        if (self.__filter_func and self.__filter_cache):
            item = self.__filter_cache.pop(pos)
            self.__filter_cache.insert(pos + amount, item)
            
        self.emit_event(self.EVENT_ITEM_SHIFTED, orig_pos, orig_amount)


    def count_items(self):
        """
        Returns the number of items in the current set.
        
        @return: number of items
        """
        
        return len(self.get_items())
        
       
    def get_items(self):
        """
        Returns the list of items in the current set.
        
        @return: list of items
        """
    
        if (self.__filter_func):
            if (not self.__filter_cache):
                self.__filter_cache = [ item for item in self.__items
                                        if self.__filter_func(item) ]
            return self.__filter_cache
        else:
            return self.__items[:]
        
        
    def get_item(self, pos):
        """
        Returns the item at the given position in the current set.
        Returns None if the position does not exist.
        
        @param pos: position
        @return: the item at that position
        """
    
        items = self.get_items()
        if (pos < len(items)):
            return items[pos]
        else:
            return None


    def set_filter(self, filter_func = None):
        """
        Sets a filter function to filter out items.
        Filter function has signature: filter_func(item)
        @since: 2010.09.14
        
        @param filter_func: filtering function or None for no filter
        """
        
        self.__filter_func = filter_func
        self.__filter_cache = []


    def set_hilight(self, pos):
        """
        Hilights the item at the given position. Pass C{-1} to remove the
        hilight.
        
        @param pos: the position of the item to hilight
        """
    
        if (self.__hilighted_pos != -1):
            self.get_item(self.__hilighted_pos).set_hilighted(False)
            
        if (pos != -1):
            self.get_item(pos).set_hilighted(True)
            
        self.__hilighted_pos = pos
        
        
    def set_cursor(self, pos):
        """
        Moves the cursor to the given position. The cursor can only be on at
        most one item at a time. Pass C{-1} to remove the cursor.
        
        @param pos: the new cursor position
        """
    
        if (self.__cursor_pos != -1):
            self.get_item(self.__cursor_pos).set_marked(False)
            
        if (pos != -1):
            self.get_item(pos).set_marked(True)

        self.__cursor_pos = pos
        
        
    def get_cursor(self):
        """
        Returns the current cursor position.
        
        @return: cursor position
        """
    
        return self.__cursor_pos

