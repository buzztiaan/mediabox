from ItemList import ItemList
from ui.Pixmap import Pixmap, text_extents

from theme import theme

import gobject
import time


# time after which the letter disappears when scrolling stops
_LETTER_TIMEOUT = 250


class ThumbableList(ItemList):

    def __init__(self, itemsize, gapsize):
    
        # the slider widget
        self.__slider = None
        
        # whether the letter is visible
        self.__letter_visible = False
        
        self.__letter_hiding_handler = False
        
        # time of letter appearance (for fade-in effect)
        self.__letter_appearance_time = 0

        
        ItemList.__init__(self, itemsize, gapsize)
        self.add_overlay_renderer(self.__render_letter)
        
        
    def set_thumb_slider(self, w):
    
        self.__slider = w
        self.__slider.connect_value_changed(self.__on_drag_slider)
        


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

        
        
    def __on_drag_slider(self, percent):
    
        w, h = self.get_size()
    
        prev_offset = self.get_offset()
        offset = int((self.get_total_size() - h) * (1.0 - percent))
        self.__show_letter()
        self.move(0, offset - prev_offset)


    def __render_letter(self, screen):
    
        x, y = 0, 0
        w, h = self.get_size()
        
        # position slider
        percent = self.get_offset() / float(self.get_total_size() - h)
        if (self.__slider):
            self.__slider.set_value(1.0 - percent)
        
        # render letter
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

