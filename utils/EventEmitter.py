import threading


class EventEmitter(object):
    """
    Abstract base class for UI objects emitting events.
    @since: 0.97
    """

    # static lock for blocking event handling
    __events_lock = threading.Event()
    
    
    def __init__(self):
    
        self.__handlers = {}
        
        
    def has_events(self):
    
        return (len(self.__handlers) > 0)


    def has_event(self, ev_name):
    
        return (ev_name in self.__handlers)


    def set_events_blocked(self, v):
    
        """
        Sets the global lock for blocking events. While events are blocked,
        no event handling takes place.
        
        @param value: whether events are blocked (True) or not (False)
        """
    
        if (value):
            self.__events_lock.set()
        else:
            self.__events_lock.clear()

        
    def _connect(self, ev_name, cb, *args):
    
        if (not ev_name in self.__handlers):
            self.__handlers[ev_name] = []

        if (not (cb, args) in self.__handlers[ev_name]):
            self.__handlers[ev_name].append((cb, args))
        
        
    def emit_event(self, ev_name, *args):

        if (self.__events_lock.isSet()): return

        for item in self.__handlers.get(ev_name, []):
            cb, u_args = item
            try:
                a = args + u_args
                cb(*a)
            except:
                import traceback; traceback.print_exc()
        #end for

