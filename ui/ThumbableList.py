from ItemList import ItemList
from ui.Pixmap import Pixmap, text_extents

from theme import theme

import gobject
import time


# time after which the thumb slider disappears when scrolling stops
_SLIDER_TIMEOUT = 250

# time after which the letter disappears when scrolling stops
_LETTER_TIMEOUT = 250

# minimal total size in pixels that the list must have for the thumb slider
_MIN_TOTAL_SIZE = 1000


class ThumbableList(ItemList):

    def __init__(self, itemsize, gapsize):

        # whether the slider is visible
        self.__slider_visible = False

        self.__slider_hiding_handler = None
        
        # time of slider appearance (for slide-in effect)
        self.__slider_appearance_time = 0
        
        # whether the user holds the slider
        self.__is_holding_slider = False
        
        # distance from the click position to the top of the slider
        self.__grab_point = 0


        # whether the letter is visible
        self.__letter_visible = False
        
        self.__letter_hiding_handler = False
        
        # time of letter appearance (for fade-in effect)
        self.__letter_appearance_time = 0
        
        self.__scroll_handler = None
        
    
        ItemList.__init__(self, itemsize, gapsize)
        self.connect_button_pressed(self.__on_button_pressed)
        self.connect_button_released(self.__on_button_released)
        self.connect_pointer_moved(self.__on_drag_slider)
        
        
    def __show_slider(self):
    
        def f():
            # don't have slider disappear while holding it
            if (self.__is_holding_slider):
                return True
            else:
                self.__fx_slide_out_slider()
                #self.render()
                self.__slider_visible = False
                return False
    
        if (self.get_total_size() < _MIN_TOTAL_SIZE): return
    
        if (not self.__slider_visible):
            self.__slider_appearance_time = time.time()
    
        self.__slider_visible = True
        if (self.__slider_hiding_handler):
            gobject.source_remove(self.__slider_hiding_handler)
            
        self.__slider_hiding_handler = gobject.timeout_add(_SLIDER_TIMEOUT, f)


    def __show_letter(self):
    
        def f():
            self.__letter_visible = False
            self.render()
            return False
    
        if (not self.__letter_visible):
            self.__letter_appearance_time = time.time()
    
        self.__letter_visible = True
        if (self.__letter_hiding_handler):
            gobject.source_remove(self.__letter_hiding_handler)
            
        self.__letter_hiding_handler = gobject.timeout_add(_LETTER_TIMEOUT, f)

        
                
    def __on_button_pressed(self, px, py):
    
        sx, sy, sw, sh = self.get_slider_coordinates()
        if (self.__slider_visible and
              sx <= px <= sx + sw and sy <= py <= sy + sh):
            self.__is_holding_slider = True
            
            # distance to slider top
            self.__grab_point = py - sy
                
        
    def __on_button_released(self, px, py):
    
        self.__is_holding_slider = False
        
        
    def __on_drag_slider(self, px, py):
    
        if (self.__is_holding_slider):
            py -= self.__grab_point

            w, h = self.get_size()
            py = min(h - 80, max(0, py))
            percent = py / float(h - 80)

            prev_offset = self.get_offset()            
            offset = int((self.get_total_size() - h) * percent)
            self.__show_letter()
            
            #if (self.__scroll_handler):
            #    gobject.source_remove(self.__scroll_handler)
            #self.__scroll_handler = gobject.timeout_add(10, self.move, 0, offset - prev_offset)
            self.move(0, offset - prev_offset)
        
        
    def slider_is_active(self):
        """
        Returns whether the slider is currently active.
        @since: 0.96.5
        
        @return: whether the slider is active
        """
        
        return self.__slider_visible
       
        
    def get_slider_coordinates(self):
        """
        Returns the coordinates and size of the slider on the list.
        @since: 0.96.5
        
        @return: x, y, w, h
        """
        
        w, h = self.get_size()
        percent = self.get_offset() / float(self.get_total_size() - h)
        sh = h - 80
        sy = int(percent * sh)
        #return (w - 80, sy, 80, 80)
        return (0, sy, 80, 80)
        
        
    def _render_scrollbar(self, screen):
    
        ItemList._render_scrollbar(self, screen)

        x, y = 0, 0
        w, h = self.get_size()
        
        now = time.time()
        if (self.__slider_visible):
            age = now - self.__slider_appearance_time
            if (age < 0.5):
                self.__slider_offset = -80 + min(80, int(age / 0.002))

            sx, sy, sw, sh = self.get_slider_coordinates()
            screen.draw_pixbuf(theme.mb_list_slider,
                               x + sx + self.__slider_offset,
                               y + sy)
        #end if
            

        if (self.__letter_visible):
            idx = self.get_index_at(h / 2)
            item = self.get_items()[idx]
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


    def move(self, dx, dy):
    
        ItemList.move(self, dx, dy)
        self.__show_slider()


    def __fx_slide_out_slider(self):
    
        def fx(params):
            from_x, to_x = params
            self.__slider_offset = 0 - from_x
            self.render()
            
            if (self.__slider_offset > -80):
                params[0] = from_x + 20
                params[1] = to_x
                return True
                
            else:
                return False

        if (not self.may_render()): return
        self.animate_with_events(50, fx, [0, 80])
