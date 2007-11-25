from utils.Observable import Observable

import gtk
import pango
import gobject
import os
import time
import gc


# predefined zoom levels
_ZOOM_LEVELS = [18, 25, 33, 50, 75, 100, 150, 200,
                300, 400, 600, 800, 1200, 1600]

# the maemo platform uses 16 bits per pixel
_BPP = gtk.gdk.get_default_root_window().get_depth()

# read this many bytes at once
_CHUNK_SIZE = 50000

_BACKGROUND_COLOR = gtk.gdk.color_parse("#101010")

# the font for comments, etc.
_FONT = "Nokia Sans Cn 22"



class Image(gtk.EventBox, Observable):
    """
    Class for rendering images.
    """    

    OBS_BEGIN_LOADING = 0
    OBS_END_LOADING = 1
    OBS_PROGRESS = 2
    OBS_RENDERED = 3
    OBS_ZOOMING = 4
    OBS_SCALE_RANGE = 5
    OBS_SMOOTHING = 6  
    

    def __init__(self):

        # the buffer contains the pixbuf for rendering on screen
        self.__buffer = None

        # original size of the image
        self.__original_size = (0, 0)

        # the visible size is the size of the image widget
        self.__visible_size = (0, 0)

        # the virtual size is the size of whole image zoomed
        self.__virtual_size = (0, 0)

        # center is the point on the virtual area that is in the
        # center of the visible area
        self.__center_pos = (0, 0)

        # the previous offset allows us to determine what to render
        # new and what to simply copy
        self.__previous_offset = (0, 0)

        # render completely new when this flag is set, e.g. after zooming
        self.__invalidated = False

        # save-under buffers (for rendering icons, etc)
        # a buffer is a tuple (pixmap, x, y, w, h)
        self.__save_unders = []

        # the currently available zoom levels (= _ZOOM_LEVELS + fitting)
        self.__zoom_levels = []
        self.__zoom_level = 4
        self.__zoom_value = 1.0
        self.__zoom_fit = 0
        self.__zoom_100 = 0

        self.__timer_tstamp = 0
        self.__current_filename = ""
        self.__banner = None

        # the loader contains the complete image
        self.__loader = None
        self.__loading_cancelled = False
        self.__pixbuf = None

        
        gtk.EventBox.__init__(self)
        #self.set_flags(gtk.CAN_FOCUS)
        self.connect("expose-event", self.__on_expose)

        self.__image = gtk.Image()
        self.__image.modify_font(pango.FontDescription(_FONT))
        self.__image.show()
        self.add(self.__image)

        # create a server-side pixmap for rendering
        #pmap = gtk.gdk.Pixmap(None, 800, 480, _BPP)
        #pmap.draw_rectangle(pmap.new_gc(), True, 0, 0, 800, 480)
        #self.__image.set_from_pixmap(pmap, None)
        #del pmap
        self.__make_pixmap(600, 400)

        # create a client-side pixmap for rendering
        self.__buffer = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,
                                       True, 8, 800, 480)


    def __make_pixmap(self, w, h):

        # create a server-side pixmap for rendering
        pmap = gtk.gdk.Pixmap(None, w, h, _BPP)
        pmap.draw_rectangle(pmap.new_gc(), True, 0, 0, w, h)
        self.__image.set_from_pixmap(pmap, None)
        del pmap


    def __on_expose(self, src, ev):

        self.resize()


    def resize(self, attempt = 0):
        """
        Checks if the widget has been resized.
        """

        w, h = self.window.get_size()
        if ((w, h) != self.__visible_size):
            self.__make_pixmap(w, h)        
            self.__visible_size = (w, h)
            #if (self.__original_size != (0, 0)): self.__scale_to_fit()
            if (self.__original_size != (0, 0)): self.zoom(self.__zoom_level)

        elif (attempt < 10):
            gobject.timeout_add(100, self.resize, attempt + 1)
        



    def __hi_quality_render(self):

        tstamp = int(time.time() * 1000)
        self.__timer_tstamp = tstamp
        gobject.timeout_add(1000, self.__hi_quality_timer, tstamp)


    def __hi_quality_timer(self, tstamp):

        if (tstamp != self.__timer_tstamp): return

        self.update_observer(self.OBS_SMOOTHING)
        self.__invalidated = True
        gobject.idle_add(self._render, True)


    def scroll_to(self, x, y):

        width, height = self.__visible_size
        vwidth, vheight = self.__virtual_size
        x = max(width / 2, min(x, vwidth - width / 2))
        y = max(height / 2, min(y, vheight - height / 2))
        self.__center_pos = (x, y)

        gobject.idle_add(self._render, False)


    def scroll_by(self, dx, dy):

        cx, cy = self.__center_pos
        self.scroll_to(cx + dx, cy + dy)


    def move(self, dx, dy):        
    
        self.scroll_by(dx, dy)


    def __get_offset(self):
        """
        Returns the required offset coordinates for the
        current center.
        """

        cx, cy = self.__center_pos
        width, height = self.__visible_size
        vwidth, vheight = self.__virtual_size

        offx = max(0, min(cx - width / 2, vwidth - width))
        offy = max(0, min(cy - height / 2, vheight - height))

        return (int(offx), int(offy))


    def zoom_fit(self):

        self.zoom(self.__zoom_fit)


    def zoom_100(self):

        self.zoom(self.__zoom_100)


    def zoom_in(self):

        self.zoom(self.__zoom_level + 1)


    def zoom_out(self):
        
        self.zoom(self.__zoom_level - 1)


    def zoom(self, level):

        cx, cy = self.__center_pos
        cx /= self.__zoom_value
        cy /= self.__zoom_value
        
        self.__zoom_level = max(0, min(len(self.__zoom_levels) - 1, level))
        self.__zoom_value = self.__zoom_levels[self.__zoom_level] / 100.0
        
        bufwidth, bufheight = self.__original_size
        self.__virtual_size = (int(bufwidth * self.__zoom_value),
                               int(bufheight * self.__zoom_value))

        for i in range(3): gc.collect()
        self.__invalidated = True

        self.update_observer(self.OBS_ZOOMING,
                             self.__zoom_level, self.__zoom_value)
        self.scroll_to(cx * self.__zoom_value, cy * self.__zoom_value)
        #gobject.timeout_add(0, self.scroll_to, cx * self.__zoom_value,
        #                                       cy * self.__zoom_value)


    def __push_save_under(self, x, y, w, h):
        """
        Saves the given area so that it can be restored later.
        """

        # it's all happening on the server-side, maybe even hw-accelerated
        pmap, nil = self.__image.get_pixmap()
        saved = gtk.gdk.Pixmap(None, w, h, _BPP)
        saved.draw_drawable(pmap.new_gc(), pmap,
                            x, y, 0, 0, w, h)
        self.__save_unders.append((saved, x, y, w, h))


    def __pop_save_under(self):
        """
        Restores a saved area.
        """

        # it's all happening on the server-side, maybe even hw-accelerated
        pmap, nil = self.__image.get_pixmap()
        if (self.__save_unders):
            saved, x, y, w, h = self.__save_unders.pop()
            pmap.draw_drawable(pmap.new_gc(), saved,
                               0, 0, x, y, w, h)



    def _render_text(self, text, posx, posy, draw_box):
        """
        Renders the given text on screen. The position is
        a percentage value of the widget size.
        """

        w, h = self.__visible_size

        context = self.__image.get_pango_context()
        layout = pango.Layout(context)
        layout.set_width(w * pango.SCALE)
        layout.set_text(text)

        layout_w, layout_h = layout.get_pixel_size()
        x = layout_w / 2 + int((w - layout_w) * posx - layout_w / 2)
        y = layout_h / 2 + int((h - layout_h) * posy - layout_h / 2)

        self.__push_save_under(x - 3, y - 3, layout_w + 6, layout_h + 6)

        pmap, nil = self.__image.get_pixmap()
        gc = pmap.new_gc()
        gc.set_foreground(self.__image.get_colormap().alloc_color("black"))

        if (draw_box):
            pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,
                                  True, 8, layout_w + 4, layout_h + 4)
            pbuf.fill(0xffffffa0)
            pmap.draw_pixbuf(None, pbuf, 0, 0, x - 2, y - 2, layout_w + 4, layout_h + 4,
                             gtk.gdk.RGB_DITHER_NONE, 0, 0)
            del pbuf
            pmap.draw_rectangle(gc, False, x - 3, y - 3, layout_w + 5, layout_h + 5)
        
        pmap.draw_layout(gc, x, y, layout, gtk.gdk.color_parse("black"))

        # only redraw the affected portion of the screen
        self.__image.queue_draw_area(x - 3, y - 3, layout_w + 6, layout_h + 6)


    def _render_bar(self, posy1, posy2):
        """
        Renders a colored bar on screen at the given position.
        The position is a percentage value of the widget size.
        """

        w, h = self.__visible_size
        y1 = int(h * posy1)
        y2 = int(h * posy2)
        height = abs(y1 - y2)

        pmap, nil = self.__image.get_pixmap()
        pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,
                              True, 8, w, height)
        pbuf.fill(0xffffffa0)
        pmap.draw_pixbuf(None, pbuf, 0, 0, 0, y1, w, height,
                         gtk.gdk.RGB_DITHER_NONE, 0, 0)
        del pbuf

        # only redraw the affected portion of the screen
        self.__image.queue_draw_area(0, y1, w, height)

        

    def _render_icon(self, icon, posx, posy):
        """
        Renders the given icon on screen. The position is
        a percentage value of the widget size.
        """

        w, h = self.__visible_size
        icon_w = icon.get_width()
        icon_h = icon.get_height()
        x = icon_w / 2 + int((w - icon_w) * posx - icon_w / 2)
        y = icon_h / 2 + int((h - icon_h) * posy - icon_h / 2)

        self.__push_save_under(x, y, icon_w, icon_h)

        pmap, nil = self.__image.get_pixmap()
        pmap.draw_pixbuf(None, icon,
                         0, 0, x, y, icon_w, icon_h,
                         gtk.gdk.RGB_DITHER_NONE, 0, 0)

        # only redraw the affected portion of the screen
        self.__image.queue_draw_area(x, y, icon_w, icon_h)


    def _render_clear(self):

        while (self.__save_unders):
            self.__pop_save_under()
        

    def _render(self, high_quality = False):
        """
        Renders the visible area of the image.
        """

        offx, offy = self.__get_offset()
        width, height = self.__visible_size
        vwidth, vheight = self.__virtual_size

        # find the area that can be copied (reused) and doesn't have to
        # be rendered again, and find the areas which have to be rendered
        prev_x, prev_y = self.__previous_offset
        dx = offx - prev_x
        dy = offy - prev_y

        areas = []
        if (dx >= 0):
            src_x = dx
            dest_x = 0
            src_w = width - dx
            areas.append((width - dx, 0, dx, height))
        elif (dx < 0):
            src_x = 0
            dest_x = -dx
            src_w = width + dx
            areas.append((0, 0, -dx, height))
        if (dy >= 0):
            src_y = dy
            dest_y = 0
            src_h = height - dy
            areas.append((0, height - dy, width, dy))
        elif (dy < 0):
            src_y = 0
            dest_y = -dy
            src_h = height + dy
            areas.append((0, 0, width, -dy))

        self._render_clear()

        pmap, nil = self.__image.get_pixmap()
        if (self.__invalidated):
            # draw full area
            areas = [(0, 0, width, height)]
            self.__invalidated = False
            
            if (vwidth < width or vheight < height):
                gc = pmap.new_gc()
                gc.set_foreground(_BACKGROUND_COLOR)
                pmap.draw_rectangle(gc, True, 0, 0, width, height)
                
        else:
            # copy on the server-side (this is our simple trick for
            # fast scrolling!)
            pmap.draw_drawable(pmap.new_gc(), pmap,
                               src_x, src_y, dest_x, dest_y, src_w, src_h)
            
        # render borders
        for rx, ry, rw, rh in areas:
            self.__render_area(rx, ry, rw, rh, high_quality)

        self.__previous_offset = (offx, offy)
        
        self.update_observer(self.OBS_RENDERED)
        self.__image.queue_draw()
        if (not high_quality): self.__hi_quality_render()

        

    def __render_area(self, rx, ry, rw, rh, high_quality = False):
        """
        Renders the given area. The coordinates are given in
        screen coordinates.
        """

        if (rw <= 0 or rh <= 0): return
        rx = max(0, rx)
        ry = max(0, ry)
        #print "RENDER", rx, ry, rw, rh

        offx, offy = self.__get_offset()
        width, height = self.__visible_size
        vwidth, vheight = self.__virtual_size

        offx += rx
        offy += ry
        
        destwidth = int(min(rw, vwidth - offx))
        destheight = int(min(rh, vheight - offy))       

        # determine interpolation type
        if (high_quality): interp = gtk.gdk.INTERP_BILINEAR
        else: interp = gtk.gdk.INTERP_NEAREST

        pbuf = self.__pixbuf# self.__loader.get_pixbuf()
        if (not pbuf): return

        destpbuf = self.__buffer.subpixbuf(rx, ry, destwidth, destheight)

        if (abs(self.__zoom_value - 1.0) < 0.0001):
            # for zoom = 100% we simply copy the area
            pbuf.copy_area(offx, offy, destwidth, destheight,
                           destpbuf,
                           0, 0)
        else:
            pbuf.scale(destpbuf,
                       0, 0, destwidth, destheight,
                       -offx, -offy,
                       self.__zoom_value, self.__zoom_value,
                       interp)

        # copy from client-side pixmap to server-side pixmap
        # I wish we could avoid this time-consuming step... (server-side
        # scaling would be nice!)
        pmap, nil = self.__image.get_pixmap()

        # maybe we have to center the image?
        if (vwidth < width or vheight < height):
            if (vwidth < width): rx += (width - vwidth) / 2
            if (vheight < height): ry += (height - vheight) / 2
        
        pmap.draw_pixbuf(None, destpbuf,
                         0, 0, rx, ry, destwidth, destheight,
                         gtk.gdk.RGB_DITHER_NONE, 0, 0)
        



    def load(self, filename):
        """
        Loads the given image file. If we're currently loading another
        image, cancel the loading first.
        """

        if (filename != self.__current_filename):
            self.__loading_cancelled = True
            self.update_observer(self.OBS_BEGIN_LOADING, filename)
            
            # timeout for the cancelation to take effect
            gobject.timeout_add(50, self.__load_img, filename)



    def __load_img(self, filename):
        """
        Loads the image while allowing user interaction.
        """

        if (self.__banner):
            self.__banner.close()

        if (not os.path.exists(filename)):
            filename = "" #pixmaps.get_path("image-missing.png")

        try:
            self.__loader.close()
        except:
            pass
        self.__loader = gtk.gdk.PixbufLoader()
        self.__loader.connect("size-prepared", self.__on_check_size)
        fd = open(filename, "r")
        # determine file size
        fd.seek(0, 2)
        size = fd.tell()
        fd.seek(0)

        # collect three generations of garbage
        for i in range(3): gc.collect()

        #self.__banner = ProgressBanner(self,
        #                "%s" % os.path.basename(filename), size)
        self.__loading_cancelled = False
        self.__current_filename = filename
        
        size_read = 0
        while (True and size > 0):
            data = fd.read(_CHUNK_SIZE)
            size_read += len(data)
            
            # this runs the gtk mainiteration and thus allows user interaction
            #if (self.__banner): self.__banner.progress(_CHUNK_SIZE)            

            self.update_observer(self.OBS_PROGRESS, size_read, size)
            while (gtk.events_pending()): gtk.main_iteration()

            if (self.__loading_cancelled):
                break
            
            if (data):
                if (self.__loader): self.__loader.write(data)
            else:
                break
        #end while

        fd.close()
        if (self.__loader):
            try:
                self.__loader.close()
            except:
                pass #hildon.hildon_banner_show_information(self, gtk.STOCK_DIALOG_ERROR,
                     #                                 "Not a valid image")
                self.__loading_cancelled = True

            if (not self.__loading_cancelled): self.__finish_loading()
            self.__loader = None

        if (self.__banner):
            self.__banner.close()
            self.__banner = None


            
        
    def __finish_loading(self):
        """
        Cleans up and displays the image.
        """

        #print "REF", self.__loader.__grefcount__

        pbuf = self.__loader.get_pixbuf()

        # automatically rotate images in portrait format
        if (pbuf.get_width() < pbuf.get_height()):
            try:
                # rotating is only supported by pygtk >= 2.10
                self.__pixbuf = pbuf.rotate_simple(
                    gtk.gdk.PIXBUF_ROTATE_CLOCKWISE)
            except:
                self.__pixbuf = pbuf
        else:
            self.__pixbuf = pbuf

        del pbuf

        w, h = self.__pixbuf.get_width(), self.__pixbuf.get_height()
        self.__original_size = (w, h)

        self.__scale_to_fit()

        # collect three generations of garbage
        for i in range(3): gc.collect()

        self.update_observer(self.OBS_END_LOADING)


    def __scale_to_fit(self):
        """
        Scales the image up or down to fit the screen.
        """

        orig_width, orig_height = self.__original_size
        w, h = orig_width, orig_height
        width, height = self.__visible_size
        fit_factor = 1
        fit_factor2 = 1

        if (w != width or h != height):
            factor1 = width / float(orig_width)
            factor2 = height / float(orig_height)
            fit_factor = min(factor1, factor2)
            fit_factor2 = max(factor1, factor2)
            
        fitting = int(fit_factor * 100)
        fitting2 = int(fit_factor2 * 100)

        self.__zoom_levels = _ZOOM_LEVELS[:]
        if (not fitting in self.__zoom_levels):
            self.__zoom_levels.append(fitting)
        if (not fitting2 in self.__zoom_levels):
            self.__zoom_levels.append(fitting2)
        self.__zoom_levels.sort()

        self.update_observer(self.OBS_SCALE_RANGE, len(self.__zoom_levels))
        self.__zoom_fit = self.__zoom_levels.index(fitting)
        self.__zoom_100 = self.__zoom_levels.index(100)
        self.zoom_fit()


    def __on_check_size(self, loader, width, height):
        """
        Resizes the image while loading if it's too large for
        the little device.
        """
        
        #print "%d megapixels" % ((width * height) / 1000000),
        # TODO: this is hardcoded for now. value could be made dependent
        #       on available RAM, or so
        factor = 1
        if (width > 1000 or height > 1000):
            factor1 = 1000 / float(width)
            factor2 = 1000 / float(height)
            factor = min(factor1, factor2)

        if (factor != 1):
            loader.set_size(int(width * factor), int(height * factor))
