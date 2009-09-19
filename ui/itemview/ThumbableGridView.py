from GridView import GridView
from ui.KineticScroller import KineticScroller
from ui.Pixmap import text_extents
from theme import theme

import gobject


# hide the letter display after this many milliseconds without scrolling
_LETTER_TIMEOUT = 100


class ThumbableGridView(GridView):

    #EVENT_ITEM_CLICKED = "item-clicked"


    def __init__(self):
    
        # the associated slider
        self.__slider = None
        
        # whether we have drag-sort enabled
        self.__has_drag_sort = False
        
        # whether the letter is visible
        self.__letter_visible = False
        
        # timeout handler for hiding the letter view
        self.__letter_timeout_handler = None
        
        
        GridView.__init__(self)
        self.connect_button_released(self.__on_release_button)
        self.connect_pointer_moved(self.__on_pointer_moved)
        self.add_overlay_renderer(self.__render_letter)
        
        self.__kscr = KineticScroller(self)
        self.__kscr.connect_clicked(self.__on_clicked)
        self.__kscr.connect_tap_and_hold(self.__on_tap_and_hold)


    def __render_letter(self, screen):
    
        w, h = self.get_size()

        # render letter
        if (self.__letter_visible):
            idx = self.get_item_at(0, h / 2)
            if (idx >= self.count_items() - 1): return
            item = self.get_item(idx)
            letter = item.get_letter()
            
            if (letter):
                tw, th = text_extents(letter, theme.font_mb_list_letter)
                tx = (w - tw) / 2
                ty = (h - th) / 2
                border_width = 10
                bw = th + 2 * border_width
                bh = bw
                bx = (w - bw) / 2
                by = (h - bh) / 2
                
                screen.fill_area(bx, by, bw, bh,
                                 theme.color_mb_list_letter_background)
                screen.draw_text(letter, theme.font_mb_list_letter, tx, ty,
                                 theme.color_mb_list_letter)
            #end if
        #end if


    def __on_clicked(self, px, py):
    
        idx = self.get_item_at(px, py)
        x, y = self.get_position_of_item(idx)
        item = self.get_item(idx)
        item.click_at(px - x, py - y)
        
        #self.emit_event(self.EVENT_ITEM_CLICKED, idx)
        
        
    def __on_tap_and_hold(self, px, py):
    
        if (self.__has_drag_sort and px < 32):
            idx = self.get_item_at(px, py)
            self.float_item(idx, px, py)
            self.invalidate()
            self.render()


    def __on_release_button(self, px, py):

        if (self.has_floating_item()):
            self.float_item(-1)
            self.invalidate()
            self.render()
            
            
    def __on_pointer_moved(self, px, py):
    
        if (self.has_floating_item()):
            floating_idx = self.get_floating_item()
            new_idx = self.get_item_at(px, py)
            self.shift_item(floating_idx, new_idx - floating_idx)

            self.float_item(new_idx, px, py)
            self.invalidate()
            self.render()
            
            w, h = self.get_size()
            if (py < 30):
                self.move(0, -10)
            elif (py > h - 30):
                self.move(0, 10)
    
        
    def __on_drag_slider(self, percent):

        w, h = self.get_size()
        total_w, total_h = self.get_total_size()
        prev_offset = self.get_offset()
        offset = int((total_h - h) * (1.0 - percent))
        self.move(0, offset - prev_offset)


    #def connect_item_clicked(self, cb, *args):
   # 
   #     self._connect(self.EVENT_ITEM_CLICKED, cb, *args)


    def __on_letter_timeout(self):
    
        self.__letter_timeout_handler = None
        self.__letter_visible = False
        self.render()
        

    def move(self, dx, dy):
    
        self.__letter_visible = True

        prev_offset = self.get_offset()
        GridView.move(self, dx, dy)
        
        # stop scrolling immediately if there is no more motion
        if (prev_offset == self.get_offset()):
            self.__kscr.stop_scrolling()
        
        # position slider
        if (self.__slider):
            w, h = self.get_size()
            total_w, total_h = self.get_total_size()
            percent = self.get_offset() / float(total_h - h)
            self.__slider.set_value(1.0 - percent)

        if (self.__letter_timeout_handler):
            gobject.source_remove(self.__letter_timeout_handler)
        self.__letter_timeout_handler = gobject.timeout_add(_LETTER_TIMEOUT,
                                                      self.__on_letter_timeout)

        
    def associate_with_slider(self, slider):
        """
        Associates this item view with a slider widget. Only one slider may be
        associated with the item view at a time.
        
        @param slider: slider widget
        """
    
        self.__slider = slider
        self.__slider.connect_value_changed(self.__on_drag_slider)
        
        
    def connect_item_activated(self, cb, *args):
        
        print "connect_item_activated"

        
    def connect_item_menu_opened(self, cb, *args):
        
        print "connect_item_menu_opened"

        
    def set_drag_sort_enabled(self, v):
    
        self.__has_drag_sort = v

