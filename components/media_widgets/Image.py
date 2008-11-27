from ui.Widget import Widget
from ui.Pixmap import Pixmap, TEMPORARY_PIXMAP
from io.Downloader import Downloader
from utils.Observable import Observable

import gtk
import pango
import gobject
import os
import time
import gc



# predefined zoom levels
_ZOOM_LEVELS = [18, 25, 33, 50, 75, 100, 150, 200,
                300, 400, 600, 800, 1200, 1600, 2400, 3200]

# read this many bytes at once
_CHUNK_SIZE = 50000

# the font for comments, etc.
_FONT = "Nokia Sans Cn 22"



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

        # the buffer contains the pixbuf for rendering on screen
        self.__buffer = None
        
        # color of the background
        self.__bg_color = gtk.gdk.color_parse("#000000")
        
        # offscreen drawing pixmap
        self.__offscreen = Pixmap(None, 800, 480)

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

        # save-under buffers (for rendering icons, etc)
        # a buffer is a tuple (pixmap, x, y, w, h)
        self.__save_unders = []

        # flag for marking new images that have not been rendered to screen yet
        self.__is_new_image = False
               
        self.__hi_quality_timer = None
        
        # the currently available zoom levels (= _ZOOM_LEVELS + fitting)
        self.__zoom_levels = []
        self.__zoom_level = 4
        self.__zoom_value = 1.0
        self.__zoom_fit = 0
        self.__zoom_100 = 0

        self.__timer_tstamp = 0
        self.__current_file = ""
        self.__banner = None

        # the loader contains the complete image
        self.__loader = None
        self.__loading_cancelled = False
        self.__pixbuf = None

        # slide from right or left
        self.__slide_from_right = True
        
        Widget.__init__(self)

        # create a client-side pixmap for rendering
        self.__buffer = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,
                                       True, 8, 800, 480)


    def render_this(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        if (self.__invalidated):
            self._render()
        else:
            screen.copy_pixmap(self.__offscreen, x, y, x, y, w, h)
        

    def set_size(self, w, h):
    
        Widget.set_size(self, w, h)

        if ((w, h) != self.__visible_size):
            self.__visible_size = (w, h)
            if (self.__original_size != (0, 0)):
                self.__invalidated = True
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

        if (not self.__zoom_levels): return

        cx, cy = self.__center_pos
        cx /= self.__zoom_value
        cy /= self.__zoom_value
        
        self.__zoom_level = max(0, min(len(self.__zoom_levels) - 1, level))
        self.__zoom_value = self.__zoom_levels[self.__zoom_level] / 100.0
        
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
            
            if (vwidth < width):
                bw = (width - vwidth) / 2
                self.__offscreen.fill_area(x, y, bw, height, self.__bg_color)
                self.__offscreen.fill_area(x + width - bw - 1, y, bw + 1, height,
                                           self.__bg_color)
            
            if (vheight < height):
                bh = (height - vheight) / 2
                self.__offscreen.fill_area(x, y, width, bh, self.__bg_color)
                self.__offscreen.fill_area(x, y + height - bh - 1, width, bh + 1,
                                           self.__bg_color)
                
        else:
            # copy on the server-side (this is our simple trick for
            # fast scrolling!)
            self.__offscreen.copy_pixmap(self.__offscreen, #screen,
                                         x + src_x, y + src_y,
                                         x + dest_x, y + dest_y,
                                         src_w, src_h)
            
        # render borders
        for rx, ry, rw, rh in areas:
            self.__render_area(rx, ry, rw, rh, high_quality)

        # wait for VBL
        #omapfb.sync_gfx()

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
        Loads the given image file. If we're currently loading another
        image, cancel the loading first.
        """

        if (f != self.__current_file):        
            self.__loading_cancelled = True
            
            if (self.__hi_quality_timer):
                gobject.source_remove(self.__hi_quality_timer)
            
            self.__load_img(f)



    def __load_img(self, f):
        """
        Loads the image.
        """

        def on_data(d, amount, total, size_read):
            if (d):
                size_read[0] += len(d)
                self.__loader.write(d)
                self.update_observer(self.OBS_PROGRESS, size_read[0], total)
            else:
                try:
                    self.__loader.close()
                    self.__finish_loading()
                except:
                    pass
                self.update_observer(self.OBS_END_LOADING)
        
        try:
            self.__loader.close()
        except:
            pass
        self.__loader = gtk.gdk.PixbufLoader()
        self.__loader.connect("size-prepared", self.__on_check_size)
        self.__current_file = f

        self.update_observer(self.OBS_BEGIN_LOADING, f)
        try:
            f.load(0, on_data, [0])
        except:
            #self.__loader.close()
            self.update_observer(self.OBS_END_LOADING)


            
        
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
        
        self.__is_new_image = True
        self.__scale_to_fit()

        # collect three generations of garbage
        #for i in range(3): gc.collect()


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
      
        
    def slide_from_left(self):
    
        self.__slide_from_right = False
        
        
    def slide_from_right(self):
    
        self.__slide_from_right = True
        
        
    def fx_slide_in(self, wait = True):
    
        import threading

        STEP = 40
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        finished = threading.Event()
        
        def f(i):
            dx = min(STEP, w - i)

            if (self.__slide_from_right):
                screen.copy_buffer(screen, x + dx, y, x, y, w - dx, h)
                screen.copy_pixmap(self.__offscreen, x + i, y, x + w - dx, y,
                                   dx, h)
            else:
                screen.copy_buffer(screen, x, y, x + dx, y, w - dx, h)
                screen.copy_pixmap(self.__offscreen, x + w - dx - i, y, x, y,
                                   dx, h)
            
            if (i < w - STEP):
                gobject.timeout_add(5, f, i + STEP)
            else:
                finished.set()

        f(0)
        while (wait and not finished.isSet()): gtk.main_iteration(False)
        
