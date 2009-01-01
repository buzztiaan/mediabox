from Widget import Widget

import math
import time
import gobject


class MultiTouchWidget(Widget):
    """
    Base class for widgets that want to register multitouch events on the
    touchscreen. This doesn't work too well, yet.
    """

    EVENT_MULTITOUCH_START = "multitouch-start"
    EVENT_MULTITOUCH_MOTION = "multitouch-motion"
    EVENT_MULTITOUCH_STOP = "multitouch-stop"
    

    STATE_NONE = 0
    STATE_ONE_FINGER = 1
    STATE_TWO_FINGERS = 2


    def __init__(self):

        self.__state = self.STATE_NONE
        self.__current_coords = (0, 0)
        self.__previous_coords = (0, 0)
        self.__timestamp = 0

        self.__velocity_history = [0, 0, 0, 0]        
            
        self.__finger1 = (0, 0)
        self.__finger2 = (0, 0)
        self.__button = 0
        self.__finger_queue = []
    
        Widget.__init__(self)
        #self.connect_button_pressed(self.__on_press)
        #self.connect_button_released(self.__on_release)
        #self.connect_pointer_moved(self.__on_motion)

       
        
    def __find_finger2(self, x, y):
        """
        Returns the position of the second finger.
        """
    
        fx, fy = self.__finger1
        dx = x - fx
        dy = y - fy
        return (x + dx, y + dy)
        
        

    def __on_press(self, px, py):
    
        #if (self.__state == self.STATE_NONE):
        self.__state = self.STATE_ONE_FINGER
        
        self.__current_coords = (px, py)
        self.__previous_coords = (px, py)
        self.__finger1 = (px, py)
        self.__velocity_history = [0, 0, 0, 0]
        self.__timestamp = time.time()
        self.__button = 1
        self.__finger_queue = []
        gobject.timeout_add(10, self.__velocity_timer)
    
    
    def  __on_release(self, px, py):
    
        self.__state = self.STATE_NONE
        self.send_event(self.EVENT_MULTITOUCH_STOP)
        self.__button = 0
        
        
    def __on_motion(self, px, py):

        if (not self.__button == 1): return
        
        self.__current_coords = (px, py)


        

    def __velocity_timer(self):

        if (not self.__button == 1): return False
    
        now = time.time()
        dt = now - self.__timestamp

        # compute the distance the pointer moved
        px, py = self.__current_coords
        ppx, ppy = self.__previous_coords        
        w = abs(ppx - px)
        h = abs(ppy - py)
        s = math.sqrt(w * w + h * h)

        # compute pointer speed (pixels per second)
        v = s / dt
        print "v", v
        
        self.__velocity_history.append(v)
        self.__velocity_history.pop(0)
        
        h1, h2, h3, h4 = self.__velocity_history
        if (h4 > 6000
            or h1 < 500 and (h2 > 1000 or h3 > 1000) and h4 < 500):
            is_peak = True
        else:
            is_peak = False
        
        if (is_peak):
            if (self.__state == self.STATE_ONE_FINGER):
                self.__state = self.STATE_TWO_FINGERS
                self.__velocity_history = [0, 0, 0, 0]
                #self.__finger1 = self.__previous_coords
                #self.__finger2 = self.__find_finger2(px, py)
                self.send_event(self.EVENT_MULTITOUCH_START)                
                print "two fingers"
                
            elif (self.__state == self.STATE_TWO_FINGERS):
                self.__state = self.STATE_ONE_FINGER
                #self.__finger1 = (px, py)
                self.send_event(self.EVENT_MULTITOUCH_STOP)
                self.__finger_queue = []
                print "one finger"

        #end if

        if (self.__current_coords != self.__previous_coords):
            if (self.__state == self.STATE_ONE_FINGER):
                #self.__finger1 = (px, py)
                pass
                
            elif (self.__state == self.STATE_TWO_FINGERS):
                self.__finger2 = self.__find_finger2(px, py)
                #fx1, fy1 = self.__finger1
                #fx2, fy2 = self.__finger2
                #print self.__finger1, self.__finger2
                self.__finger_queue.append((self.__finger1, self.__finger2))
                if (len(self.__finger_queue) > 3):
                    f1, f2 = self.__finger_queue.pop(0)
                    fx1, fy1 = f1
                    fx2, fy2 = f2
                    self.send_event(self.EVENT_MULTITOUCH_MOTION,
                                    fx1, fy1, fx2, fy2)
        #end if

        self.__previous_coords = self.__current_coords
        self.__timestamp = now
        
        return True
        


    def get_fingers(self):
    
        return (self.__finger1, self.__finger2)


    def connect_multitouch_started(self, h, *args):
    
        self._connect(self.EVENT_MULTITOUCH_START, h, *args)

        
    def connect_multitouch_moved(self, h, *args):
    
        self._connect(self.EVENT_MULTITOUCH_MOTION, h, *args)


    def connect_multitouch_stopped(self, h, *args):
    
        self._connect(self.EVENT_MULTITOUCH_STOP, h, *args)

