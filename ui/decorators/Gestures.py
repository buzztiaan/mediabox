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
_ACTION_WAIT = 3

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
        
        self.__actions = []
        self.__is_recording = False
        self.__detection_handler = None
        self.__is_button_pressed = False
        
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


    def __check_for_gesture(self):
    
        state = _STATE_NONE
        wait_count = 0
        px, py = 0, 0
        
        for entry in self.__actions:
            act = entry[0]

            if (act == _ACTION_WAIT):
                wait_count += 1
            else:
                wait_count == 0

            if (state == _STATE_NONE):
                if (act == _ACTION_PRESS):
                    nil, px, py = entry
                    state = _STATE_HOLD

            elif (state == _STATE_HOLD):
                if (act == _ACTION_RELEASE):
                    nil, px, py = entry
                    state = _STATE_TAP
                elif (act == _ACTION_WAIT and wait_count > 10):
                    # HOLD
                    print "HOLD"
                    self.emit_event(self.EVENT_HOLD, px, py)
                    return True

            elif (state == _STATE_TAP):
                if (act == _ACTION_PRESS):
                    nil, px, py = entry
                    state = _STATE_TAP_HOLD
                elif (act == _ACTION_WAIT and wait_count > 5):
                    # TAP
                    print "TAP"
                    self.emit_event(self.EVENT_TAP, px, py)
                    return True
            
            elif (state == _STATE_TAP_HOLD):
                if (act == _ACTION_RELEASE):
                    nil, px, py = entry
                    state = _STATE_TAP_TAP
                elif (act == _ACTION_WAIT and wait_count > 10):
                    # TAP HOLD
                    print "TAP HOLD"
                    self.emit_event(self.EVENT_TAP_HOLD, px, py)
                    return True

            elif (state == _STATE_TAP_TAP):
                # TAP TAP
                print "TAP TAP"
                self.emit_event(self.EVENT_TAP_TAP, px, py)
                return True

        #end for

        return False


    def __detect_gesture(self):
    
        if (self.__check_for_gesture()):
            self.__is_recording = False
            self.__actions = []
            return False
        else:                        
            self.__actions.append((_ACTION_WAIT,))
            return True
        
    
    def __on_press(self, px, py):
    
        if (not self.__is_recording):
            self.__is_recording = True
            self.__detection_handler = \
                gobject.timeout_add(50, self.__detect_gesture)
            
        self.__actions.append((_ACTION_PRESS, px, py))
        self.__is_button_pressed = True
        
        
    def __on_release(self, px, py):

        self.__actions.append((_ACTION_RELEASE, px, py))
        self.__is_button_pressed = False

        
    def __on_motion(self, px, py):
    
        if (not self.__is_button_pressed): return
    
        self.__actions.append((_ACTION_MOTION, px, py))
        
        """
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
        else:
            return
            
        #self.__twirl(direction)
        self.__swipe(direction)
        try:
            self.__state = _TRANSITIONS[(self.__state, _ACTION_MOTION)]
        except:
            pass
        self.__detect_event()
        """
        
