"""
A text label with autoscrolling.
"""

from Widget import Widget
from Pixmap import Pixmap, pixmap_for_text

import gobject
import pango
import time



class Label(Widget):

    # text alignments
    LEFT = 0
    RIGHT = 1
    CENTERED = 2

    def __init__(self, text, font, color):
    
        self.__text_pmap = None
        self.__bg = None
        self.__is_new_text = True
        self.__alignment = self.LEFT
        self.__render_timer = None
    
        self.__text = text
        self.__font = font
        self.__color = color
    
        Widget.__init__(self)
        self.__create_text_pmap()


    def _reload(self):
    
        self.__is_new_text = True
        self.__bg = None
        #self.__create_text_pmap()


    def set_size(self, w, h):
    
        Widget.set_size(self, w, h)
        self.__is_new_text = True
        self.__bg = None


    def __create_text_pmap(self):
    
        if (not self.__is_new_text): return
        
        self.__text_pmap = pixmap_for_text(self.__text or " ", self.__font)


    def __acquire_background(self):
    
        if (not self.__is_new_text): return
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        text_w, text_h = self.__text_pmap.get_size()

        if (w <= 0): w = text_w
        if (h <= 0): h = text_h
        
        self.__bg = Pixmap(None, w, text_h)
        y += (h - text_h) / 2
        self.__bg.copy_buffer(screen, x, y, 0, 0, w, text_h)


    def __restore_background(self):
    
        if (not self.__is_new_text or not self.__bg): return
        if (not self.may_render()): return
        
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        text_w, text_h = self.__text_pmap.get_size()

        if (not w): w = text_w
        if (not h): h = text_h

        bg_w, bg_h = self.__bg.get_size()
        y += (h - text_h) / 2
        screen.copy_pixmap(self.__bg, 0, 0, x, y, bg_w, bg_h)
                

    def __create_text(self):
    
        if (not self.__is_new_text): return
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        text_w, text_h = self.__text_pmap.get_size()

        if (not w): w = text_w
        if (not h): h = text_h        

        if (text_w <= w):
            if (self.__alignment == self.LEFT): text_x = 0
            elif (self.__alignment == self.CENTERED): text_x = (w - text_w) / 2
            else: text_x = w - text_w
        else:
            text_x = 0

        # tile background
        for i in range(0, text_w, w):
            self.__text_pmap.copy_pixmap(self.__bg, 0, 0, i - text_x, 0,
                                            w, text_h)
        
        # draw text
        self.__text_pmap.draw_text(self.__text, self.__font, 0, 0, self.__color)


    def set_alignment(self, alignment):
    
        self.__alignment = alignment


    def get_physical_size(self):

        w, h = self.get_size()
        if (self.__text_pmap):
            text_w, text_h = self.__text_pmap.get_size()    
            if (not w): w = text_w
            if (not h): h = text_h

        return (w, h)
        

    def set_text(self, text):

        if (self.__text == text): return

        self.__is_new_text = True
        self.__text = text

        if (self.may_render()):
            if (self.__render_timer):
                gobject.source_remove(self.__render_timer)        
            self.__render_text(0, 1)


    def get_text(self):
    
        return self.__text
            

    def render_this(self):

        self.__is_new_text = True
        self.__create_text_pmap()
        self.__acquire_background()
        self.__create_text()
        self.__is_new_text = False

        if (self.may_render()):
            if (self.__render_timer):
                gobject.source_remove(self.__render_timer)        
            self.__render_text(0, 1)    
        
        
    def __render_text(self, pos, direction, begin_time = 0):

        if (not self.may_render()): return

        if (not begin_time): begin_time = time.time()

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
        if (text_w <= w):
            if (self.__alignment == self.LEFT): text_x = 0
            elif (self.__alignment == self.CENTERED): text_x = (w - text_w) / 2
            else: text_x = w - text_w
        else:
            text_x = 0
            
        if (self.may_render()):
            text_y = (h - text_h) / 2
            #self.use_clipping(True)
            screen.copy_pixmap(self.__text_pmap, pos, 0, x + text_x, y + text_y,
                               min(text_w, w), text_h)
            #self.use_clipping(False)

        # handle scrolling
        # (only scroll for 10 minutes, then stop to save battery)
        if (text_w > w and self.may_render() and begin_time + 600 > time.time()):
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

            self.__render_timer = \
              gobject.timeout_add(delay, self.__render_text, pos, direction,
                                  begin_time)
            
        else:
            self.__render_timer = None
        #end if
        
