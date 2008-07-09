from utils.Observable import Observable

import gtk
import gobject
import time


_SCROLL_DELAY = 10
_TAP_AND_HOLD_DELAY = 500


class KineticScroller(Observable):
    """
    Class for adding kinetic scrolling to a child widget. The child must
    implement a move(dx, dy) method.
    """

    OBS_SCROLLING = 0
    OBS_STOPPED = 1
    OBS_CLICKED = 2
    OBS_TAP_AND_HOLD = 3


    def __init__(self, child):
    
        self.__may_click = True
    
        self.__child = child

        self.__is_dragging = False
        self.__dragging_from = (0, 0)
        self.__drag_pointer = (0, 0)
        self.__drag_begin = 0
        self.__pointer = (0, 0)
                
        # whether kinetic scrolling is enabled
        self.__kinetic_enabled = True

        # the area where the user can touch to scroll
        self.__touch_area = (0, 1000)
        
        # the physics behind kinetic scrolling
        self.__impulse_point = 0        
        self.__delta_s = (0, 0)
        self.__delta_t = 0
   
        # this flag tells whether we are currently scrolling    
        self.__scrolling = False
        
        # whether the impulse handler is running
        self.__impulse_handler_running = False

        child.connect_button_pressed(self.__on_drag_start)
        child.connect_button_released(self.__on_drag_stop)
        child.connect_pointer_moved(self.__on_drag)


    def impulse(self, force_x, force_y):
    
        self.__delta_s = (force_x, force_y)
        self.__delta_t = 1        

        # start up impulse handler if not running        
        if (not self.__impulse_handler_running):
            self.__impulse_handler_running = True
            self.__impulse_handler()
            
            
    def stop_scrolling(self):
    
        self.__delta_s = (0, 0)
        self.__is_dragging = False
            

    def enable_kinetic(self, value):
        """
        Enables or disables kinetic scrolling.
        """
    
        self.__kinetic_enabled = value


    def set_touch_area(self, begin, end):
    
        self.__touch_area = (begin, end)


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
            
            gobject.timeout_add(_SCROLL_DELAY, self.__impulse_handler)
                
        
    def __on_drag_start(self, px, py):
    
        self.__pointer = (px, py)
        touch_begin, touch_end = self.__touch_area
        
        # the pointer is inside the touch area
        if (touch_begin <= px <= touch_end):
            self.__is_dragging = True
            self.__drag_pointer = (px, py)
            self.__dragging_from = (px, py)
            self.__drag_begin = time.time()
            #delta_sx, delta_sy = self.__delta_s
           
            self.__delta_s = (0, 0)
            self.__scrolling = False
        
            #gobject.timeout_add(_TAP_AND_HOLD_DELAY,
            #                    self.__check_for_tap_and_hold, px, py)

        #end if

        handled = self.update_observer(self.OBS_CLICKED, px, py)
        if (handled):
            self.__is_dragging = False
            self.__scrolling = False
            
                
        
    def __on_drag_stop(self, px, py):

        self.__pointer = (px, py)

        #if (not self.__is_dragging): return
        self.__is_dragging = False
        self.__scrolling = False
      
        # start up impulse handler if not running        
        if (not self.__impulse_handler_running):
            self.__impulse_handler_running = True
            self.__impulse_handler()
       
        
    def __on_drag(self, px, py):

        self.__pointer = (px, py)
            
        if (self.__is_dragging):
            now = time.time()            

            if (self.__drag_pointer == (px, py)): return

            prev_dsx, prev_dsy = self.__delta_s
            dsx = self.__drag_pointer[0] - px
            dsy = self.__drag_pointer[1] - py
            
            #if (abs(prev_dsx) < 0.1 and abs(prev_dsy) < 0.1 and
            #      abs(dsx - prev_dsx) < 30 and abs(dsy - prev_dsy) < 30):
            #    return
            #else:
            self.__delta_s = (dsx, dsy)
                
            self.__delta_t = now - self.__impulse_point
            self.__impulse_point = now
            self.__drag_pointer = (px, py)
            
            if (abs(self.__delta_s[0]) > 0.1 or abs(self.__delta_s[1]) > 0.1):
                
                if (not self.__scrolling):
                    self.update_observer(self.OBS_SCROLLING)        
                    self.__scrolling = True                                        
                    
                self.__child.move(self.__delta_s[0], self.__delta_s[1])
            #end if        
        #end if

