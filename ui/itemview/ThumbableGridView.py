from GridView import GridView
from ui.KineticScroller import KineticScroller
from ui.Pixmap import text_extents
from theme import theme

import gobject
import time


# hide the letter display after this many milliseconds without scrolling
_LETTER_TIMEOUT = 500

# letters are only displayed if the list is at least this many times bigger
# than the screen size
_LETTER_LENGTH_THRESHOLD = 5


class ThumbableGridView(GridView):

    CLICK_BEHAVIOR_SINGLE = 0
    CLICK_BEHAVIOR_DOUBLE = 1
    

    def __init__(self):
       
        # value of the built-in slider
        self.__slider_value = 0.0
        
        # slider grab position
        self.__slider_grab_pos = 0
        
        # whether the user is using the slider
        self.__is_sliding = False
       
        
        # whether multi select is enabled
        self.__multi_select = False
               
        # whether the index letter is enabled
        self.__letter_enabled = True
               
        # whether the letter is visible
        self.__letter_visible = False
        
        # timeout handler for hiding the letter view
        self.__letter_timeout_handler = None
        
        # handler for auto scrolling when dragging items
        self.__autoscroll_handler = None
        
        # timestamp of when the cursor was last positioned
        self.__last_cursor_time = 0
        
        # click behavior for selecting items
        self.__click_behavior = self.CLICK_BEHAVIOR_SINGLE
        
        # index of the marked item
        self.__marked_idx = -1
        
        GridView.__init__(self)
        self.connect_button_pressed(self.__on_press_button)
        self.connect_button_released(self.__on_release_button)
        self.connect_pointer_moved(self.__on_pointer_moved)
        self.add_overlay_renderer(self.__render_letter)
        self.add_overlay_renderer(self.__render_slider)
        
        self.__kscr = KineticScroller(self)
        self.__kscr.connect_scrolling_started(self.__on_scrolling_started)
        self.__kscr.connect_clicked(self.__on_clicked)
        self.__kscr.connect_tap_and_hold(self.__on_tap_and_hold)


    def __render_letter(self, screen):

        if (not self.__letter_enabled): return
    
        w, h = self.get_size()
        total_w, total_h = self.get_total_size()

        # render letter
        if (self.__letter_visible and h * _LETTER_LENGTH_THRESHOLD < total_h):
            idx = self.get_item_at(0, h / 2)
            if (idx >= self.count_items() - 1): return
            item = self.get_item(idx)
            letter = item.get_letter()
            
            if (letter):
                tw, th = text_extents(letter, theme.font_list_letter)
                tx = (w - tw) / 2
                ty = (h - th) / 2
                border_width = 10
                bw = th + 2 * border_width
                bh = bw
                bx = (w - bw) / 2
                by = (h - bh) / 2
                
                screen.fill_area(bx, by, bw, bh,
                                 theme.color_list_letter_background)
                screen.draw_text(letter, theme.font_list_letter, tx, ty,
                                 theme.color_list_letter)
            #end if
        #end if


    def __render_slider(self, screen):
    
        w, h = self.get_size()
        t_w, t_h = self.get_total_size()
        if (self.__letter_visible and t_h > h * 2):
            h -= theme.mb_list_slider.get_height()
            screen.draw_pixbuf(theme.mb_list_slider, 0, self.__slider_value * h)


    def __on_scrolling_started(self):
    
        #csr = self.get_cursor()
        #if (csr != -1):
        #    self.set_cursor(-1)
        #    self.invalidate_item(csr)
        #    self.render()
        pass
        

    def __on_clicked(self, px, py):

        idx = self.get_item_at(px, py)
        x, y = self.get_position_of_item(idx)
        #self.set_cursor(idx)
        #self.invalidate_item(idx)
        #self.render()

        csr = self.get_cursor()
        item = self.get_item(idx)

        if (self.__multi_select):
            item.set_selected(not item.is_selected())

        elif (px > 40):
            # the touchscreen of Maemo4 devices is not sensitive enough for
            # single click operation
            if (self.__click_behavior == self.CLICK_BEHAVIOR_SINGLE or
                (idx == self.get_cursor() and
                 time.time() - self.__last_cursor_time > 0.5)):
                item.click_at(px - x, py - y)
                self.set_cursor(-1)
            else:
                self.set_cursor(idx)
                self.__last_cursor_time = time.time()
                if (csr != -1):
                    self.invalidate_item(csr)
                #self.render()
            #end if
        #end if
        self.invalidate_item(idx)
        
        
    def __on_tap_and_hold(self, px, py):

        if (not self.__multi_select and not self.has_floating_item()):
            idx = self.get_item_at(px, py)
            x, y = self.get_position_of_item(idx)
            item = self.get_item(idx)
            item.tap_and_hold(px - x, py - y)
        #end if


    def __on_press_button(self, px, py):
    
        idx = self.get_item_at(px, py)
        item = self.get_item(idx)
        w, h = self.get_size()

        if (px > w - 80 and item.is_draggable()):
            # handle drag-sorting
            self.float_item(idx, px - w, py)
            self.__kscr.set_enabled(False)
            self.invalidate()
            self.render()

        elif (px < 40):
            self.stop_scrolling()
            self.__is_sliding = True
            w, h = self.get_size()
            h -= theme.mb_list_slider.get_height()
            self.__slider_grab_pos = py - self.__slider_value * h
            
        else:
            # handle clicking
            if (item.is_button()):
                if (self.__marked_idx != -1):
                    item2 = self.get_item(self.__marked_idx)
                    item2.set_marked(False)
                    self.invalidate_item(item2)
                    
                item.set_marked(True)
                self.invalidate_item(idx)
                self.__marked_idx = idx
        


    def __on_release_button(self, px, py):
        
        if (self.has_floating_item()):
            self.float_item(-1)
            self.__kscr.set_enabled(True)
            self.invalidate()

            self.render()

        elif (self.__is_sliding):
            self.stop_scrolling()
            self.__is_sliding = False

        else:
            idx = self.get_item_at(px, py)
            item = self.get_item(idx)
            if (item.is_button()):
                item2 = self.get_item(self.__marked_idx)
                item2.set_marked(False)
                self.invalidate_item(self.__marked_idx)
                self.__marked_idx = -1

        if (self.__autoscroll_handler):
            gobject.source_remove(self.__autoscroll_handler)
            self.__autoscroll_handler = None


            
    def __on_pointer_moved(self, px, py):
    
        if (self.has_floating_item()):
            # handle drag-sorting
            floating_idx = self.get_floating_item()
            new_idx = self.get_item_at(px, py)
            if (0 <= new_idx < self.count_items()):
                w, h = self.get_size()
                self.shift_item(floating_idx, new_idx - floating_idx)

                self.float_item(new_idx, px - w, py)
                self.invalidate()
                self.render()
            
            if (self.__autoscroll_handler):
                gobject.source_remove(self.__autoscroll_handler)
                self.__autoscroll_handler = None
            
            w, h = self.get_size()
            if (py < 80):
                self.__autoscroll_handler = gobject.timeout_add(
                                                 50, self.__do_autoscroll, -30)

            elif (py > h - 80):
                self.__autoscroll_handler = gobject.timeout_add(
                                                 50, self.__do_autoscroll, 30)

        elif (self.__is_sliding):
            w, h = self.get_size()
            total_w, total_h = self.get_total_size()
            percent = (py - self.__slider_grab_pos) / \
                      float((h - theme.mb_list_slider.get_height()))
            percent = max(min(percent, 1.0), 0.0)
            prev_offset = self.get_offset()
            offset = int((total_h - h) * percent)
            #self.stop_scrolling()
            self.move(0, offset - prev_offset)
        #end if


    def __on_letter_timeout(self):
    
        self.__letter_timeout_handler = None
        self.__letter_visible = False
        self.render()
        

    def __do_autoscroll(self, amount):
    
        self.move(0, amount)
        return True


    def stop_scrolling(self):
    
        self.__kscr.stop_scrolling()


    def move(self, dx, dy):
    
        self.__letter_visible = True

        prev_offset = self.get_offset()
        dy, dy = GridView.move(self, dx, dy)
        
        # stop scrolling immediately if there is no more motion
        if (prev_offset == self.get_offset()):
            self.__kscr.stop_scrolling()
        
        # position slider
        self.__update_slider()

        if (self.__letter_timeout_handler):
            gobject.source_remove(self.__letter_timeout_handler)
        self.__letter_timeout_handler = gobject.timeout_add(_LETTER_TIMEOUT,
                                                      self.__on_letter_timeout)

        return (dx, dy)


    def set_multi_select(self, value):
    
        self.__multi_select = value
        for item in self.get_items():
            item.set_selected(False)
        self.invalidate()
        self.render()


    def select_all(self):
        
        if (self.__multi_select):
            for item in self.get_items():
                item.set_selected(True)
            self.invalidate()
            self.render()
        #end if            


    def unselect_all(self):
        
        for item in self.get_items():
            item.set_selected(False)
        self.invalidate()
        self.render()


    def set_letter_enabled(self, value):
    
        self.__letter_enabled = value


    def set_click_behavior(self, behavior):
    
        self.__click_behavior = behavior


    def switch_item_set(self, s):
    
        GridView.switch_item_set(self, s)
        self.__update_slider()

    def clear_items(self):
    
        GridView.clear_items(self)
        self.__update_slider()


    def __update_slider(self):

        w, h = self.get_size()
        total_w, total_h = self.get_total_size()
        if (total_h <= h):
            percent = 0.0
        else:
            percent = self.get_offset() / float(total_h - h)
        self.__slider_value = percent

        """
        if (self.__slider):
            w, h = self.get_size()
            total_w, total_h = self.get_total_size()
            if (total_h <= h):
                percent = 0.0
            else:
                percent = self.get_offset() / float(total_h - h)
            self.__slider.set_value(1.0 - percent)
        #end if    
        """
       
        
    def connect_item_activated(self, cb, *args):
        
        print "connect_item_activated"

        
    def connect_item_menu_opened(self, cb, *args):
        
        print "connect_item_menu_opened"

