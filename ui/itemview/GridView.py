from ItemView import ItemView
from ui.Pixmap import Pixmap, TEMPORARY_PIXMAP
from theme import theme

import math


class GridView(ItemView):

    def __init__(self):
    
        # offscreen buffer
        self.__buffer = None
        
        # background buffer
        self.__background = None
        
        # color of the background
        self.__bg_color = theme.color_mb_background
        
        # offset value of the currently visible area
        self.__offset = 0
        
        # offset values of the different sets
        # table: set_id -> offset
        self.__offsets =  {}
        
        # the currently floating item
        self.__floating_item = -1
        
        # position of the floating item on screen
        self.__floating_position = (0, 0)
        
        # list of overlay renderers
        self.__overlay_renderers = []
        
        # items per row
        self.__items_per_row = 1
        
        
        self.__is_invalidated = True
    
        ItemView.__init__(self)


    def set_size(self, w, h):
    
        old_w, old_h = self.get_size()
        ItemView.set_size(self, w, h)
        if ((old_w, old_h) != (w, h)):
            self.__init_buffer()
            self.set_items_per_row(self.__items_per_row)

    def append_item(self, item):
    
        ItemView.append_item(self, item)
        
        w, h = self.get_size()
        item_w = w / self.__items_per_row
        nil, item_h = item.get_size()
        item.set_size(item_w, item_h)


    def set_items_per_row(self, n):
        """
        Sets the number of items per row.
        
        @param n: number of columns
        """
        
        self.__items_per_row = max(1, n)
        
        if (self.get_items()):
            w, h = self.get_size()
            item_w = w / self.__items_per_row
            nil, item_h = self.get_item(0).get_size()
            for i in self.get_items():
                i.set_size(item_w, item_h)
            #end for
        #end if


    def get_items_per_row(self):
    
        return self.__items_per_row



    def set_background(self, color):
        """
        Sets the background color of the view.
        
        @param color: background color
        """
        
        self.__bg_color = color
        
        if (self.__background):
            w, h = self.__background.get_size()
            self.__background.fill_area(0, 0, w, h, color)
            self.invalidate()


    def _reload(self):

        self.__bg_color.reload()
        self.set_background(self.__bg_color)
        self.invalidate()
        for item in self.get_items():
            item._invalidate_cached_pixmap()


    def invalidate(self):
        """
        Invalidates this view. This causes the view to be redrawn completely
        redrawn the next time it gets rendered.
        """
        
        self.__is_invalidated = True


    def invalidate_item(self, idx):
        """
        Invalidates the given item. This causes the item to be redrawn the next
        time the view gets rendered.
        
        @param idx: index number of the item to invalidate
        """
        
        self.__render_item(idx)
    


    def switch_item_set(self, set_id):
    
        prev_set_id = self.get_set_id()
        self.__offsets[prev_set_id] = self.__offset
        
        ItemView.switch_item_set(self, set_id)
        #item_x, item_y = self.get_position_of_item(self.get_cursor())
        self.__offset = self.__offsets.get(set_id, 0)


    def get_items_per_row(self):
        """
        Returns the number of items per row.
        """

        #return self.__items_per_row

        items = self.get_items()
        if (items):
            w, h = self.get_size()
            item = items[0]
            item_w, item_h = item.get_size()
            if (item_w > 0):
                return max(1, (w / item_w))
            else:
                return 1
        else:
            return 1


    def get_total_size(self):
        """
        Returns the total size of this view.
        
        @return: tuple of (width, height)
        """
        
        items = self.get_items()
        if (items):
            item_w, item_h = items[0].get_size()
            per_row = self.get_items_per_row()
            total_w = per_row * item_w
            total_h = int(math.ceil(self.count_items() / float(per_row))) * item_h
            
        else:
            total_w = 0
            total_h = 0
            
        return (total_w, total_h)


    def __init_buffer(self):
        """
        Initializes the offscreen buffer.
        """

        w, h = self.get_size()
        
        self.__background = Pixmap(None, w, h)
        self.__background.clear_translucent()
        self.set_background(self.__bg_color)
        
        self.__buffer = Pixmap(None, w, h)
        self.invalidate()

        for i in range(len(self.get_items())):
            self.__render_item(i)



    def get_item_at(self, x, y):
        """
        Returns the index number of the item at the given position.
        """
    
        w, h = self.get_size()
        self.__offset = max(0, min(self.__offset, self.get_total_size()[1] - h))
        y += self.__offset
        items = self.get_items()
        if (items):
            item_w, item_h = items[0].get_size()
            items_per_row = self.get_items_per_row()
            idx = (y / item_h) * items_per_row + (x / item_w)
            return idx
            
        else:
            return -1


    def get_position_of_item(self, idx):

        items = self.get_items()
        if (items):
            item_w, item_h = items[0].get_size()
            items_per_row = self.get_items_per_row()
            item_x = (idx % items_per_row) * item_w
            item_y = (idx / items_per_row) * item_h
            return (item_x, item_y)

        else:
            return (0, 0)
        

    def __render_item(self, idx):
        """
        Renders the given item.
        """
        
        w, h = self.get_size()
        item = self.get_item(idx)
        item_w, item_h = item.get_size()
        items_per_row = self.get_items_per_row()
        
        item_x = (idx % items_per_row) * item_w
        item_y = (idx / items_per_row) * item_h - self.__offset
        
        # render item if it's visible
        if (item_y + item_h >= 0 and item_y < h):
            self.__render_background(item_x, item_y, item_w, item_h)

            # render only if not floating
            if (idx != self.__floating_item):
                item.render_at(self.__buffer, item_x, item_y)
            else:
                self.__buffer.fill_area(item_x, item_y, item_w, item_h,
                                        "#66666620")
        #end if
        
        
    def __render_floating_item(self):
        """
        Renders the floating item, if any.
        """
    
        if (self.__floating_item != -1):
            item = self.get_item(self.__floating_item)
            x, y = self.__floating_position
            item.render_at(self.__buffer, x, y)


    def __render(self, begin, end):
    
        items = self.get_items()
        
        if (items):
            w, h = self.get_size()
            item_w, item_h = items[0].get_size()
            lines = list(range(begin, end, item_h)) + [end]
            items_to_render = []
            
            for y in lines:
                for x in range(0, w - item_w + 1, item_w):
                    idx = self.get_item_at(x, y)
                    if (idx < len(items) and not idx in items_to_render):
                        items_to_render.append(idx)
                #end for
            #end for
            
            for idx in items_to_render:
                self.__render_item(idx)
        #end if


    def __render_background(self, x, y, w, h):
    
        if (self.__buffer and self.__background):
            self.__buffer.copy_buffer(self.__background, x, y, x, y, w, h)


    def render_this(self):

        if (not self.__buffer): return

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        # render background and items
        if (self.__is_invalidated):
            self.__is_invalidated = False
            self.__render_background(0, 0, w, h)
            self.__render(0, h)

        TEMPORARY_PIXMAP.copy_buffer(self.__buffer, 0, 0, 0, 0, w, h)

        # render floating item
        self.__render_floating_item()

        # render overlays
        for renderer in self.__overlay_renderers:
            renderer(self.__buffer)

        screen.copy_buffer(self.__buffer, 0, 0, x, y, w, h)
        self.__buffer.copy_buffer(TEMPORARY_PIXMAP, 0, 0, 0, 0, w, h)


    def add_overlay_renderer(self, renderer):
    
        self.__overlay_renderers.append(renderer)


    def get_offset(self):
    
        return self.__offset
        

    def move(self, dx, dy):
    
        if (not self.__buffer): return (dx, dy)
    
        w, h = self.get_size()
        total_w, total_h = self.get_total_size()
        total_h = max(h, total_h)
    
        if (self.__offset + dy < 0):
            dy = 0 - self.__offset
            
        elif (self.__offset + dy > total_h - h):
            dy = (total_h - h) - self.__offset
    
        self.__offset += dy          

        abs_dy = abs(dy)
        if (dy < 0):
            self.__buffer.move_area(0, 0, w, h - abs_dy, 0, abs_dy)
            self.__render_background(0, 0, w, abs_dy)
            self.__render(0, abs_dy)

        elif (dy > 0):
            self.__buffer.move_area(0, abs_dy, w, h - abs_dy, 0, -dy)
            self.__render_background(0, h - abs_dy, w, abs_dy)
            self.__render(h - abs_dy, h)

        self.render()
        
        return (dx, dy)
        
        
    def scroll_to_item(self, pos):
    
        # get position of icon
        items = self.get_items()
        if (items):
            item_w, item_h = items[0].get_size()
            item_x, item_y = self.get_position_of_item(pos)
            
            w, h = self.get_size()
            
            # scroll if necessary
            if (item_y < self.__offset):
                self.move(0, item_y - self.__offset)
            elif (item_y > self.__offset + h - item_h):
                self.move(0, item_y - self.__offset - (h - item_h))
                
        #end if
        
    """
    def set_cursor(self, pos):
    
        #prev_pos = self.get_cursor()
        ItemView.set_cursor(self, pos)
        #if (prev_pos != -1):
        #    self.__render_item(prev_pos)            
        #self.__render_item(pos)
        self.scroll_to_item(pos)
        #self.render()
    """
        
    def float_item(self, pos, x = 0, y = 0):
        """
        Makes the given item floating. Only one item can be floating at a time.
        Pass C{-1} to disable floating.
        
        @param pos: position of the item to float
        @param x:   x-position of the floating item
        @param y:   y-position of the floating item
        """
        
        self.__floating_item = pos
        self.__floating_position = (x, y)


    def has_floating_item(self):
        """
        Returns whether there is an item currently floating.
        
        @return: whether an item is floating
        """
        
        return (self.__floating_item != -1)


    def get_floating_item(self):
        """
        Returns the index number of the currently floating item.

        @return: index number
        """
        
        return self.__floating_item



    def fx_slide_left(self):

        def fx(params):
            from_x, to_x = params
            dx = (to_x - from_x) / 3
            
            if (dx > 0):
                screen.move_area(x + dx, y, w - dx, h, -dx, 0)
                screen.copy_pixmap(buf, from_x, 0, x + w - dx, y, dx, h)

                params[0] = from_x + dx
                params[1] = to_x
                return True

            else:
                dx = to_x - from_x
                screen.move_area(x + dx, y, w - dx, h, -dx, 0)
                screen.copy_pixmap(buf, from_x, 0, x + w - dx, y, dx, h)
                
                return False


        if (not self.may_render()): return

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        #if (self.__scrollbar_pmap):
        #    slider_width, nil = self.__scrollbar_pmap.get_size()
        #    slider_width /= 2
        #    w -= slider_width

        buf = self.__buffer
        buf.fill_area(0, 0, w, h, self.__bg_color)
        self.render_at(buf)

        self.animate(50, fx, [0, w])



    def fx_slide_right(self):

        def fx(params):
            from_x, to_x = params
            dx = (to_x - from_x) / 3
            
            if (dx > 0):
                screen.move_area(x, y, w - dx, h, dx, 0)
                screen.copy_pixmap(buf, w - from_x - dx, 0, x, y, dx, h)

                params[0] = from_x + dx
                params[1] = to_x
                return True

            else:
                dx = to_x - from_x
                screen.move_area(x, y, w - dx, h, dx, 0)
                screen.copy_pixmap(buf, w - from_x - dx, 0, x, y, dx, h)

                return False


        if (not self.may_render()): return

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        #if (self.__scrollbar_pmap):
        #    slider_width, nil = self.__scrollbar_pmap.get_size()
        #    slider_width /= 2
        #    w -= slider_width

        buf = self.__buffer
        buf.fill_area(0, 0, w, h, self.__bg_color)
        self.render_at(buf)

        self.animate(50, fx, [0, w])

