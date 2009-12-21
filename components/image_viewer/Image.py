from ui.Widget import Widget
from ui.Pixmap import Pixmap, TEMPORARY_PIXMAP
from io.Downloader import Downloader
from utils.Observable import Observable
from utils import logging

import gtk
import pango
import gobject
import os
import time
import gc



# predefined zoom levels
_ZOOM_LEVELS = [12, 15, 18, 22, 25, 31, 36, 43, 50, 63, 75, 88, 100,
                125, 150, 175, 200, 250, 300, 350, 400, 500, 600,
                700, 800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200]

# read this many bytes at once
_CHUNK_SIZE = 50000



class Image(Widget, Observable):
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

        # client-side buffer for scaling
        self.__buffer = None
        
        # color of the background
        self.__bg_color = "#000000"
        
        # offscreen drawing pixmap
        self.__offscreen = Pixmap(None, gtk.gdk.screen_width(),
                                        gtk.gdk.screen_height())

        # original size of the image
        self.__original_size = (0, 0)

        # the visible size is the size of the image widget
        self.__visible_size = (100, 100)

        # the virtual size is the size of whole image zoomed
        self.__virtual_size = (0, 0)

        # center is the point on the virtual area that is in the
        # center of the visible area
        self.__center_pos = (0, 0)

        # the previous offset allows us to determine what to render
        # new and what to simply copy
        self.__previous_offset = (0, 0)

        # render completely new when this flag is set, e.g. after zooming
        self.__invalidated = True

        # flag for marking new images that have not been rendered to screen yet
        self.__is_new_image = False
               
        self.__hi_quality_timer = None
        
        # the currently available zoom levels (= _ZOOM_LEVELS + fitting)
        self.__zoom_levels = []
        self.__zoom_level = 4
        self.__zoom_value = 1.0
        self.__zoom_fit = 0
        self.__zoom_100 = 0

        self.__current_file = ""

        # the loader contains the complete image
        self.__loader = None
        self.__is_loading = False
        self.__is_preloading = False
        self.__currently_loading = None
        self.__pixbuf = None
        
        # flag for aborting the load process if it would cause trouble
        self.__loading_aborted = False
        
        # preloaded pixbuf
        self.__preloaded_pixbuf = None
        # preloaded file
        self.__preloaded_file = None
        
        # handler for scheduling the preloader
        self.__scheduled_preloader = None
        
        # slide from right or left
        self.__slide_from_right = True
        
        # progress percentage value
        self.__progress = 0
        
        # amount by which the image is dragged
        self.__drag_amount = 0
        
        # rendering overlays
        self.__overlays = []        
        
        Widget.__init__(self)
        
        # create a client-side pixmap for scaling
        self.__buffer = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,
                                       True, 8,
                                       gtk.gdk.screen_width(),
                                       gtk.gdk.screen_height())


    def add_overlay(self, overlay):
        
        self.__overlays.append(overlay)


    def __copy_image_buffer(self, buf1, buf2):

        x, y = self.get_screen_pos()
        w, h = self.get_size()

        if (self.__drag_amount >= 0):
            src_x = x
            dst_x = x + self.__drag_amount
            dst_w = w - self.__drag_amount
            if (self.__drag_amount != 0):
                buf2.fill_area(x, y, self.__drag_amount, h, self.__bg_color)
        else:
            src_x = x - self.__drag_amount
            dst_x = x
            dst_w = w + self.__drag_amount
            buf2.fill_area(x + dst_w, y, abs(self.__drag_amount), h, self.__bg_color)

        buf2.copy_pixmap(buf1, src_x, y, dst_x, y, dst_w, h)
    
        


    def render_this(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        if (self.__progress): h -= 16
        screen = self.get_screen()
        if (self.__invalidated):
            self._render()
        else:
            self.__copy_image_buffer(self.__offscreen, screen)
        

    def set_size(self, w, h):
    
        Widget.set_size(self, w, h)

        if ((w, h) != self.__visible_size):
            self.__visible_size = (w, h)
            if (self.__original_size != (0, 0)):
                self.__invalidated = True
                self.__offscreen = Pixmap(None, w, h)
                self.__buffer = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,
                                               True, 8, w, h)
                self._render()
                self.__scale_to_fit()
                #gobject.idle_add(self.__scale_to_fit)


    def set_background(self, col):
    
        self.__bg_color = col
        self.__invalidated = True
        #self.__offscreen.fill_area(0, 0, 800, 480, self.__bg_color)
        

    def __hi_quality_render(self):

       self.update_observer(self.OBS_SMOOTHING)
       self.__invalidated = True
       self._render(True)


    def scroll_to(self, x, y):

        width, height = self.__visible_size
        vwidth, vheight = self.__virtual_size
        x = max(width / 2, min(x, vwidth - width / 2))
        y = max(height / 2, min(y, vheight - height / 2))
        self.__center_pos = (x, y)

        self._render(False)
        #gobject.idle_add(self._render, False)


    def scroll_by(self, dx, dy):

        cx, cy = self.__center_pos
        self.scroll_to(cx + dx, cy + dy)


    def move(self, dx, dy):        
    
        self.scroll_by(dx, dy)
        return (dx, dy)


    def set_drag_amount(self, amount):
    
        self.__drag_amount = amount
        self.render()
        

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


    def is_image_fitting(self):
        """
        Returns whether the image fits the screen (True) or has to be
        scrolled (False).
        """

        w, h = self.get_size()
        virtual_w, virtual_h = self.__virtual_size
        
        return (virtual_w <= w and virtual_h <= h)


    def zoom_fit(self, animated = True):

        if (animated):
            self.__zoom_animated(self.__zoom_fit)
        else:
            self.zoom(self.__zoom_fit)


    def zoom_100(self, animated = True):

        if (animated):
            self.__zoom_animated(self.__zoom_100)
        else:
            self.zoom(self.__zoom_100)


    def zoom_in(self, animated = True):

        if (animated):
            self.__zoom_animated(self.__zoom_level + 1)
        else:
            self.zoom(self.__zoom_level + 1)


    def zoom_out(self, animated = True):

        if (animated):        
            self.__zoom_animated(self.__zoom_level - 1)
        else:
            self.zoom(self.__zoom_level - 1)
        

    def zoom(self, level, zoom_value = 0):

        if (not self.__zoom_levels): return

        cx, cy = self.__center_pos
        cx /= self.__zoom_value
        cy /= self.__zoom_value
        
        if (not zoom_value):
            self.__zoom_level = max(0, min(len(self.__zoom_levels) - 1, level))
            self.__zoom_value = self.__zoom_levels[self.__zoom_level] / 100.0
        else:
            for i in range(len(self.__zoom_levels)):
                zl = self.__zoom_levels[i]
                if (zl > zoom_value):
                    self.__zoom_level = i
                    break
            #end for
            self.__zoom_value = zoom_value
        
        bufwidth, bufheight = self.__original_size
        self.__virtual_size = (int(bufwidth * self.__zoom_value),
                               int(bufheight * self.__zoom_value))

        #for i in range(3): gc.collect()
        self.__invalidated = True

        self.update_observer(self.OBS_ZOOMING,
                             self.__zoom_level, self.__zoom_value)
        self.scroll_to(cx * self.__zoom_value, cy * self.__zoom_value)
        #gobject.timeout_add(0, self.scroll_to, cx * self.__zoom_value,
        #                                       cy * self.__zoom_value)
          
      
    def __zoom_animated(self, level):
    
        def f(params):
            from_value, to_value = params
            dv = (to_value - from_value) / 3

            if (abs(dv) > 0.01):
                self.zoom(0, from_value + dv)
                params[0] = from_value + dv                
                return True
            else:
                self.zoom(0, to_value)
                return False
    
        level = max(0, min(len(self.__zoom_levels) - 1, level))
        from_value = self.__zoom_value
        to_value = self.__zoom_levels[level] / 100.0
        
        self.animate(25, f, [from_value, to_value])
        self.__zoom_level = level
        
      

    def _render(self, high_quality = False):
        """
        Renders the visible area of the image.
        """

        x, y = self.get_screen_pos()
        screen = self.get_screen()

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

        #self._render_clear()

        if (self.__invalidated):
            # draw full area
            areas = [(0, 0, width, height)]
            self.__invalidated = False
            
            if (vwidth + 1 < width):
                bw = (width - vwidth) / 2
                self.__offscreen.fill_area(x, y, bw, height, self.__bg_color)
                self.__offscreen.fill_area(x + width - bw - 1, y, bw + 1, height,
                                           self.__bg_color)
            
            if (vheight + 1 < height):
                bh = (height - vheight) / 2
                self.__offscreen.fill_area(x, y, width, bh, self.__bg_color)
                self.__offscreen.fill_area(x, y + height - bh - 1, width, bh + 1,
                                           self.__bg_color)
                
        else:
            # copy on the server-side (this is our simple trick for
            # fast scrolling!)
            self.__offscreen.move_area(x + src_x, y + src_y, src_w, src_h,
                                       -dx, -dy)
            
        # render borders
        for rx, ry, rw, rh in areas:
            self.__render_area(rx, ry, rw, rh, high_quality)

        # copy to screen
        if (self.may_render()):
            if (self.__is_new_image):
                self.__is_new_image = False
                self.fx_slide_in()
            #else:
            #    screen.copy_pixmap(self.__offscreen, x, y, x, y, width, height)            
            
            if (not high_quality):
                if (self.__hi_quality_timer):
                    gobject.source_remove(self.__hi_quality_timer)
                    
                self.__hi_quality_timer = \
                  gobject.timeout_add(1000, self.__hi_quality_render)
            else:
                self.__hi_quality_timer = None

        self.__previous_offset = (offx, offy)
        
        #self.render()
        if (self.may_render()):
            self.render_at(TEMPORARY_PIXMAP, x, y)
            for o in self.__overlays:
                o(TEMPORARY_PIXMAP, x, y, width, height)
            screen.copy_pixmap(TEMPORARY_PIXMAP, x, y, x, y, width, height)
            self.update_observer(self.OBS_RENDERED)


        

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

        # maybe we have to center the image?
        if (vwidth < width or vheight < height):
            if (vwidth < width): rx += (width - vwidth) / 2
            if (vheight < height): ry += (height - vheight) / 2

        x, y = self.get_screen_pos()
        self.__offscreen.draw_pixbuf(destpbuf, x + rx, y + ry)        
       



    def load(self, f):
        """
        Loads the given image file.
        """
        
        if (f != self.__current_file):        
            if (self.__hi_quality_timer):
                gobject.source_remove(self.__hi_quality_timer)
            
            if (self.__scheduled_preloader):
                gobject.source_remove(self.__scheduled_preloader)
                self.__scheduled_preloader = None
            
            self.__current_file = f
            
            # case 1: image is not preloaded
            #         simply load image, cancelling any running load operation
            if (self.__preloaded_file != f):
                logging.debug("preloading image %s", f)
                self.__is_preloading = False
                self.__load_img(f, self.__use_pixbuf)
                
            # case 2: image is currently being preloaded
            #         make the remaining preloading process visible
            elif (not self.__preloaded_pixbuf):
                logging.debug("using preloading image %s", f)
                self.update_observer(self.OBS_BEGIN_LOADING)
                self.__is_preloading = False
                
            # case 3: image is already preloaded and can be used
            #         use image
            elif (self.__preloaded_pixbuf):
                logging.debug("using preloaded image %s", f)
                self.update_observer(self.OBS_BEGIN_LOADING)
                self.__drag_amount = 0
                self.__use_pixbuf(self.__preloaded_pixbuf)
                self.update_observer(self.OBS_END_LOADING)

            # TODO: there's still one bug:
            #       when cancelling loading of a file and reloading the same
            #       file again before the cancelled loader didn't terminate,
            #       the cancelled loader becomes active again and closes the
            #       pixbuf loader before the new loader finished writing to it
            #
            #       this does not apply to normal use-cases, though

            # disable preloaded stuff
            self.__preloaded_pixbuf = None
            self.__preloaded_file = None



    def preload(self, f):
        """
        Preloads the given image file.
        """

        def on_load(pixbuf):
            if (self.__is_preloading):
                self.__preloaded_pixbuf = pixbuf
            else:
                self.__use_pixbuf(pixbuf)


        if (f != self.__current_file):
            # case 1: nothing is loading at the moment
            #         simply load
            if (not self.__is_loading):
                logging.debug("preloading image %s", f)
                self.__preloaded_file = f
                self.__is_preloading = True
                self.__scheduled_preloader = None
                self.__load_img(f, on_load)
                
            # case 2: something is loading
            #         schedule preloader for later
            else:
                logging.debug("preloading image %s later", f)
                self.__scheduled_preloader = gobject.timeout_add(500,
                                                               self.preload, f)


    def __load_img(self, f, cb, *args):
        """
        Loads the image.
        """

        def on_data(d, amount, total, size_read, f):
            if (f != self.__currently_loading): return
            if (d):
                size_read[0] += len(d)
                try:
                    if (not self.__loading_aborted):
                        self.__loader.write(d)
                except:
                    pass
                    
                if (not self.__is_preloading):
                    self.__progress = size_read[0] / float(total) * 100
                    self.render()
                    self.update_observer(self.OBS_PROGRESS, size_read[0], total)
            else:
                try:
                    self.__loader.close()
                    pixbuf = self.__finish_loading()
                    cb(pixbuf, *args)
                except:
                    pass
                    
                self.__progress = 0
                if (not self.__is_preloading):
                    self.__drag_amount = 0
                    self.render()
                    self.update_observer(self.OBS_END_LOADING)

                self.__is_loading = False


        self.__currently_loading = f
        self.__is_loading = True
        self.__loading_aborted = False
        try:
            self.__loader.close()
        except:
            pass
        self.__loader = gtk.gdk.PixbufLoader()
        self.__loader.connect("size-prepared", self.__on_check_size)

        if (not self.__is_preloading):
            self.update_observer(self.OBS_BEGIN_LOADING, f)

        try:
            f.load(0, on_data, [0], f)
        except:
            if (not self.__is_preloading):
                self.update_observer(self.OBS_END_LOADING)

            self.__is_loading = False
                           
        
    def __finish_loading(self):
        """
        Cleans up and displays the image.
        """

        #print "REF", self.__loader.__grefcount__

        pbuf = self.__loader.get_pixbuf()
        
        # properly support images with alpha channel
        if (pbuf.get_has_alpha()):
            pbuf2 = pbuf.composite_color_simple(pbuf.get_width(),
                                                pbuf.get_height(),
                                                gtk.gdk.INTERP_NEAREST, 0xff,
                                                32, 0, 0)
            del pbuf
            pbuf = pbuf2
            del pbuf2
        #end if
            

        # automatically rotate images in portrait format
        w, h = self.get_size()
        if (w > h and pbuf.get_width() < pbuf.get_height() or
            w < h and pbuf.get_width() > pbuf.get_height()):
            try:
                # rotating is only supported by pygtk >= 2.10
                pixbuf = pbuf.rotate_simple(
                    gtk.gdk.PIXBUF_ROTATE_CLOCKWISE)
            except:
                pixbuf = pbuf
        else:
            pixbuf = pbuf

        del pbuf        


        return pixbuf
        

        # collect three generations of garbage
        #for i in range(3): gc.collect()


    def __use_pixbuf(self, pbuf):
        
        self.__pixbuf = pbuf
        w, h = self.__pixbuf.get_width(), self.__pixbuf.get_height()
        self.__original_size = (w, h)
    
        self.__is_new_image = True
        self.__scale_to_fit()
                
        del pbuf


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
        self.zoom_fit(animated = False)


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

        if (width * height > 8000000):
            logging.info("aborted loading image because resolution is"
                         " too high: %dx%d, %0.2f megapixels",
                         width, height, width * height / 1000000.0)
            self.__loading_aborted = True


        if (factor != 1):
            loader.set_size(int(width * factor), int(height * factor))
      
        
    def slide_from_left(self):
    
        self.__slide_from_right = False
                
        
    def slide_from_right(self):
    
        self.__slide_from_right = True
        
        
    def fx_slide_in(self, wait = True):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        if (self.__slide_from_right):
            self.fx_slide_horizontal(self.__offscreen, x, y, w, h,
                                     self.SLIDE_LEFT)
        else:
            self.fx_slide_horizontal(self.__offscreen, x, y, w, h,
                                     self.SLIDE_RIGHT)
        
        
        """
        def f(params):
            from_x, to_x = params
            dx = (to_x - from_x) / 5
            done = False

            if (dx > 0):
                pass
            else:
                dx = to_x - from_x
                done = True

            if (self.__slide_from_right):
                screen.move_area(x + dx, y, w - dx, h, -dx, 0)
                screen.copy_pixmap(self.__offscreen,
                                   x + from_x, y,
                                   x + w - dx, y,
                                   dx, h)
            else:
                screen.move_area(x, y, w - dx, h, dx, 0)
                screen.copy_pixmap(self.__offscreen,
                                   x + w - from_x - dx, y,
                                   x, y,
                                   dx, h)

            if (not done):
                params[0] = from_x + dx
                params[1] = to_x
                return True

            else:
                return False

        self.animate(50, f, [0, w])
        """
