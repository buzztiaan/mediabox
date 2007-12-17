import gtk
import gobject


_BPP = gtk.gdk.get_default_root_window().get_depth()


class ImageStrip(gtk.DrawingArea):
    """
    Class for rendering a scrollable strip of images.
    """

    def __init__(self, width, itemsize, gapsize):
    
        self.__pbuf_cache = {}
        self.__arrows = None
        self.__arrows_save_under = None
    
        gtk.DrawingArea.__init__(self)
        self.connect("expose-event", self.__on_expose)
        #self.set_double_buffered(False)
        self.set_size_request(width, -1)

        self.__images = []
        self.__bg = None
        self.__offset = 0
        self.__canvas = None
        self.__cmap = None
        self.__itemwidth = width
        self.__itemsize = itemsize
        self.__gapsize = gapsize
        self.__totalsize = 0
        
        self.__is_scrolling = False
        
        # the selection offset initially selects the item in the middle and
        # centers the view around it
        self.__selection_offset = 0 #(self.__height - self.__itemsize) / 2
        
        # whether we wrap around
        self.__wrap_around = True
        
        # whether to display a slider
        self.__show_slider = False

        
        def f():
            # retrieve canvas and gc once they're available
            if (not self.window):
                gobject.timeout_add(500, f)
                return
            else:
                self.__canvas = self.window
                self.__gc = self.__canvas.new_gc()
                self.__cmap = self.__canvas.get_colormap()
                gobject.timeout_add(100, self.render_full)
            
        gobject.idle_add(f)        
        
        
        
    def __on_expose(self, src, ev):
    
        self.render_full()
    
    
    def __to_pixbuf(self, obj):
    
        if (hasattr(obj, "add_alpha")):
            return obj
        else:
            return gtk.gdk.pixbuf_new_from_file(obj)

    
    
    def __create_pixbuf(self, filename):
    
        if (filename in self.__pbuf_cache):
            return self.__pbuf_cache[filename]
        else:
            try:
                pbuf = gtk.gdk.pixbuf_new_from_file(filename)
            except:
                pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 160, 120)
            self.__pbuf_cache[filename] = pbuf
            
            return pbuf
    
    
    def get_size(self):
    
        win = self.window
        if (win):
            return win.get_size()
        else:
            return (0, 0)
    
        
    def set_background(self, bg):
        """
        Sets the background image from the given pixbuf or filename.
        """
    
        self.__bg = self.__to_pixbuf(bg)
        
        
    def set_arrows(self, arrows):
        """
        Sets arrow graphics from the given pixbuf.
        """
    
        if (arrows):
            w, h = arrows.get_width(), arrows.get_height()
            h2 = h / 2
            arrow_up = arrows.subpixbuf(0, 0, w, h2)
            arrow_down = arrows.subpixbuf(0, h2, w, h2)
            self.__arrows = (arrow_up, arrow_down)
            
            pmap1 = gtk.gdk.Pixmap(None, w, h2, _BPP)
            pmap2 = gtk.gdk.Pixmap(None, w, h2, _BPP)
            self.__arrows_save_under = (pmap1, pmap2)
        else:
            self.__arrows = None


    def set_show_slider(self, value):
    
        self.__show_slider = value


    def get_image(self, idx):
    
        return self.__images[idx]
        
        
    def set_images(self, images):
        """
        Sets the list of images to be displayed by the image strip.
        It can either be a list of pixbufs or a list of filenames.
        """

        while (self.__images):
            img = self.__images.pop()
            del img  
            
        import gc; gc.collect()  

        self.__images = [ self.__to_pixbuf(f) for f in images ]                
        self.__totalsize = (self.__itemsize + self.__gapsize) * len(images)
        
        self.__offset = 0
        self.queue_draw()        
        
        
    def append_image(self, img):
    
        self.__images.append(self.__to_pixbuf(img))
        self.__totalsize = (self.__itemsize + self.__gapsize) * len(self.__images)
        self.queue_draw()
        
        return len(self.__images) - 1
                        
        
    def replace_image(self, idx, image):
    
       img = self.__images[idx]
       self.__images[idx] = self.__to_pixbuf(image)           
       del img
       self.queue_draw()       

       
       
    def remove_image(self, idx):
    
        del self.__images[idx]
        self.__totalsize = (self.__itemsize + self.__gapsize) * len(self.__images)        
        self.__offset = 0
        self.queue_draw()
        
        
    def overlay_image(self, idx, img, x, y):
    
        pbuf = self.__to_pixbuf(img)
        sub = self.__images[idx].subpixbuf(x, y,
                                           pbuf.get_width(), pbuf.get_height())
        pbuf.composite(sub, 0, 0, pbuf.get_width(), pbuf.get_height(),
                       0, 0, 1, 1,
                       gtk.gdk.INTERP_NEAREST, 0xff)
        self.queue_draw()
        
        
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
        Returns the index of the item at the given position.
        """
        
        if (not self.__images or y > self.__totalsize):
            return -1
        else:
            blocksize = self.__itemsize + self.__gapsize
            pos = self.__offset + y
            index = (pos / blocksize) % len(self.__images)
        
            return index
        
        
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
    
        if (not self.__canvas): return
    
        arrow_up, arrow_down = self.__arrows
        arrow_width, arrow_height = arrow_up.get_width(), arrow_up.get_height()
        w, h = self.get_size()
        
        pmap1, pmap2 = self.__arrows_save_under
        pmap1.draw_drawable(pmap1.new_gc(), self.__canvas,
                            (w - arrow_width) / 2, 0, 0, 0,
                            arrow_width, arrow_height)
        pmap2.draw_drawable(pmap2.new_gc(), self.__canvas,
                            (w - arrow_width) / 2, h - arrow_height, 0, 0,
                            arrow_width, arrow_height)

        if (self.__offset > 0):        
            self.__canvas.draw_pixbuf(self.__gc, arrow_up,
                                      0, 0, (w - arrow_width) / 2, 0,
                                      arrow_width, arrow_height)

        if (self.__offset < self.__totalsize - h):
            self.__canvas.draw_pixbuf(self.__gc, arrow_down,
                                  0, 0, (w - arrow_width) / 2, h - arrow_height,
                                      arrow_width, arrow_height)


    def __unrender_arrows(self):

        if (not self.__canvas): return
            
        arrow_up, arrow_down = self.__arrows
        arrow_width, arrow_height = arrow_up.get_width(), arrow_up.get_height()
        w, h = self.get_size()

        pmap1, pmap2 = self.__arrows_save_under
        self.__canvas.draw_drawable(self.__gc, pmap1,
                                    0, 0, (w - arrow_width) / 2, 0,
                                   arrow_width, arrow_height)
        self.__canvas.draw_drawable(self.__gc, pmap2,
                                  0, 0, (w - arrow_width) / 2, h - arrow_height,
                                    arrow_width, arrow_height)
        
        
    def __render_slider(self):
    
        w, h = self.get_size()
        if (self.__totalsize > 0):
            percent = self.__offset / float(self.__totalsize)
            slider_size = (h / float(self.__totalsize)) * h
        else:
            percent = 0
            slider_size = h


        y1 = int(h * percent)
        y2 = int(y1 + slider_size)

        if (False and self.__bg):
            self.__canvas.draw_pixbuf(self.__gc, self.__bg,
                                        w - 2, 0, w - 2, 0,
                                        2, y1)
            if (y2 < h):
                self.__canvas.draw_pixbuf(self.__gc, self.__bg,
                                          w - 2, y2, w - 2, y2,
                                          2, max(0, h - y2))
        #end if

        self.__gc.set_foreground(self.__cmap.alloc_color("#cccccc"))
        self.__canvas.draw_rectangle(self.__gc, True,
                                     w - 2, 0, 2, y1)
        self.__canvas.draw_rectangle(self.__gc, True,
                                     w - 2, y2, 2, h - y2)
        
        self.__gc.set_foreground(self.__cmap.alloc_color("#444444"))
        self.__canvas.draw_rectangle(self.__gc, True,
                                     w - 2, y1, 2, y2 - y1 + 1)

        
        
        
        
    def render_full(self):
        """
        Fully renders the widget.
        """
    
        w, h = self.get_size()
        self.__render(0, h)
        if (self.__arrows):
            self.__render_arrows()
        
        
        
    def __render(self, render_offset, render_height):
   
        if (not self.__canvas): return

        blocksize = self.__itemsize + self.__gapsize
        render_to = render_offset + render_height

        w, h = self.get_size()

        while (self.__images and render_offset < render_to):
            idx = ((self.__offset + render_offset) / blocksize)
            # wrap around is not available when there are too few items
            if (self.__wrap_around and h < self.__totalsize):
                idx %= len(self.__images)
            elif (idx >= len(self.__images) or idx < 0):
                break                            

            img_offset = (self.__offset + render_offset) % blocksize

            remain = min(self.__itemsize - img_offset, render_to - render_offset)

            if (remain > 0):
                pbuf = self.__images[idx]
                self.__canvas.draw_pixbuf(self.__gc, pbuf,
                                          0, img_offset, 0, render_offset,
                                          pbuf.get_width(), remain)

            render_offset += (remain + self.__gapsize)
        #end while

        if (self.__bg):
            if (render_offset < render_to):
                self.__canvas.draw_pixbuf(self.__gc, self.__bg,
                                          0, render_offset, 0, render_offset,
                                          w, render_to - render_offset)
        
            gap_offset = 0 - (self.__offset % blocksize) - self.__gapsize

            while (gap_offset < h):
                if (gap_offset + self.__gapsize < 0):
                    gap_offset += self.__gapsize + self.__itemsize
                    continue
                elif (gap_offset < 0):
                    render_offset = 0
                    remain = self.__gapsize - abs(gap_offset)
                else:
                    render_offset = gap_offset
                    remain = min(self.__gapsize, h - render_offset)
                    
                if (remain > 0):
                    self.__canvas.draw_pixbuf(self.__gc, self.__bg,
                                              0, render_offset, 0, render_offset,
                                              min(w, self.__bg.get_width()),
                                              min(remain, self.__bg.get_height()))

                gap_offset += blocksize
            #end while
        #end if
    
        if (self.__show_slider):
            self.__render_slider()
        
        
    def move(self, nil, delta):
        """
        Scrolls the image strip by the given positive or negative amount.
        """
                
        if (not self.__images): return
                        

        w, h = self.get_size()
        
        if (not (self.__wrap_around and h < self.__totalsize)):
            if (self.__offset + delta > self.__totalsize - h):
                #delta = self.__totalsize - self.__height - self.__offset
                return
            elif (self.__offset + delta < 0):
                #delta = self.__offset
                return
        #end if

        self.__offset += delta
        if (self.__offset < 0):
            self.__offset += self.__totalsize
        elif (self.__offset > self.__totalsize):
            self.__offset -= self.__totalsize
            
        if (not self.__canvas): return


        if (self.__arrows):
            self.__unrender_arrows()
            
        if (delta > 0):
            self.__canvas.draw_drawable(self.__gc, self.__canvas,
                                        0, delta, 0, 0,
                                        self.__itemwidth, h - delta)

            self.__render(h - delta, delta)

        elif (delta < 0):
            self.__canvas.draw_drawable(self.__gc, self.__canvas,
                                        0, 0, 0, abs(delta),
                                        self.__itemwidth, h - abs(delta))
                                        
            self.__render(0, abs(delta))
            
        if (self.__arrows):
            self.__render_arrows()



    def scroll_to_item(self, idx):
        """
        Scrolls to bring the given item into view.
        """
        
        def f(idx):
            w, h = self.get_size()
        
            # offset must be between these values to make the item visible
            offset2 = (self.__itemsize + self.__gapsize) * idx
            offset1 = offset2 - (h - self.__itemsize)          

            if (self.__offset < offset1):
                self.move(0, 10)
            elif (self.__offset > offset2):
                self.move(0, -10)
            else:
                self.__is_scrolling = False
                return False

            return True

                        
        if (not self.__is_scrolling):
            self.__is_scrolling = True
            gobject.timeout_add(5, f, idx)
