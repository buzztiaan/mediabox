class State(object):

    def __init__(self, name, on_enter = None, on_leave = None):
   
        self.__name = name
        self.__on_enter = on_enter
        self.__on_leave = on_leave


    def __str__(self):
    
        return "STATE: " + self.__name


    def __call__(self, on_enter = None, on_leave = None):
   
        self.__on_enter = on_enter
        self.__on_leave = on_leave


    def enter(self, sm):
    
        if (self.__on_enter):
            self.__on_enter(sm)


    def leave(self, sm):
        
        if (self.__on_leave):
            self.__on_leave(sm)


class StateMachine(object):

    def __init__(self, initial_state, transitions):
    
        self.__transitions = transitions
        self.__properties = {}
    
        self.__state = initial_state
        initial_state.enter(self)
        
        
    def send_input(self, new_input):
    
        # check states
        moved = False
        for item in self.__transitions:
            src_state, trans_input, trans_guard, dest_state = item

            if (src_state != self.__state or trans_input != new_input): continue
            
            if (trans_guard(self)):
                moved = True
                print "%s (%s) -> %s" \
                       % (str(src_state), str(new_input), str(dest_state))
                if (src_state != dest_state):
                    src_state.leave(self)
                    self.__state = dest_state
                    dest_state.enter(self)
                #end if
                break
            #end if

        #end for
        
        # process immediate transitions
        if (moved):
            self.send_input(None)


    def set_property(self, key, value):
    
        self.__properties[key] = value
        
        
    def get_property(self, key, default = None):
    
        return self.__properties.get(key, default)


    def has_property(self, key):
    
        return self.__key in self.__properties

        
if (__name__ == "__main__"):

    # define states
    STATE_NONE = State()
    STATE_LOADED = State()
    STATE_PLAYING = State()
    STATE_PAUSED = State()

    # define input
    INPUT_LOAD = 0
    INPUT_PLAY = 1
    INPUT_SEEK = 2
    INPUT_PAUSE = 3
    INPUT_EOF = 4
    INPUT_IDLE = 5
    INPUT_RESUME = 6

    guard = lambda x: True

    # define transitions
    TRANSITIONS = [
      ( STATE_NONE,     INPUT_LOAD,    guard,     STATE_LOADED  ),
      ( STATE_LOADED,   INPUT_PLAY,    guard,     STATE_PLAYING ),
      ( STATE_LOADED,   INPUT_SEEK,    guard,     STATE_PLAYING ),
      ( STATE_PLAYING,  INPUT_SEEK,    guard,     STATE_PLAYING ),
      ( STATE_PLAYING,  INPUT_PAUSE,   guard,     STATE_PAUSED  ),
      ( STATE_PLAYING,  INPUT_EOF,     guard,     STATE_LOADED  ),
      ( STATE_PAUSED,   INPUT_PAUSE,   guard,     STATE_EOF     ),
      ( STATE_PAUSED,   INPUT_SEEK,    guard,     STATE_PLAYING ),
      ( STATE_PAUSED,   INPUT_IDLE,    guard,     STATE_NONE    ),
    ]
    
    sm = StateMachine(STATE_NONE, TRANSITIONS)
    
