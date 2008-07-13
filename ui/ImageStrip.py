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
        #self.__is_scrolling = threading.Event()
        
        # the selection offset initially selects the item in the middle and
        # centers the view around it
        self.__selection_offset = 0 #(self.__height - self.__itemsize) / 2
        
        # whether we wrap around
        self.__wrap_around = True
        
        # handle of the renderer
        self.__render_handler = None

        self.__buffer = Pixmap(None, 800, 480)
 
 
    def _reload(self):

        self.set_bg_color(self.__bg_color)
        if (self.__shared_pmap):
            self.__shared_pmap.clear_cache()

        #self.render_full()
        #self.render()
 
 
    def set_size(self, w, h):
    
        Widget.set_size(self, w, h)
        self.set_scrollbar(self.__scrollbar_pbuf)
 

    def set_bg_color(self, color):
    
        self.__bg_color = color
        self.__buffer.fill_area(0, 0, 800, 480, self.__bg_color)
        
        
    def set_background(self, bg):
        """
        Sets the background image from the given pixbuf or filename.
        """
    
        self.__bg = bg
        
        
    def set_caps(self, top, bottom):
        """
        Sets the top and bottom caps for visual effects. Pass None as value to
        disable a cap.
        """
    
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
        """
    
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
        """

        return self.__arrows


    def set_scrollbar(self, pbuf):
    
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
        """
    
        self.__floating_index = idx
        self.__floating_position = pos


    def get_image(self, idx):
    
        return self.__images[idx]
        
        
    def get_images(self):
    
        return self.__images[:]
        
        
    def set_images(self, images):
        """
        Sets the list of images to be displayed by the image strip.
        It can either be a list of pixbufs or a list of filenames.
        """
        
        while (self.__images):
            img = self.__images.pop()
            del img  
            
        import gc; gc.collect()

        if (images):
            if (not self.__shared_pmap):
                w, h = images[0].get_size()
                self.__shared_pmap = SharedPixmap(w, h)
            
            self.__images = []
            for img in images:
                img.set_canvas(self.__shared_pmap)
                self.__images.append(img)
                
            #self.__images = [ f for f in images ]
            self.__itemsize = self.__images[0].get_size()[1]
            self.__totalsize = (self.__itemsize + self.__gapsize) * len(images)
               
        self.__offset = 0
        self.render()
        
        
    def append_image(self, img):

        if (not self.__shared_pmap):
            w, h = img.get_size()
            self.__shared_pmap = SharedPixmap(w, h)

        img.set_canvas(self.__shared_pmap)    
        self.__images.append(img)
        self.__itemsize = self.__images[0].get_size()[1]
        self.__totalsize = (self.__itemsize + self.__gapsize) * len(self.__images)


        self.render()
        
        return len(self.__images) - 1
                        
        
    def replace_image(self, idx, image):
    
       img = self.__images[idx]
       self.__images[idx] = image
       del img
       self.render()

       
       
    def remove_image(self, idx):
    
        w, h = self.get_size()
        del self.__images[idx]
        self.__totalsize = (self.__itemsize + self.__gapsize) * len(self.__images)        
        self.__offset = max(0, min(self.__offset, self.__totalsize - h))
        self.render()

        
    def overlay_image(self, idx, img, x, y):
        # TODO: deprecated

        self.__images[idx].draw_pixbuf(img, x, y)
        self.render()
        
        
    def set_wrap_around(self, value):
        """
        Sets whether the strip wraps around, i.e. it has no beginning or end.
        """
    
        self.__wrap_around = value
        
        
        
    def set_selection_offset(self, seloff):
        """
        Sets the selection offset.
        The selection offset is the position specifying the currently
        selected item.
        E.g., a selection offset of 0 selects the item displayed at the top,
        while a selection offset of height / 2 - itemsize / 2 selects the item
        in the middle.
        This setting also affects the index_fraction.        
        """
    
        self.__selection_offset = seloff
        
        
    def get_index_at(self, y):
        """
        Returns the index of the item at the given position or -1 if there's no
        item at that position.
        """
        
        if (not self.__images or y > self.__totalsize):
            return -1
        else:
            blocksize = self.__itemsize + self.__gapsize
            pos = self.__offset + y            
            index = (pos / blocksize)
            
            if (index < 0 or index >= len(self.__images)):
                if (self.__wrap_around):
                    index %= len(self.__images)
                else:
                    index = -1
        
            return index
            

    def get_index_at_and_relpos(self, y):
        """
        Returns the index of the item at the given position or -1 if there's no
        item at that position. Also returns, the per one percentage of the y position inside the row.
        """
        
        if (not self.__images or y > self.__totalsize):
            return -1, 0
        else:
            blocksize = self.__itemsize + self.__gapsize
            pos = self.__offset + y            
            index = (pos / blocksize)
            inside_y = (float(pos) / blocksize) - index
            
            if (index < 0 or index >= len(self.__images)):
                if (self.__wrap_around):
                    index %= len(self.__images)
                else:
                    index = -1
        
            return index, inside_y
            
            
    def swap(self, idx1, idx2):
        """
        Swaps the place of two images.
        """
        
        temp = self.__images[idx1]
        self.__images[idx1] = self.__images[idx2]
        self.__images[idx2] = temp
        #self.render()
        
        
    def get_current_index(self):
        """
        Returns the index of the currently selected image.
        """
    
        blocksize = self.__itemsize + self.__gapsize
        pos = self.__offset + self.__selection_offset + self.__itemsize / 2
        try:
            index = (pos / blocksize) % len(self.__images)
        except:
            index = 0
        
        return index
        
        
    def get_current_index_fraction(self):
    
        blocksize = self.__itemsize + self.__gapsize
        pos = self.__offset + self.__selection_offset
        fr = (pos / float(blocksize))
        fr = fr - int(fr)
        
        return fr
     
     
    def get_offset(self):
    
        return self.__offset
        
        
    def set_offset(self, offset):
    
        w, h = self.get_size()
        offset = min(offset, max(0, self.__totalsize - h))
        self.__offset = offset
        
        
    def __render_arrows(self):

        if (not self.may_render()): return

        x, y = self.get_screen_pos()
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

        if (not self.may_render()): return
        
        x, y = self.get_screen_pos()
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

        x, y = self.get_screen_pos()
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
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.__buffer
        
        try:        
            item = self.__images[self.__floating_index]
        except:
            return

        self.__shared_pmap.prepare(item)
        fw, fh = item.get_size()
        fx = x + (w - fw) / 2
        fy = y + self.__floating_position - fh / 2
        self.__buffer.draw_pixmap(self.__shared_pmap, fx, fy)


    def __render_buffered(self, screen, offset, height):

        x, y = self.get_screen_pos()
        w, h = self.get_size()

        TEMPORARY_PIXMAP.copy_pixmap(self.__buffer, x, y, x, y, w, h)

        if (self.__scrollbar_pmap):
            self.__render_scrollbar()
            
        if (self.__floating_index >= 0):
            self.__render_floating_item()

        if (self.__cap_top):
            cw, ch = self.__cap_top_size
            self.__buffer.draw_pixbuf(self.__cap_top, x, y, w, ch)
            
        if (self.__cap_bottom):
            cw, ch = self.__cap_bottom_size
            self.__buffer.draw_pixbuf(self.__cap_bottom, x, y + h - ch, w, ch)
            
        screen.copy_pixmap(self.__buffer, x, y + offset, x, y + offset, w, height)
        self.__buffer.copy_pixmap(TEMPORARY_PIXMAP, x, y, x, y, w, h)

        
    def render_this(self):

        w, h = self.get_size()
        screen = self.get_screen()
        self.__render_handler = None

        self.render_full()
        self.__render_buffered(screen, 0, h)
        
        
        
    def render_full(self):
        """
        Fully renders the widget.
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

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.__buffer

        # render items
        while (self.__images and render_offset < render_to):            
            idx = ((self.__offset + render_offset) / blocksize)

            # wrap around is not available when there are too few items
            if (self.__wrap_around and h < self.__totalsize):
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
                
        
    def move(self, nil, delta):
    
        #if (not self.__is_scrolling.isSet()):
        if (not self.__scroll_to_item_handler):
            self.__move(nil, delta)

        
        
    def __move(self, nil, delta):
        """
        Scrolls the image strip by the given positive or negative amount.
        """
                
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        if (not (self.__wrap_around and h < self.__totalsize)):
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

        if (self.__arrows[0]):
            self.__unrender_arrows()
            
        if (delta > 0):
            self.__buffer.move_area(x, y + delta, w, h - delta,
                                    0, -delta)
            self.__render(h - delta, delta)

        elif (delta < 0):
            self.__buffer.move_area(x, y, w, h - abs(delta),
                                    0, abs(delta))
            self.__render(0, abs(delta))
            
        if (self.__arrows[0]):
            self.__render_arrows()

        self.__render_buffered(screen, 0, h)


    def scroll_to_item(self, idx):
        """
        Scrolls to bring the given item into view.
        """

        w, h = self.get_size()

        
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
            
            #if (self.__totalsize > 2 * h):
            #    offset1 += h / 3
            #    offset2 -= h / 3
            
            offset3 = offset1 + self.__totalsize
            offset4 = offset2 + self.__totalsize


            if (offset1 <= self.__offset <= offset2 or 
                offset3 <= self.__offset <= offset4):
                self.__scroll_to_item_handler = None
                return False                
           
            # how far would we have to scroll up or down?
            distance1 = offset1 - self.__offset
            distance2 = offset2 - self.__offset
            if (self.__wrap_around):
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
            if (abs(distance) > 1000):
                self.__offset += distance / 5

            delta = distance / 10

            if (distance < 0):
                self.__move(0, max(-h, min(-1, delta)))
            elif (distance > 0):
                self.__move(0, min(h, max(1, delta)))
            else:
                self.__scroll_to_item_handler = None
                #self.__is_scrolling.clear()
                return False

            if (self.__offset == offset):
                # nothing moved
                self.__scroll_to_item_handler = None
                #self.__is_scrolling.clear()
                return False
                
            #print offset, offset1, offset2, self.__totalsize, distance, distances

            return True

        self.__scroll_to_item_index = idx
        if (not self.__scroll_to_item_handler):
            self.__scroll_to_item_handler = gobject.timeout_add(5, f)



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

        slider_width, nil = self.__scrollbar_pmap.get_size()
        slider_width /= 2
        w -= slider_width

        buf = Pixmap(None, w, h) #x + w, y + h)
        self.render_at(buf)
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
        while (wait and not finished.isSet()): gtk.main_iteration()
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
            import theme
            screen.copy_pixmap(screen, x + STEP, y, x, y, w - i, h)
            screen.draw_subpixbuf(theme.background, x + w - i, y, x + w - i, y,
                                  STEP, h)
            #screen.copy_pixmap(buf, x + w - i - 4, y, x, y, 4, h)
            if (i < w):
                gobject.timeout_add(5, f, i + STEP)
            else:
                finished.set()

        f(0)
        while (wait and not finished.isSet()): gtk.main_iteration()

