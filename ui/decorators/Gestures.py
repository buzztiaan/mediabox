"""
Decorator class for detecting various finger gestures.
"""

from utils.EventEmitter import EventEmitter

import gobject

_STATE_NONE = 0
_STATE_TAP = 1
_STATE_HOLD = 2
_STATE_TAP_TAP = 3
_STATE_TAP_HOLD = 4
_STATE_MOTION = 5

_ACTION_PRESS = 0
_ACTION_RELEASE = 1
_ACTION_MOTION = 2

# motion directions
_DIRECTION_N = 0
_DIRECTION_NE = 1
_DIRECTION_E = 2
_DIRECTION_SE = 3
_DIRECTION_S = 4
_DIRECTION_SW = 5
_DIRECTION_W = 6
_DIRECTION_NW = 7

_MOTION_THRESHOLD = 10

_TRANSITIONS = {
    (_STATE_NONE, _ACTION_PRESS): _STATE_HOLD,
    (_STATE_NONE, _ACTION_RELEASE): _STATE_NONE,
    
    (_STATE_HOLD, _ACTION_RELEASE): _STATE_TAP,
    (_STATE_HOLD, _ACTION_MOTION): _STATE_MOTION,
    
    (_STATE_TAP, _ACTION_PRESS): _STATE_TAP_HOLD,
    (_STATE_TAP_HOLD, _ACTION_RELEASE): _STATE_TAP_TAP,

    (_STATE_MOTION, _ACTION_PRESS): _STATE_NONE,
    (_STATE_MOTION, _ACTION_RELEASE): _STATE_NONE,
}


class Gestures(EventEmitter):

    EVENT_TAP = "event-tap"
    EVENT_HOLD = "event-hold"
    EVENT_TAP_TAP = "event-tap-tap"
    EVENT_TAP_HOLD = "event-tap-hold"
    
    EVENT_TWIRL = "event-twirl"
    EVENT_SWIPE = "event-swipe"

    EVENT_RELEASE = "event-release"

    EVENT_GESTURE_FINISHED = "event-gesture-finished"


    def __init__(self, w):
    
        self.__widget = w
        self.__state = _STATE_NONE
        self.__is_button_pressed = False
        self.__tap_handler = None
        self.__hold_handler = None
        self.__pointer_pos = (0, 0)

        # list of twirling directions
        self.__twirling = []
        
        # swiping directions
        self.__swiping = []

        EventEmitter.__init__(self)

        w.connect_button_pressed(self.__on_press)
        w.connect_button_released(self.__on_release)
        w.connect_pointer_moved(self.__on_motion)
        
        
        

    def connect_tap(self, cb, *args):
    
        self._connect(self.EVENT_TAP, cb, *args)


    def connect_hold(self, cb, *args):
    
        self._connect(self.EVENT_HOLD, cb, *args)


    def connect_tap_tap(self, cb, *args):
    
        self._connect(self.EVENT_TAP_TAP, cb, *args)


    def connect_tap_hold(self, cb, *args):
    
        self._connect(self.EVENT_TAP_HOLD, cb, *args)


    def connect_twirl(self, cb, *args):
    
        self._connect(self.EVENT_TWIRL, cb, *args)


    def connect_swipe(self, cb, *args):
    
        self._connect(self.EVENT_SWIPE, cb, *args)


    def connect_release(self, cb, *args):
    
        self._connect(self.EVENT_RELEASE, cb, *args)


    def connect_gesture_finished(self, cb, *args):
    
        self._connect(self.EVENT_GESTURE_FINISHED, cb, *args)


    def __detect_event(self):
    
        if (self.__tap_handler):
            gobject.source_remove(self.__tap_handler)
        if (self.__state in (_STATE_TAP, _STATE_TAP_TAP)):
            self.__tap_handler = gobject.timeout_add(150, self.__on_tap)

        if (self.__hold_handler):
            gobject.source_remove(self.__hold_handler)
        if (self.__state in (_STATE_HOLD, _STATE_TAP_HOLD)):
            self.__hold_handler = gobject.timeout_add(800, self.__on_hold)


    def __on_tap(self):
    
        self.__tap_handler = None
        self.__twirling = []
        
        if (self.__state == _STATE_TAP):
            px, py = self.__pointer_pos
            print "TAP"
            self.emit_event(self.EVENT_TAP, px, py)
            self.__state = _STATE_NONE

        elif (self.__state == _STATE_TAP_TAP):
            px, py = self.__pointer_pos
            print "TAP TAP"
            self.emit_event(self.EVENT_TAP_TAP, px, py)
            self.__state = _STATE_NONE
        
        return False


    def __on_hold(self):
    
        self.__hold_handler = None

        if (self.__state == _STATE_HOLD):
            px, py = self.__pointer_pos
            print "HOLD"
            self.emit_event(self.EVENT_HOLD, px, py)
            self.__state = _STATE_NONE

        elif (self.__state == _STATE_TAP_HOLD):
            px, py = self.__pointer_pos
            print "TAP HOLD"
            self.emit_event(self.EVENT_TAP_HOLD, px, py)
            self.__state = _STATE_NONE
        
        return False


    def __on_press(self, px, py):
    
        self.__pointer_pos = (px, py)
        self.__is_button_pressed = True
        self.__swiping = []
        self.__state = _TRANSITIONS[(self.__state, _ACTION_PRESS)]
        self.__detect_event()
        
        
    def __on_release(self, px, py):

        self.__pointer_pos = (px, py)
        self.__is_button_pressed = False

        if (self.__state == _STATE_MOTION):
            self.__check_swiping()

        if (self.__state in (_STATE_NONE, _STATE_MOTION)):
            self.emit_event(self.EVENT_RELEASE, px, py)
    
        self.__state = _TRANSITIONS[(self.__state, _ACTION_RELEASE)]
        self.__detect_event()
        
        
    def __on_motion(self, px, py):
    
        if (not self.__is_button_pressed): return
    
        prev_px, prev_py = self.__pointer_pos
        self.__pointer_pos = (px, py)
        
        dx = px - prev_px
        dy = py - prev_py

        if (abs(dx) < _MOTION_THRESHOLD): dx = 0
        if (abs(dy) < _MOTION_THRESHOLD): dy = 0

        if (dx == 0 and dy < 0):
            direction = _DIRECTION_N
        elif (dx > 0 and dy < 0):
            direction = _DIRECTION_NE
        elif (dx > 0 and dy == 0):
            direction = _DIRECTION_E
        elif (dx > 0 and dy > 0):
            direction = _DIRECTION_SE
        elif (dx == 0 and dy > 0):
            direction = _DIRECTION_S
        elif (dx < 0 and dy > 0):
            direction = _DIRECTION_SW
        elif (dx < 0 and dy == 0):
            direction = _DIRECTION_W
        elif (dx < 0 and dy < 0):
            direction = _DIRECTION_NW
            
        self.__twirl(direction)
        self.__swipe(direction)
        self.__state = _TRANSITIONS[(self.__state, _ACTION_MOTION)]
        self.__detect_event()


    def __twirl(self, direction):
    
    
        # avoid double entries
        if (self.__twirling and self.__twirling[-1] == direction):
            return
        else:
            self.__twirling.append(direction)
        
        # is twirl long enough (full circle)?
        if (len(self.__twirling) < 8): return
            
        # check twirl
        directions = []
        prev_d = self.__twirling[0]
        for d in self.__twirling[1:]:
            if ((prev_d, d) == (_DIRECTION_NW, _DIRECTION_N)):
                directions.append(1)
            elif ((prev_d, d) == (_DIRECTION_N, _DIRECTION_NW)):
                directions.append(-1)
            elif (d > prev_d):
                directions.append(1)
            elif (d < prev_d):
                directions.append(-1)
            prev_d = d
        #end for
               
        twirl_sum = reduce(lambda a,b: a + b, directions)
        twirl_length = len(directions)

        if (twirl_sum >= twirl_length - 2):
            # clockwise twirl
            print "CLOCKWISE"
            self.emit_event(self.EVENT_TWIRL, 1)
            self.__twirling = self.__twirling[1:]

        elif (twirl_sum <= - twirl_length + 2):
            # counter-clockwise twirl
            print "COUNTER-CLOCKWISE"
            self.emit_event(self.EVENT_TWIRL, -1)
            self.__twirling = self.__twirling[1:]

        else:
            # not a valid twirl
            print "---"
            self.__twirling = []


    def __swipe(self, direction):

        self.__swiping.append(direction)
            
            
    def __check_swiping(self):

        directions = []
        for d in self.__swiping:
            if (d == _DIRECTION_W):
                directions.append(-1)
            elif (d == _DIRECTION_E):
                directions.append(1)
            else:
                directions.append(0)
        #end for
        
        # is it a valid swipe?
        swipe_sum = reduce(lambda a,b: a + b, directions)
        swipe_length = len(directions)

        if (swipe_sum == swipe_length or swipe_sum == -swipe_length):
            self.emit_event(self.EVENT_SWIPE, directions[0])

