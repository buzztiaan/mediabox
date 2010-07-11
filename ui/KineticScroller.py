"""
Decorator for adding kinetic scrolling to a widget.
"""


from utils.EventEmitter import EventEmitter
from utils.Observable import Observable

import gtk
import gobject
import time


_FPS = 50
_SCROLL_DELAY = 1.0 / _FPS
_DRAG_THRESHOLD = 20

# a click must last at least this long to be recognized as such
_CLICK_THRESHOLD = 0

# a tap-and-hold action must last at least this long to be recognized as such
_TAP_AND_HOLD_THRESHOLD = 500


class KineticScroller(EventEmitter, Observable):
    """
    Class for adding kinetic scrolling to a widget. The widget must
    implement a move(dx, dy) method.
    """

    EVENT_CLICKED = "clicked"
    EVENT_SCROLLING_STARTED = "scrolling-started"
    EVENT_SCROLLING_STOPPED = "scrolling-stopped"
    EVENT_TAP_AND_HOLD = "tap-and-hold"

    # deprecated
    OBS_SCROLLING = 0
    OBS_STOPPED = 1
    OBS_CLICKED = 2
    OBS_TAP_AND_HOLD = 3


    def __init__(self, child):
    
        self.__is_click = False
        self.__is_button_pressed = False        
    
        # timestamp of when the click began
        self.__click_begin = 0
    
        self.__child = child

        self.__is_dragging = False
        self.__drag_pointer = (0, 0)
        self.__drag_begin = 0
        self.__pointer = (0, 0)
        self.__drag_threshold = _DRAG_THRESHOLD
                
        # whether kinetic scrolling is enabled
        self.__kinetic_enabled = True

        # the physics behind kinetic scrolling
        self.__impulse_point = 0        
        self.__delta_s = (0, 0)
        self.__delta_t = 0
   
        # this flag tells whether we are currently scrolling    
        self.__scrolling = False
        
        # whether the impulse handler is running
        self.__impulse_handler_running = False
        
        # handler for detecting tap-and-hold
        self.__tap_and_hold_handler = None
    
    
        EventEmitter.__init__(self)
        
        child.connect_button_pressed(self.__on_button_pressed)
        child.connect_button_released(self.__on_button_released)
        child.connect_pointer_moved(self.__on_drag)


    def connect_clicked(self, cb, *args):
    
        self._connect(self.EVENT_CLICKED, cb, *args)


    def connect_scrolling_started(self, cb, *args):
    
        self._connect(self.EVENT_SCROLLING_STARTED, cb, *args)


    def connect_scrolling_stopped(self, cb, *args):
    
        self._connect(self.EVENT_SCROLLING_STOPPED, cb, *args)


    def connect_tap_and_hold(self, cb, *args):
    
        self._connect(self.EVENT_TAP_AND_HOLD, cb, *args)


    def set_drag_threshold(self, t):
        """
        Sets the threshold amount for registering motions as dragging.
        
        @param t: threshold in pixels
        """
    
        self.__drag_threshold = t


    def impulse(self, force_x, force_y):
    
        self.__delta_s = (force_x, force_y)
        self.__delta_t = 1        

        # start up impulse handler if not running        
        if (not self.__impulse_handler_running):
            self.__impulse_handler_running = True
            self.__impulse_handler()
            
            
    def stop_scrolling(self):
        """
        Stops scrolling immediately.
        """
    
        self.__delta_s = (0, 0)
        self.__is_dragging = False
        self.emit_event(self.EVENT_SCROLLING_STOPPED)
            

    def set_enabled(self, value):
        """
        Enables or disables kinetic scrolling.
        """
    
        self.__kinetic_enabled = value


    def __impulse_handler(self):
        """
        Handler for applying the physics of kinetic scrolling.
        """
        
        if (not self.__kinetic_enabled):
            self.update_observer(self.OBS_STOPPED)
            return False
        
        delta_sx, delta_sy = self.__delta_s
        
        now = time.time()
        #if (now < self.__impulse_point + _SCROLL_DELAY):
        #    gobject.timeout_add(5, self.__impulse_handler)
        #    return False
        #else:
        #    self.__impulse_point = now
        
        if (self.__is_dragging or (abs(delta_sx) < 1 and abs(delta_sy) < 1)):
            # shut down impulse handler when not needed to save battery
            self.__impulse_handler_running = False
            self.emit_event(self.EVENT_SCROLLING_STOPPED)
            return False
        
        else:
            delta_sx, delta_sy = self.__child.move(int(delta_sx), int(delta_sy))
            
            # apply simple physics
            vx = delta_sx / self.__delta_t
            vx *= 0.96
            vy = delta_sy / self.__delta_t
            vy *= 0.96
            
            self.__delta_s = (vx * self.__delta_t, vy * self.__delta_t)
            
            # do not call main_iteration from inside a main_iteration call,
            # it will block
            #gtk.main_iteration(False)
            gobject.timeout_add(0, self.__impulse_handler)
        

    def __begin_tap_and_hold(self):
    
        self.__abort_tap_and_hold()
        self.__tap_and_hold_handler = \
            gobject.timeout_add(_TAP_AND_HOLD_THRESHOLD, self.__on_tap_and_hold)


    def __abort_tap_and_hold(self):
    
        if (self.__tap_and_hold_handler):
            gobject.source_remove(self.__tap_and_hold_handler)
            self.__tap_and_hold_handler = None
        
        
    def __on_tap_and_hold(self):
    
        self.__tap_and_hold_handler = None
        px, py = self.__pointer
        self.__is_click = False
        self.__is_dragging = False
        self.__is_button_pressed = False
        
        if (self.__kinetic_enabled):
            print "TAP AND HOLD", px, py
            self.emit_event(self.EVENT_TAP_AND_HOLD, px, py)
                
        
    def __on_button_pressed(self, px, py):
    
        self.__pointer = (px, py)
        self.__is_button_pressed = True

        if (not self.__impulse_handler_running):
            self.__click_begin = time.time()
            self.__is_click = True
        else:
            # stop scrolling if the user clicks while scrolling
            self.__is_click = False
            self.stop_scrolling()

        self.__begin_tap_and_hold()
        self.__is_dragging  = False

        
    def __on_button_released(self, px, py):

        self.__pointer = (px, py)
        self.__is_button_pressed = False
        self.__is_dragging = False
        
        self.__abort_tap_and_hold()
        
        if (self.__is_click):
            click_duration = (time.time() - self.__click_begin) * 1000
            #print "click duration:", click_duration, "ms"
            if (click_duration > _CLICK_THRESHOLD):
                self.emit_event(self.EVENT_CLICKED, px, py)
                
        else:
            # start up impulse handler if not running
            if (not self.__impulse_handler_running):
                self.__impulse_handler_running = True
                self.__impulse_handler()            
        #end if

        self.__scrolling = False
        self.__is_click = False

        
    def __on_drag(self, px, py):

        if (not self.__is_button_pressed or not self.__kinetic_enabled): return


        prev_px, prev_py = self.__pointer

        dx = px - prev_px
        dy = py - prev_py


        # begin dragging
        
        if (abs(dx) > self.__drag_threshold or \
            abs(dy) > self.__drag_threshold):
            print "ABORT TAP AND HOLD"
            self.__abort_tap_and_hold()
            self.__is_click = False

        if (not self.__is_dragging):
            self.__is_dragging = True
            self.__drag_pointer = (prev_px, prev_py)
            self.__drag_begin = time.time()

            self.__delta_s = (0, 0)
            self.__scrolling = False

        # handle dragging
        elif (self.__is_dragging):
            now = time.time()

            if (self.__drag_pointer == (px, py)): return

            prev_dsx, prev_dsy = self.__delta_s
            dsx = self.__drag_pointer[0] - px
            dsy = self.__drag_pointer[1] - py
            self.__delta_s = (dsx, dsy)
                
            self.__delta_t = now - self.__impulse_point
            if (self.__delta_t < 0.05): return
            
            self.__impulse_point = now
            self.__drag_pointer = (px, py)
            self.__pointer = (px, py)
            
            if (abs(self.__delta_s[0]) > 0.1 or abs(self.__delta_s[1]) > 0.1):
                
                if (not self.__scrolling):
                    self.emit_event(self.EVENT_SCROLLING_STARTED)
                    self.__scrolling = True
                    
                self.__child.move(self.__delta_s[0], self.__delta_s[1])
            
            else:
                self.emit_event(self.EVENT_SCROLLING_STOPPED)
            #end if

        #end if

