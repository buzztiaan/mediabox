"""
This module is basically a port of mClock from pygame (SDL) to Gtk+.
"""

import sun

import gtk
import os
import time
import datetime
import math


_PATH = os.path.dirname(__file__)

# maps for the seasons
_MAPS = ["1-Winter-January.jpg", "2-Spring-April.jpg",
         "3-Summer-July.jpg", "4-Fall-October.jpg"]

# some constants for determining the current season
# from http://www.astro.uu.nl/~strous/AA/en/antwoorden/seizoenen.html
_DELTA_SPRING = datetime.timedelta(365,  2, 0, 0, 49, 5, 0)
_DELTA_SUMMER = datetime.timedelta(365, 57, 0, 0, 47, 5, 0)
_DELTA_AUTUMN = datetime.timedelta(365, 31, 0, 0, 48, 5, 0)
_DELTA_WINTER = datetime.timedelta(365, 33, 0, 0, 49, 5, 0)

_START_SPRING_2005 = datetime.datetime(2005,  3, 20, 11, 33, 19)  #20 March 2005	11:33:19
_START_SUMMER_2005 = datetime.datetime(2005,  6, 21,  6, 39, 11)  # 21 June 2005 06:39:11
_START_AUTUMN_2005 = datetime.datetime(2005,  9, 22, 22, 16, 34)  #22 September 2005 22:16:34
_START_WINTER_2005 = datetime.datetime(2005, 12, 21, 18, 34, 51)  #21 December 2005 18:34:51

_BPP = gtk.gdk.get_default_root_window().get_depth()


class SunClock(gtk.DrawingArea):

    def __init__(self):
                
        self.__render_map_next = 0
                
        self.__night = gtk.gdk.pixbuf_new_from_file(
            os.path.join(_PATH, "0-Night.jpg"))
            
        self.__sun = gtk.gdk.pixbuf_new_from_file(
            os.path.join(_PATH, "sun.png"))
            
        self.__numbers = gtk.gdk.pixbuf_new_from_file(
            os.path.join(_PATH, "numbers.png"))
    
        gtk.DrawingArea.__init__(self)
        self.set_size_request(800, 400)
        self.connect("expose-event", self.__on_expose)        
    
        # mask for overlaying the night
        self.__mask = gtk.gdk.Pixmap(None, 800, 400, 1)
        self.__mask_gc = self.__mask.new_gc()
    
        # buffer for holding the rendered map
        self.__map = gtk.gdk.Pixmap(None, 800, 400, _BPP)
        self.__map_gc = self.__map.new_gc()
    
        # buffer for the screen
        self.__screen = gtk.gdk.Pixmap(None, 800, 400, _BPP)
        self.__screen_gc = self.__screen.new_gc()
      
        self.update()
        
        
    def __on_expose(self, src, ev):
    
        area = ev.area
        src.window.draw_drawable(src.window.new_gc(), self.__screen,
                                 area.x, area.y, area.x, area.y,
                                 area.width, area.height)
        
        
    def __clear_mask(self):
    
        self.__mask_gc.set_foreground(gtk.gdk.Color(0, 0, 0, 0))
        self.__mask.draw_rectangle(self.__mask_gc, True, 0, 0, 800, 400)
        
        
        
    def __draw_mask(self, vertices):
    
        self.__mask_gc.set_foreground(gtk.gdk.Color(0, 0, 0, 1))
        
        for poly in vertices:
            self.__mask.draw_polygon(self.__mask_gc, True, poly)
        
        
    def __set_background(self, n):
    
        img = _MAPS[n]
        self.__bg.set_from_file(os.path.join(_PATH, img))
        
        
    def __get_current_map(self):

        years_since = time.localtime()[0] - 2005

        start_spring = _START_SPRING_2005 + years_since * _DELTA_SPRING
        start_summer = _START_SUMMER_2005 + years_since * _DELTA_SUMMER
        start_autumn = _START_AUTUMN_2005 + years_since * _DELTA_AUTUMN
        start_winter = _START_WINTER_2005 + years_since * _DELTA_WINTER
    
        now = datetime.datetime.utcnow()
        if (now < start_spring):
            return 0
        elif (start_spring <= now < start_summer):
            return 1
        elif (start_summer <= now < start_autumn):
            return 2
        elif (start_autumn <= now < start_winter):
            return 3
        else:
            return 0
        
        
    def update(self):
    
        if (time.time() > self.__render_map_next):
            self.__render_map()
            self.__render_map_next = time.time() + 10 * 60  # ten minutes

        self.__render_clock()            
        self.queue_draw()


    def __render_clock(self):
    
        now = time.localtime(time.time())
        hours = now[3]
        mins = now[4]
        secs = now[5]

        self.__screen.draw_drawable(self.__screen_gc, self.__map, 0, 0, 0, 0,
                                    800, 400)

        t = "%d:%02d" % (hours, mins)
        w = len(t) * 108
        h = 200
        x = 400 - w / 2
        y = 200 - h / 2
        for c in t:
            try:
                cx = int(c) * 108
            except:
                cx = 10 * 108
            self.__screen.draw_pixbuf(self.__screen_gc, self.__numbers,
                                      cx, 0, x, y, 108, 200)
            x += 108
        #end for                           


    def __render_map(self):

        now = datetime.datetime.utcnow()
        year = now.year
        month = now.month
        day = now.day
        hours = now.hour
        mins = now.minute
        secs = now.second
    
        the_sun = sun.Sun()
        time_in_minutes = hours * 60.0 + (1.0 / 60.0 * mins)
                
        # compute declination of the sun
        n_days = the_sun.daysSince2000Jan0(year, month, day)
        res = the_sun.sunRADec(n_days)
        dec = res[1]
        
        # compute longitude position of the sun in degrees
        std = hours + mins / 60.0 + secs / 3600.0
        tau = the_sun.computeGHA(day, month, year, std)
               
        # (x0, y0) is the center of the map (0 deg, 0 deg) 
        k = math.pi / 180.0
        x0 = 180
        y0 = 90
        
        scale = 400 / 180.0
        
        # walk around the world and compute illumination
        vertices = []
        for i in range(-180, 180, 1):
            longitude = i + tau            
            tanlat = - math.cos(longitude * k) / math.tan(dec * k)
            arctanlat = math.atan(tanlat) / k
            y1 = y0 - int(arctanlat + 0.5)

            longitude += 1            
            tanlat = - math.cos(longitude * k) / math.tan(dec * k)
            arctanlat = math.atan(tanlat) / k
            y2 = y0 - int(arctanlat + 0.5)                        
            
            v1 = (int(scale * (x0 + i)), int(scale * y1))
            v2 = (int(scale * (x0 + i + 1)), int(scale * y2))
            if (dec > 0):
                v3 = (int(scale * (x0 + i + 1)), 400)
                v4 = (int(scale * (x0 + i)), 400)
            else:
                v3 = (int(scale * (x0 + i + 1)), 0)
                v4 = (int(scale * (x0 + i)), 0)
                
            vertices.append((v1, v2, v3, v4))
        #end for        
        
        sun_x = 400 - int(scale * tau)
        sun_y = 200 - int(scale * dec)
        if (sun_x < 0): sun_x = 800 + sun_x
        
        map_file = _MAPS[self.__get_current_map()]
        map_pbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(_PATH, map_file))
                                       
        self.__clear_mask()
        self.__draw_mask(vertices)
        
        cmap = self.__map.get_colormap()
        self.__map_gc.set_foreground(cmap.alloc_color("blue"))
        
        self.__map.draw_pixbuf(self.__map_gc, map_pbuf, 0, 0, 0, 0, -1, -1)
        self.__map_gc.set_clip_mask(self.__mask)
        self.__map.draw_pixbuf(self.__map_gc, self.__night, 0, 0, 0, 0, -1, -1)
        self.__map_gc.set_clip_rectangle(gtk.gdk.Rectangle(0, 0, 800, 480))
        self.__map.draw_line(self.__map_gc, 0, 200, 800, 200)
        self.__map.draw_pixbuf(self.__map_gc, self.__sun, 0, 0,
                               sun_x - self.__sun.get_width() / 2,
                               sun_y - self.__sun.get_height() / 2,
                               -1, -1)
        
        del map_pbuf
        import gc; gc.collect()       

