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
                             gtk.gdk.POINTER_MOTION_MASK)



    def __on_button_pressed(self, src, ev):

        px, py = src.get_pointer()
        zone = self.__get_zone_at(px, py)
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
    
        
        
    def __get_zone_at(self, px, py):
    
        for x, y, w, h, cb, args in self.__zones.values():
            if (x <= px <= x + w and y <= py <= y + h):
                return (cb, args)
                
        return None
        
        
    def set_zone(self, ident, x, y, w, h, cb, *args):
    
        #print "ZONE", ident, x, y, w, h
        self.__zones[ident] = (x, y, w, h, cb, args)
        
        
    def remove_zone(self, ident):
    
        try:
            del self.__zones[ident]
        except:
            pass

