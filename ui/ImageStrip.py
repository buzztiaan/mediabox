"""
A scrollable strip of images.
"""

from Widget import Widget
from Pixmap import Pixmap, TEMPORARY_PIXMAP
from SharedPixmap import SharedPixmap

import gtk
import gobject
import threading


_BPP = gtk.gdk.get_default_root_window().get_depth()


class ImageStrip(Widget):
    """
    Class for rendering a scrollable strip of images.
    """

    def __init__(self, gapsize):
        """
        Creates a new ImageStrip object.
        
        @param gapsize: size of the gap between images in pixels.
        """
    
        self.__arrows = (None, None, None, None)
        self.__arrows_save_under = None
        self.__scrollbar_pmap = None
        self.__scrollbar_pbuf = None
        self.__cap_top = None
        self.__cap_top_size = (0, 0)
        self.__cap_bottom = None
        self.__cap_bottom_size = (0, 0)
    
        # index and position of a floating item
        # index = -1 means that no item is currently floating
        self.__floating_index = -1
        self.__floating_position = 0

        # the currently hilighted image    
        self.__hilighted_image = -1
    
        # shared pixmap for storing the items
        self.__shared_pmap = None
    
        Widget.__init__(self)

        self.__images = []
        self.__bg = None
        self.__bg_color = None
        self.__offset = 0
        self.__canvas = None
        self.__cmap = None
        self.__itemsize = 0 #itemsize
        self.__gapsize = gapsize
        self.__totalsize = 0
        
        self.__scroll_to_item_handler = None
        self.__scroll_to_item_index = 0

        # whether we wrap around
        self.__wrap_around = True
        
        self.__buffer = Pixmap(None, 100, 100)
        self.__buffer_dirty = False
 
        self.set_size(100, 100)
 
 
    def _reload(self):
        """
        Reload graphics when theme has changed.
        """

        self.invalidate_buffer()

        if (self.__scrollbar_pbuf):
            self.set_scrollbar(self.__scrollbar_pbuf)

        if (self.__shared_pmap):
            self.__shared_pmap.clear_cache()

        for image in self.__images:
            image.invalidate()


    def invalidate_buffer(self):
        """
        Invalidates the rendering buffer. While nothing has changed, the
        contents of the buffer are taken to redraw the list. If you changed the
        contents of an item you have to invoke this method manually.
        """

        self.__buffer_dirty = True

 
    def set_size(self, w, h):
    
        if ((w, h) == self.get_size()): return

        Widget.set_size(self, w, h)

        if (w > 0 and h > 0):
            self.__buffer = Pixmap(None, w, h)
        self.set_scrollbar(self.__scrollbar_pbuf)

        self.__shared_pmap = None
        for img in self.__images:
            nil, img_h = img.get_size()
            if (not self.__shared_pmap):
                self.__shared_pmap = SharedPixmap(w, img_h)
            img.set_canvas(self.__shared_pmap)
            img.set_size(w, img_h)
 

    def set_bg_color(self, color):
    
        w, h = self.get_size()
        self.invalidate_buffer()
        self.__bg_color = color
        self.__buffer.fill_area(0, 0, w, h, self.__bg_color)
        
        
    def set_background(self, bg):
        """
        Sets the background image from the given pixbuf or filename.
        """
    
        self.invalidate_buffer()
        self.__bg = bg
        
        
    def set_caps(self, top, bottom):
        """
        Sets the top and bottom caps for visual effects. Pass None as value to
        disable a cap.
        Caps are overlay pixbufs and can e.g. be used for fading effects.
        
        @param top: pixbuf for the top cap
        @param bottom: pixbuf for the bottom cap
        """
    
        self.invalidate_buffer()
        self.__cap_top = top
        if (top):
            self.__cap_top_size = (top.get_width(), top.get_height())            
        self.__cap_bottom = bottom
        if (bottom):
            self.__cap_bottom_size = (bottom.get_width(), bottom.get_height())
        
        
    def set_arrows(self, arrows, arrows_off):
        """
        Sets arrow graphics from the given pixbufs. If 'arrows_off' is given,
        it must be the same size as 'arrows'.
        Arrows are displayed if the list can be scrolled in that direction.        
        
        @param arrows:     pixbuf for the arrows
        @param arrows_off: pixbuf for the disabled arrows
        """

        self.invalidate_buffer()
    
        arrow_up = None
        arrow_down = None
        arrow_off_up = None
        arrow_off_down = None
        
        if (arrows):
            w, h = arrows.get_width(), arrows.get_height()
            h2 = h / 2
            arrow_up = arrows.subpixbuf(0, 0, w, h2)
            arrow_down = arrows.subpixbuf(0, h2, w, h2)

            if (arrows_off):
                arrow_off_up = arrows_off.subpixbuf(0, 0, w, h2)
                arrow_off_down = arrows_off.subpixbuf(0, h2, w, h2)
            #end if
            
            pmap1 = Pixmap(None, w, h2)
            pmap2 = Pixmap(None, w, h2)
            self.__arrows_save_under = (pmap1, pmap2)
        #end if

        self.__arrows = (arrow_up, arrow_down, arrow_off_up, arrow_off_down)


    def get_arrows (self):
        """
        Returns the arrow graphics or None if no arrows were set.
        
        @return: the arrows pixbuf
        """

        return self.__arrows


    def set_scrollbar(self, pbuf):
        """
        Sets a pixbuf to use for displaying a scrollbar.
        Pass 'None' in order to remove the scrollbar again.
        
        The scrollbar is not interactive.
        
        @param pbuf: the pixbuf for the scrollbar
        """
    
        self.invalidate_buffer()
    
        self.__scrollbar_pbuf = pbuf
        if (not pbuf):
            self.__scrollbar_pmap = None
        else:
            nil, h = self.get_size()
            w = pbuf.get_width()
            w = max(2, w)
            h = max(2, h)
            self.__scrollbar_pmap = Pixmap(None, w, h)            
            self.__scrollbar_pmap.draw_pixbuf(pbuf, 0, 0, w, h, scale = True)


    def float_item(self, idx, pos = 0):
        """
        Floats the given item at the given position. Position is relative
        to the current offset.
        
        @param idx: index number of the item to float
        @param pos: position where to display the item
        """

        self.invalidate_buffer()
        
        self.__floating_index = idx
        self.__floating_position = pos


    def get_image(self, idx):
        """
        Returns the item with the given index.
        
        @param idx: index number of the item to retrieve
        @return: item object
        """
    
        return self.__images[idx]
        
        
    def get_images(self):
        """
        Returns a list of all items.
        
        @return: list of all items
        """
    
        return self.__images[:]
        
        
    def set_images(self, images):
        """
        Sets the list of images to be displayed by the image strip.
        
        @param images: list of StripItem objects
        """

        # remove current images
        while (self.__images):
            img = self.__images.pop()
            del img  
        self.__images = []
        self.__hilighted_image = -1
        
        import gc; gc.collect()

        # append new images
        for img in images:
            self.append_image(img)
        #endfor

        self.invalidate_buffer()
        self.__offset = 0
        
        
    def append_image(self, img):
        """
        Appends the given image item to the list.
        
        @param img: StripItem object to append
        @return: index of the newly appended image
        """

        w, h = self.get_size()
        img_w, img_h = img.get_size()
        if (self.__scrollbar_pbuf):
            w -= self.__scrollbar_pbuf.get_width()
        img.set_size(w, img_h)
        img.set_hilighted(False)

        self.invalidate_buffer()
        if (not self.__shared_pmap):
            self.__shared_pmap = SharedPixmap(w, img_h)

        img.set_canvas(self.__shared_pmap)
        self.__images.append(img)
        self.__itemsize = img_h

        self.__totalsize = (self.__itemsize + self.__gapsize) * len(self.__images)


        #if (len(self.__images) < 30): self.__shared_pmap.prepare(img)
        
        return len(self.__images) - 1


    def insert_image(self, img, pos):
        """
        Inserts the given image item at the given position.
        
        @param img: StripItem object to insert
        @param pos: index position after which the image gets inserted
        """

        w, h = self.get_size()
        img_w, img_h = img.get_size()
        if (self.__scrollbar_pbuf):
            w -= self.__scrollbar_pbuf.get_width()
        img.set_size(w, img_h)

        self.invalidate_buffer()
        if (not self.__shared_pmap):
            self.__shared_pmap = SharedPixmap(w, img_h)

        img.set_canvas(self.__shared_pmap)
        self.__images.insert(pos + 1, img)
        self.__itemsize = img_h
        self.__totalsize = (self.__itemsize + self.__gapsize) * len(self.__images)

        #if (len(self.__images) < 30): self.__shared_pmap.prepare(img)
                     
        
    def replace_image(self, idx, image):
       """
       Replaces the image item at the given position with a new one.
       
       @param idx: index of the item to replace
       @param image: StripItem object with which to replace
       """

       self.invalidate_buffer()
       img = self.__images[idx]
       self.__images[idx] = image
       del img
       
       if (self.__hilighted_image == idx):
            image.set_hilighted(True)       
       #self.render()

       
       
    def remove_image(self, idx):
        """
        Removes the image at the given position.
        
        @param idx: index of the image to remove
        """
    
        self.invalidate_buffer()
        w, h = self.get_size()
        del self.__images[idx]
        self.__totalsize = (self.__itemsize + self.__gapsize) * len(self.__images)        

        if (self.__offset > idx * (self.__itemsize + self.__gapsize)):
            self.__offset = max(0, self.__offset - \
                                   (self.__itemsize + self.__gapsize))

        if (idx == self.__hilighted_image):
            self.__hilighted_image = -1
        elif (idx < self.__hilighted_image):
            self.__hilighted_image -= 1

        #self.render()



    def hilight(self, idx):
        """
        Sets the given image as hilighted. Only one image is hilighted at
        a time.
        """

        self.invalidate_buffer()
        if (self.__hilighted_image >= 0):
            try:
                item = self.get_image(self.__hilighted_image)
                item.set_hilighted(False)
            except:
                pass

        if (idx >= 0 and idx < len(self.__images)):
            item = self.get_image(idx)
            item.set_hilighted(True)
            self.__hilighted_image = idx
            self.render()


        
    def set_wrap_around(self, value):
        """
        Sets whether the strip wraps around, i.e. it has no beginning or end.
        
        @param value: whether to wrap around
        """
    
        self.__wrap_around = value
        
        if (not value):
            w, h = self.get_size()
            self.__offset = max(0, min(self.__offset, self.__totalsize - h))

    def __is_wrap_around(self):
    
        w, h = self.get_size()
        h -= (self.__cap_top_size[1] + self.__cap_bottom_size[1])
        
        return (self.__wrap_around and self.__totalsize > h)

        
    def get_index_at(self, y):
        """
        Returns the index of the item at the given position or -1 if there's no
        item at that position.
        
        @param y: position
        @return: index of the item at that position
        """
        
        idx, relpos = self.get_index_at_and_relpos(y)
        return idx
            

    def get_index_at_and_relpos(self, y):
        """
        Returns the index of the item at the given position or -1 if there's no
        item at that position. Also returns, the per one percentage of the
        y position inside the row.

        @param y: position
        @return: tuple of index of the item at that position and the relative
                 position
        """
      
        if (not self.__is_scrollable()):
            cw, ch = self.__cap_top_size
            y -= ch
        
        if (not self.__images or y > self.__totalsize):
            return -1, 0
        else:
            blocksize = self.__itemsize + self.__gapsize
            pos = self.__offset + y            
            index = (pos / blocksize)
            inside_y = (float(pos) / blocksize) - index
            
            if (index < 0 or index >= len(self.__images)):
                if (self.__is_wrap_around()):
                    index %= len(self.__images)
                else:
                    index = -1
        
            return index, inside_y
            
            
    def swap(self, idx1, idx2):
        """
        Swaps the place of two images.
        
        @param idx1: place 1
        @param idx2: place 2
        """
        
        self.invalidate_buffer()
        temp = self.__images[idx1]
        self.__images[idx1] = self.__images[idx2]
        self.__images[idx2] = temp

        if (self.__hilighted_image == idx1):
            self.__hilighted_image = idx2
        elif (self.__hilighted_image == idx2):
            self.__hilighted_image = idx1


        #self.render()


    def __is_scrollable(self):
        """
        Returns whether this strip has enough items to be scrollable.
        """
        
        w, h = self.get_size()
        cw, ch = self.__cap_top_size
        
        return (self.__totalsize > h - ch)
    
     
    def get_offset(self):
        """
        Returns the current display offset.
        
        @return: current display offset
        """
    
        return self.__offset
        
        
    def set_offset(self, offset):
        """
        Sets the current display offset.
        
        @param offset: new display offset
        """
    
        w, h = self.get_size()
        offset = min(offset, max(0, self.__totalsize - h))
        self.__offset = offset
        
        
    def __render_arrows(self):
        """
        Renders the arrows onto the buffer.
        """

        if (not self.may_render()): return

        x, y = 0, 0 #self.get_screen_pos()
        w, h = self.get_size()
        screen = self.__buffer #self.get_screen()

        arrow_up, arrow_down, arrow_off_up, arrow_off_down = self.__arrows
        if (not arrow_up): return
        
        arrow_width, arrow_height = arrow_up.get_width(), arrow_up.get_height()
        
        pmap1, pmap2 = self.__arrows_save_under
        pmap1.copy_pixmap(screen, x + (w - arrow_width), y, 0, 0,
                          arrow_width, arrow_height)
        pmap2.copy_pixmap(screen,
                          x + (w - arrow_width), y + h - arrow_height, 0, 0,
                          arrow_width, arrow_height)        

        if (self.__offset > 0):
            screen.draw_pixbuf(arrow_up, x + (w - arrow_width), y)
        elif (arrow_off_up):
            screen.draw_pixbuf(arrow_off_up, x + (w - arrow_width), y)

        if (self.__offset < self.__totalsize - h - 10):
            screen.draw_pixbuf(arrow_down,
                               x + (w - arrow_width), y + h - arrow_height)
        elif (arrow_off_down):
            screen.draw_pixbuf(arrow_off_down,
                               x + (w - arrow_width), y + h - arrow_height)
            


    def __unrender_arrows(self):
        """
        Removes the arrows from the buffer.
        """

        if (not self.may_render()): return
        
        x, y = 0, 0 #self.get_screen_pos()
        w, h = self.get_size()
        screen = self.__buffer #self.get_screen()

        arrow_up, arrow_down, nil, nil = self.__arrows
        arrow_width, arrow_height = arrow_up.get_width(), arrow_up.get_height()

        pmap1, pmap2 = self.__arrows_save_under
        screen.copy_pixmap(pmap1,
                           0, 0,
                           x + (w - arrow_width), y,
                           arrow_width, arrow_height)
        screen.copy_pixmap(pmap2,
                           0, 0,
                           x + (w - arrow_width), y + h - arrow_height,
                           arrow_width, arrow_height)
        
        
    def __render_scrollbar(self):
        """
        Renders the scrollbar onto the buffer.
        """

        x, y = 0, 0 #self.get_screen_pos()
        w, h = self.get_size()
        screen = self.__buffer

        if (self.__totalsize > 0):
            percent = self.__offset / float(self.__totalsize)
            slider_size = (h / float(self.__totalsize)) * h
        else:
            percent = 0
            slider_size = h

        y1 = int(h * percent)
        y2 = int(y1 + slider_size)

        slider_width, nil = self.__scrollbar_pmap.get_size()
        slider_width /= 2

        screen.copy_pixmap(self.__scrollbar_pmap,
                           0, 0,
                           x + w - slider_width, y,
                           slider_width, h)
        screen.copy_pixmap(self.__scrollbar_pmap,
                           slider_width, 0, x + w - slider_width, y + y1,
                           slider_width, y2 - y1 + 1)


    
    def __render_floating_item(self):
        """
        Renders the floating item onto the buffer.
        """
    
        x, y = 0, 0 #self.get_screen_pos()
        w, h = self.get_size()
        screen = self.__buffer
        
        try:        
            item = self.__images[self.__floating_index]
        except:
            return

        self.__shared_pmap.prepare(item)
        fw, fh = item.get_size()
        fx = x + (w - fw) / 2
        fx += 48   # indent floating item a bit
        fy = y + self.__floating_position - fh / 2
        self.__buffer.draw_pixmap(self.__shared_pmap, fx, fy)


    def __render_buffered(self, screen, offset, height):
        """
        Composes the widget onto the buffer.
        """

        x, y = self.get_screen_pos()
        w, h = self.get_size()

        TEMPORARY_PIXMAP.copy_pixmap(self.__buffer, 0, 0, 0, 0, w, h)

        #if (self.__arrows[0]):
        #    self.__render_arrows()
        
        if (self.__scrollbar_pmap):
            self.__render_scrollbar()
            
        if (self.__floating_index >= 0):
            self.__render_floating_item()

        if (self.__cap_top):
            cw, ch = self.__cap_top_size
            self.__buffer.draw_pixbuf(self.__cap_top, 0, 0, w, ch)
            
        if (self.__cap_bottom):
            cw, ch = self.__cap_bottom_size
            self.__buffer.draw_pixbuf(self.__cap_bottom, 0, h - ch, w, ch)
            
        screen.copy_pixmap(self.__buffer, 0, offset, x, y + offset, w, height)
        self.__buffer.copy_pixmap(TEMPORARY_PIXMAP, 0, 0, 0, 0, w, h)
        self.__buffer_dirty = False

        
    def render_this(self):

        w, h = self.get_size()
        screen = self.get_screen()

        if (self.__buffer_dirty):
            self.render_full()
            self.__render_buffered(screen, 0, h)
            
        else:
            # nothing changed; simply render the buffer again
            print "restoring from buffer"
            self.__render_buffered(screen, 0, h)
        
        
        
    def render_full(self):
        """
        Fully renders the widget onto the buffer.
        """
    
        w, h = self.get_size()
        self.__render(0, h)

        if (self.__arrows[0]):
            self.__render_arrows()      


    def __render(self, render_offset, render_height):
        """
        Renders the given portion to the offscreen buffer.
        """
   
        if (not self.may_render()): return

        
        blocksize = self.__itemsize + self.__gapsize
        render_to = render_offset + render_height

        x, y = 0, 0 #self.get_screen_pos()
        w, h = self.get_size()
        screen = self.__buffer
        if (not self.__wrap_around and self.__totalsize > h and 
              self.__offset > self.__totalsize - h):
            self.__offset = self.__totalsize - h

        if (not self.__is_scrollable()):
            cw, ch = self.__cap_top_size
            screen.fill_area(x, y, w, ch, self.__bg_color)
            y += ch
            h -= ch

        # render items
        while (self.__images and render_offset < render_to):            
            idx = ((self.__offset + render_offset) / blocksize)

            # wrap around is not available when there are too few items
            if (self.__is_wrap_around()):
                idx %= len(self.__images)
            elif (idx >= len(self.__images) or idx < 0):
                break                            

            img_offset = (self.__offset + render_offset) % blocksize

            # compute the remaining visible part of the item            
            remain = min(self.__itemsize - img_offset, render_to - render_offset)
            if (remain > 0):
                # prepare item
                item = self.__images[idx]
                self.__shared_pmap.prepare(item)
                pw, ph = item.get_size()

                # center it, unless the item is wider than the strip
                if (pw < w):
                    offx = (w - pw) / 2
                else:
                    offx = 0

                if (self.__floating_index != idx):
                    # render item
                    screen.copy_pixmap(self.__shared_pmap, 0, img_offset,
                                       x + offx, y + render_offset,
                                       pw, remain)
                else:
                    # leave a gap where the floating item would have been
                    screen.fill_area(x + offx, y + render_offset, pw, remain,
                                     self.__bg_color)

                # fill the empty space at the sides if the item was centered
                if (offx > 0 and self.__bg_color):
                    screen.fill_area(x, y + render_offset,
                                     offx, remain,
                                     self.__bg_color)
                    screen.fill_area(x + offx + pw, y + render_offset,
                                     offx, remain,
                                     self.__bg_color)
            #end if
            
            render_offset += (remain + self.__gapsize)
        #end while
        
        # render the space not covered by items
        if (self.__bg_color):

            # fill the space beneath the items, if any
            if (render_offset < render_to):
                screen.fill_area(x, y + render_offset, w, render_to - render_offset,
                                 self.__bg_color)
                #screen.draw_subpixbuf(self.__bg,
                #                      0, render_offset, x, y + render_offset,
                #                      w, render_to - render_offset)
            #end if

            if (self.__gapsize > 0):
                # compute position of first gap
                gap_offset = 0 - (self.__offset % blocksize) - self.__gapsize
                
                # render gap by gap
                while (gap_offset < h):
                    if (gap_offset + self.__gapsize < 0):
                        # gap is off screen
                        gap_offset += self.__gapsize + self.__itemsize
                        continue
                    elif (gap_offset < 0):
                        # gap is partially on screen
                        render_offset = 0
                        remain = self.__gapsize - abs(gap_offset)
                    else:
                        # gap is on screen
                        render_offset = gap_offset
                        remain = min(self.__gapsize, h - render_offset)
                        
                    # render gap if visible
                    if (remain > 0):
                        screen.fill_area(x, y + render_offset, w, remain,
                                         self.__bg_color)
                        #screen.draw_subpixbuf(self.__bg,
                        #                   0, render_offset, x, y + render_offset,
                        #                   min(w, self.__bg.get_width()),
                        #                   min(remain, self.__bg.get_height()))
                    #end if

                    gap_offset += blocksize    
                #end while
            #end if
        #end if

        
    def move(self, nil, delta):
        """
        Scrolls the strip by the given amount.
        
        @param nil: ignored (for compatibility with the KineticScroller)
        @param delta: amount to scroll
        """
    
        if (not self.__scroll_to_item_handler):
            self.__move(nil, delta)

        
        
    def __move(self, nil, delta):
        """
        Scrolls the image strip by the given positive or negative amount.
        """

        self.invalidate_buffer()
                
        x, y = 0, 0 #self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        if (not self.__is_wrap_around()):
            if (self.__offset + delta > self.__totalsize - h):
                return
            elif (self.__offset + delta < 0):
                return
        #end if

        self.__offset += delta
        while (self.__offset < 0):
            self.__offset += self.__totalsize
        while (self.__offset > self.__totalsize):
            self.__offset -= self.__totalsize
            

        if (not self.may_render()): return

        #if (self.__arrows[0]):
        #    self.__unrender_arrows()
            
        if (delta > 0):
            self.__buffer.move_area(x, y + delta, w, h - delta,
                                    0, -delta)
            self.__render(h - delta, delta)

        elif (delta < 0):
            self.__buffer.move_area(x, y, w, h - abs(delta),
                                    0, abs(delta))
            self.__render(0, abs(delta))
            
        #if (self.__arrows[0]):
        #    self.__render_arrows()

        if (self.may_render()):
            self.__render_buffered(screen, 0, h)


    def scroll_to_item(self, idx, force_on_top = False):
        """
        Scrolls to bring the given item into view.
        
        @param idx: index of the item to scroll to
        @param force_on_top: whether the item must appear on top
        """

        def f():
            idx = self.__scroll_to_item_index
            offset = self.__offset

            # offset must be between these values to make the item visible
            # item is at upper border
            offset2 = (self.__itemsize + self.__gapsize) * idx # + self.__itemsize
            # item is at bottom border
            offset1 = offset2 - (h - self.__itemsize) #+ self.__itemsize

            if (self.__cap_top):
                offset2 -= self.__cap_top_size[1]
            if (self.__cap_bottom):
                offset1 += self.__cap_bottom_size[1]

            offset3 = offset1 + self.__totalsize
            offset4 = offset2 + self.__totalsize
            
            if (force_on_top):
                offset1 = offset2
                offset3 = offset4
    
            # stop scrolling if item is visible
            elif (offset1 <= self.__offset <= offset2 or 
                offset3 <= self.__offset <= offset4):
                self.__scroll_to_item_handler = None
                return False                

            # no need to have this animated while the widget is hidden
            if (not self.may_render()):
                self.__offset = max(0, offset2)
                self.__scroll_to_item_handler = None
                return False
           
            # how far would we have to scroll up or down?
            distance1 = offset1 - self.__offset
            distance2 = offset2 - self.__offset
            if (self.__is_wrap_around()):
                distance3 = (offset2 - self.__totalsize) - self.__offset
                distance4 = (offset1 + self.__totalsize) - self.__offset
            else:
                distance3 = distance1
                distance4 = distance2
            
            # determine shortest distance
            def c(a,b): return cmp(abs(a), abs(b))
            distances = [distance1, distance2, distance3, distance4]
            distances.sort(c)
            distance = distances[0]
                                
            # cheat to make scrolling through laaaaarge lists faster
            if (distance > 1000):
                self.__offset += distance - 500
            elif (distance < -1000):
                self.__offset += distance + 500

            delta = distance / 10

            if (distance < 2):
                self.__move(0, max(-h, min(-1, delta)))
            elif (distance > 2):
                self.__move(0, min(h, max(1, delta)))
            else:
                self.__scroll_to_item_handler = None
                return False

            if (self.__offset == offset):
                # nothing moved
                self.__scroll_to_item_handler = None
                return False
                
            #print offset, offset1, offset2, self.__totalsize, distance, distances

            return True

        w, h = self.get_size()
        self.__scroll_to_item_index = idx
        if (not self.__scroll_to_item_handler):
            #self.__scroll_to_item_handler = gobject.timeout_add(5, f)
            self.animate_with_events(50, f)
            #self.set_events_blocked(True)
            #self.set_events_blocked(False)


    """
    def fx_slide_left(self, wait = True):
    
        STEP = 16
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        slider_width, nil = self.__scrollbar_pmap.get_size()
        slider_width /= 2
        w -= slider_width

        buf = Pixmap(None, w, h) #x + w, y + h)
        self.render_at(buf)
        finished = threading.Event()
        
        def f(i):
            screen.copy_pixmap(screen, x + STEP, y, x, y, w - STEP, h)
            screen.copy_pixmap(buf, i, 0, x + w - STEP, y, STEP, h)
            if (i < w - STEP):
                gobject.timeout_add(5, f, i + STEP)
            else:
                self.render()
                finished.set()

        self.set_events_blocked(True)                
        f(0)        
        while (wait and not finished.isSet()): gtk.main_iteration()
        self.set_events_blocked(False)


    def fx_slide_right(self, wait = True):
    
        STEP = 16
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        if (self.__scrollbar_pmap):
            slider_width, nil = self.__scrollbar_pmap.get_size()
            slider_width /= 2
            w -= slider_width

        buf = Pixmap(None, w, h) #x + w, y + h)
        buf.fill_area(0, 0, w, h, self.__bg_color)
        #self.render_at(buf)
        finished = threading.Event()
        
        def f(i):
            screen.copy_pixmap(screen, x, y, x + STEP, y, w - STEP, h)
            screen.copy_pixmap(buf, w - i, 0, x, y, STEP, h)
            if (i < w - STEP):
                gobject.timeout_add(5, f, i + STEP)
            else:
                self.render()
                finished.set()

        self.set_events_blocked(True)                
        f(0)
        while (wait and not finished.isSet()): gtk.main_iteration(False)
        self.set_events_blocked(False)
            
            
    def fx_slide_in(self, wait = True):
    
        STEP = 8
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        buf = Pixmap(None, x + w, y + h)
        self.render_at(buf)
        finished = threading.Event()
        
        def f(i):
            screen.copy_pixmap(screen, x, y, x + STEP, y, w - STEP, h)
            screen.copy_pixmap(buf, w - i - STEP, 0, x, y, STEP, h)
            if (i < w - STEP):
                gobject.timeout_add(5, f, i + STEP)
            else:
                finished.set()
                
        f(0)
        while (wait and not finished.isSet()): gtk.main_iteration()
        

    def fx_slide_out(self, wait = True):
    
        STEP = 8
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        finished = threading.Event()

        def f(i):
            from theme import theme
            screen.copy_pixmap(screen, x + STEP, y, x, y, w - i, h)
            screen.fill_area(x + w - i, y, STEP, h, self.__bg_color)
            #screen.draw_subpixbuf(theme.background, x + w - i, y, x + w - i, y,
            #                      STEP, h)
            #screen.copy_pixmap(buf, x + w - i - 4, y, x, y, 4, h)
            if (i < w):
                gobject.timeout_add(5, f, i + STEP)
            else:
                finished.set()

        f(0)
        while (wait and not finished.isSet()): gtk.main_iteration(False)
    """
