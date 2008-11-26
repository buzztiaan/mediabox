from Widget import Widget
import gtk


class EventSensor(object):

    def __init__(self, gtkwidget):
        
        self.__zones = {}
        self.__locked_zone = None
        
        gtkwidget.connect("button-press-event", self.__on_button_pressed)
        gtkwidget.connect("button-release-event", self.__on_button_released)
        gtkwidget.connect("motion-notify-event", self.__on_motion)
        
        gtkwidget.set_events(gtk.gdk.BUTTON_PRESS_MASK |
                             gtk.gdk.BUTTON_RELEASE_MASK |
                             gtk.gdk.POINTER_MOTION_MASK |
                             gtk.gdk.POINTER_MOTION_HINT_MASK)


    def __on_button_pressed(self, src, ev):

        px, py = src.get_pointer()
        zone = self.__get_zone_at(px, py)
        #zones = self.__get_zones_at(px, py)
        #print zones
        #for zone in zones:
        if (zone):
            cb, args = zone
            cb(Widget.EVENT_BUTTON_PRESS, px, py, *args)
            self.__locked_zone = zone
        
        
    def __on_button_released(self, src, ev):

        px, py = src.get_pointer()
        zone = self.__locked_zone or self.__get_zone_at(px, py)
        if (zone):
            cb, args = zone
            cb(Widget.EVENT_BUTTON_RELEASE, px, py, *args)
        self.__locked_zone = None
        
        
    def __on_motion(self, src, ev):

        px, py = src.get_pointer()
        zone = self.__locked_zone or self.__get_zone_at(px, py)
        if (zone):
            cb, args = zone
            cb(Widget.EVENT_MOTION, px, py, *args)
    
    
    def __get_zones_at(self, px, py):
    
        zones = []
        for x, y, w, h, tstamp, cb, args in self.__zones.values():
            if (x <= px <= x + w and y <= py <= y + h):
                zones.append((cb, args))
                
        return zones
        
        
    def __get_zone_at(self, px, py):
    
        zone = None
        zone_tstamp = 0
        
        for x, y, w, h, tstamp, cb, args in self.__zones.values():
            if (x <= px <= x + w and y <= py <= y + h and tstamp > zone_tstamp):
                zone = (cb, args)
                zone_tstamp = tstamp
        #end for
        
        return zone
        
        
    def set_zone(self, ident, x, y, w, h, tstamp, cb, *args):
    
        #print "ZONE", ident, x, y, w, h
        self.__zones[ident] = (x, y, w, h, tstamp, cb, args)
        
        
    def remove_zone(self, ident):
    
        try:
            del self.__zones[ident]
        except:
            pass

