from utils.Observable import Observable

import gtk
import gobject
import time


class KineticScroller(gtk.EventBox, Observable):
    """
    Class for adding kinetic scrolling to a child widget. The child must
    implement a move(dx, dy) method.
    """

    OBS_SCROLLING = 0
    OBS_STOPPED = 1
    OBS_CLICKED = 2


    def __init__(self, child):
    
        self.__may_click = True
    
        self.__child = child

        self.__is_dragging = False
        self.__dragging_from = (0, 0)
        self.__drag_pointer = (0, 0)
        self.__drag_begin = 0
        
        # whether kinetic scrolling is enabled
        self.__kinetic_enabled = True
        
        # the physics behind kinetic scrolling
        self.__impulse_point = 0        
        self.__delta_s = (0, 0)
        self.__delta_t = 0

        # this flag helps to tell the difference between a mouse click and
        # a drag or stop operation
        self.__might_be_click = True
    
        # this flag tells whether we are currently scrolling    
        self.__scrolling = False
        
        # whether the impulse handler is running
        self.__impulse_handler_running = False

    
        gtk.EventBox.__init__(self)
        self.add(child)
        
        self.connect("button-press-event", self.__on_drag_start)
        self.connect("button-release-event", self.__on_drag_stop)
        self.connect("motion-notify-event", self.__on_drag)


    def enable_kinetic(self, value):
        """
        Enables or disables kinetic scrolling.
        """
    
        self.__kinetic_enabled = value


    def __impulse_handler(self):
        """
        Handler for applying the physics of kinetic scrolling.
        """
        
        if (not self.__kinetic_enabled): return False
        
        delta_sx, delta_sy = self.__delta_s
        
        if (self.__is_dragging or (abs(delta_sx) < 1 and abs(delta_sy) < 1)):
            # shut down impulse handler when not needed to save battery
            self.__impulse_handler_running = False
            return False
        
        else:
            self.__child.move(int(delta_sx), int(delta_sy))
            
            # apply simple physics
            vx = delta_sx / self.__delta_t
            vx *= 0.96
            vy = delta_sy / self.__delta_t
            vy *= 0.96
            
            self.__delta_s = (vx * self.__delta_t, vy * self.__delta_t)
            
            return True


    def __check_for_click(self):
    
        if (self.__might_be_click):        
            px, py = self.get_pointer()
            fx, fy = self.__dragging_from
            
            dx = abs(fx - px)
            dy = abs(fy - py)
            
            if (dx < 30 and dy < 30):
                self.update_observer(self.OBS_CLICKED, px, py)
        #end if
                
        
    def __on_drag_start(self, src, ev):
    
        px, py = self.get_pointer()
        self.__is_dragging = True
        self.__drag_pointer = (px, py)
        self.__dragging_from = (px, py)
        self.__drag_begin = time.time()
        delta_sx, delta_sy = self.__delta_s
        
        # during kinetic scrolling, clicks stop the scrolling but don't select
        # an item
        if (abs(delta_sx) < 1 and abs(delta_sy) < 1):
            self.__might_be_click = True
        else:
            self.__might_be_click = False
            
        self.__delta_s = (0, 0)
        self.__scrolling = False
                
        
    def __on_drag_stop(self, src, ev):
    
        if (not self.__is_dragging): return
        
        self.__is_dragging = False
        self.__scrolling = False

        if (self.__may_click):
            self.__check_for_click()
        
        # start up impulse handler if not running
        if (not self.__impulse_handler_running):
            gobject.timeout_add(5, self.__impulse_handler)
            self.__impulse_handler_running = True

        # wait until we may accept clicks again
        def f(): self.__may_click = True
        self.__may_click = False        
        gobject.timeout_add(500, f)
        
        
    def __on_drag(self, src, ev):
            
        if (self.__is_dragging):
            px, py = self.get_pointer()
            now = time.time()            

            if (self.__drag_pointer == (px, py)): return

            self.__delta_s = (self.__drag_pointer[0] - px,
                              self.__drag_pointer[1] - py)
            self.__delta_t = now - self.__impulse_point
            self.__impulse_point = now
            self.__drag_pointer = (px, py)
            
            if (not self.__might_be_click or
                abs(self.__delta_s[0]) > 0.1 or abs(self.__delta_s[1]) > 0.1):
                #self.__might_be_click = False
                
                if (not self.__scrolling):
                    self.update_observer(self.OBS_SCROLLING)        
                    self.__scrolling = True                                        
                    
                self.__child.move(self.__delta_s[0], self.__delta_s[1])
            #end if        
        #end if            
