from ItemList import ItemList
from ui.Pixmap import Pixmap, text_extents

from theme import theme

import gobject


class ThumbableList(ItemList):

    def __init__(self, itemsize, gapsize):

        # whether the slider is visible
        self.__slider_visible = False

        self.__slider_hiding_handler = None
        
        # whether the user holds the slider
        self.__is_holding_slider = False
        
        # distance from the click position to the top of the slider
        self.__grab_point = 0


        # whether the letter is visible
        self.__letter_visible = False
        
        self.__letter_hiding_handler = False
        
    
        ItemList.__init__(self, itemsize, gapsize)
        self.connect_button_pressed(self.__on_button_pressed)
        self.connect_button_released(self.__on_button_released)
        self.connect_pointer_moved(self.__on_drag_slider)
        
        
    def __show_slider(self):
    
        def f():
            self.__slider_visible = False
            self.render()
    
        if (self.get_total_size() < 1000): return
    
        self.__slider_visible = True
        if (self.__slider_hiding_handler):
            gobject.source_remove(self.__slider_hiding_handler)
            
        self.__slider_hiding_handler = gobject.timeout_add(500, f)


    def __show_letter(self):
    
        def f():
            self.__letter_visible = False
            self.render()
    
        self.__letter_visible = True
        if (self.__letter_hiding_handler):
            gobject.source_remove(self.__letter_hiding_handler)
            
        self.__letter_hiding_handler = gobject.timeout_add(500, f)

        
                
    def __on_button_pressed(self, px, py):
    
        sx, sy, sw, sh = self.get_slider_coordinates()
        if (self.__slider_visible and
              sx <= px <= sx + sw and sy <= py <= sy + sh):
            self.__is_holding_slider = True
            
            # distance to slider top
            self.__grab_point = py - sy
            
        else:
            self.__slider_visible = False
            self.render()
        
        
        
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
        return (w - 80, sy, 80, 80)
        
        
    def _render_scrollbar(self, screen):
    
        ItemList._render_scrollbar(self, screen)

        x, y = 0, 0
        w, h = self.get_size()
        
        if (self.__slider_visible):
            sx, sy, sw, sh = self.get_slider_coordinates()
            #screen.fit_pixbuf(theme.mb_panel, x + sx, y+ sy, sw, sh)
            screen.draw_pixbuf(theme.mb_list_slider, x + sx, y + sy)

        if (self.__letter_visible):
            idx = self.get_index_at(h / 2)
            item = self.get_items()[idx]
            letter = item.get_letter()
            if (not letter): return
            
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

    def move(self, dx, dy):
    
        ItemList.move(self, dx, dy)
        self.__show_slider()

