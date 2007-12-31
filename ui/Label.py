from Widget import Widget
from Pixmap import Pixmap, pixmap_for_text

import gobject
import pango


class Label(Widget):

    def __init__(self, esens, text, font, color):
    
        self.__text_pmap = None
        self.__bg = None
        self.__is_scrolling = False
        self.__is_new_text = False
    
        self.__text = text
        self.__font = font
        self.__color = color
    
        Widget.__init__(self, esens)


    def __create_text_pmap(self):
    
        if (not self.__is_new_text): return
        
        self.__text_pmap = pixmap_for_text(self.__text or " ", self.__font)


    def __acquire_background(self):
    
        if (not self.__is_new_text): return
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        text_w, text_h = self.__text_pmap.get_size()

        if (not w): w = text_w
        if (not h): h = text_h
            
        self.__bg = Pixmap(None, w, h)
        self.__bg.copy_buffer(screen, x, y, 0, 0, w, h)


    def __restore_background(self):
    
        if (not self.__is_new_text or not self.__bg): return
        if (not self.may_render()): return
        
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        bg_w, bg_h = self.__bg.get_size()
        screen.copy_pixmap(self.__bg, 0, 0, x, y, bg_w, bg_h)
                

    def __create_text(self):
    
        if (not self.__is_new_text): return
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        text_w, text_h = self.__text_pmap.get_size()

        if (not w): w = text_w
        if (not h): h = text_h        

        # tile background
        for i in range(0, text_w, w):
            self.__text_pmap.copy_pixmap(self.__bg, 0, 0, i, 0, w, h)
        
        # draw text
        self.__text_pmap.draw_text(self.__text, self.__font, 0, 0, self.__color)


    def set_text(self, text):

        self.__is_new_text = True
        self.__text = text

        if (not self.__is_scrolling and self.may_render()):
            self.__render_text(0, 1)
            

    def render(self):

        if (not self.may_render()): return

        self.__is_new_text = True
        self.__create_text_pmap()
        self.__acquire_background()
        self.__create_text()
        self.__is_new_text = False
    
        if (not self.__is_scrolling):    
            self.__render_text(0, 1)

        
        
    def __render_text(self, pos, direction):

        if (self.__is_new_text):
            self.__restore_background()
            self.__create_text_pmap()
            self.__acquire_background()
            self.__create_text()
            self.__is_new_text = False
            pos = 0
            direction = 1
        #end if            

        text_w, text_h = self.__text_pmap.get_size()    
        x, y = self.get_screen_pos()
        w, h = self.get_size()    
        screen = self.get_screen()

        if (not w): w = text_w
        if (not h): h = text_h

        # render currently visible text portion
        if (text_w <= w): pos = 0
        if (self.may_render()):
            screen.copy_pixmap(self.__text_pmap, pos, 0, x, y,
                               min(text_w, w), text_h)

        # handle scrolling
        if (text_w > w and self.may_render()):
            self.__is_scrolling = True
            if (pos == 0):
                direction = 1
                delay = 1500
            elif (pos == text_w - w):
                direction = -1
                delay = 1500
            else:
                delay = 50
            
            if (direction == 1):
                pos += 1
            else:
                pos -= 1

            gobject.timeout_add(delay, self.__render_text, pos, direction)
            
        else:
            self.__is_scrolling = False
        #end if
        
