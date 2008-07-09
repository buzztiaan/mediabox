import time


class Widget(object):
    """
    Base class for GDK based lightweight widgets.
    """

    EVENT_BUTTON_PRESS = 0
    EVENT_BUTTON_RELEASE = 1
    EVENT_MOTION = 2
    
    
    # static flag for blocking event handling
    __events_blocked = [False]


    _esens = None
        

    def __init__(self):
    
        self.__children = []
        self.__parent = None
    
        self.__event_sensor = self._esens
        self.__event_handlers = {}
        self.__is_enabled = True
        self.__is_frozen = False
        self.__is_visible = True
        self.__can_be_visible = True
        
        self.__position = (0, 0)
        self.__size = (0, 0)
        
        self.__screen = None
          
          
    def send_event(self, ev, *args):
        """
        Sends the given event. The widget emits the event to all event handlers
        registered for the event.
        """

        if (self.__events_blocked[0]): return
        
        handlers = self.__event_handlers.get(ev, [])
        for cb, user_args in handlers:
            try:
                cb(*(args + user_args))
            except:
                import traceback; traceback.print_exc()
        #end for
    
        
        
    def __on_action(self, etype, px, py):

        x, y = self.get_screen_pos()
        px2 = px - x
        py2 = py - y
    
        self.send_event(etype, px2, py2)


    def set_events_blocked(self, value):
        """
        Sets the global flag for blocking events. While events are blocked,
        no event handling takes place by the Widget class.
        """
    
        self.__events_blocked[0] = value
    
    
    def get_children(self):
    
        return self.__children[:]
    
    
    def add(self, child):
        
        self.__children.append(child)
        child.set_parent(self)
        child.set_screen(self.get_screen())
        self.__check_zone()
        
        
    def remove(self, child):
    
        self.__children.remove(child)
        self.__check_zone()
        
        
    def set_parent(self, parent):
    
        self.__parent = parent
        
        
    def get_parent(self):
    
        return self.__parent
                
                
    def set_screen(self, screen):
    
        self.__screen = screen
        for c in self.__children:
            c.set_screen(screen)
        self.__check_zones()
        
        
    def get_screen(self):
    
        return self.__screen
        
        
    def set_zone(self, ident, x, y, w, h):
    
        #print "ZONE", x, y, w, h, ident
        self.__event_sensor.set_zone(ident, x, y, w, h, time.time(),
                                     self.__on_action)
        
        
    def set_enabled(self, value):
        
        self.__is_enabled = value
        #print self, value
        self.__check_zone()
        
        for c in self.__children:
            c.set_enabled(value)
            
            
    def is_enabled(self):
    
        if (not self.is_visible()):
            return False
        else:
            return self.__is_enabled
        
        
    def set_frozen(self, value):
    
        self.__is_frozen = value
        for c in self.__children:
            c.set_frozen(value)
        
    def is_frozen(self):
    
        return self.__is_frozen
        
        
    def is_visible(self):
    
        if (not self._can_be_visible()):
            return False
        else:
            return self.__is_visible
        
        
    def set_visible(self, value):
    
        self.__is_visible = value
        self.__check_zones()
        
                        
                
    def _can_be_visible(self):
    
        if (self.__parent):
            return self.__is_visible and self.__parent._can_be_visible()
        else:
            return self.__is_visible
                
    
    def _set_can_be_visible(self, value):
    
        self.__can_be_visible = value
        self.__check_zone()
                
        for c in self.__children:
            c._set_can_be_visible(value)


    def may_render(self):
    
        return (self.__screen and self.is_visible() and not self.is_frozen())
        

    def __check_zone(self):
    
        if (self.is_enabled() and self.__event_handlers):
            x, y = self.get_screen_pos()
            w, h = self.get_size()
            self.set_zone(self, x, y, w, h)
        else:
            self.__event_sensor.remove_zone(self)
            
            
    def __check_zones(self):
    
        self.__check_zone()
        for c in self.__children:
            c.__check_zones()

        
    def _connect(self, etype, cb, *args):
        """
        Connects a callback to an event type. This is a low-level function
        and should only be used when implementing new widgets.
        """
    
        if (not etype in self.__event_handlers):
            self.__event_handlers[etype] = []
            
        self.__event_handlers[etype].append((cb, args))
        self.__check_zone()


    def connect_clicked(self, cb, *args):
        
        self._connect(self.EVENT_BUTTON_RELEASE,
                      lambda x,y,*a:cb(*a),
                      *args)


    def connect_button_pressed(self, cb, *args):
    
        self._connect(self.EVENT_BUTTON_PRESS,
                      lambda x,y,*a:cb(x, y, *a),
                      *args)
                     
                     
    def connect_button_released(self, cb, *args):
    
        self._connect(self.EVENT_BUTTON_RELEASE,
                      lambda x,y,*a:cb(x, y, *a),
                      *args)


    def connect_pointer_moved(self, cb, *args):
    
        self._connect(self.EVENT_MOTION,
                      lambda x,y,*a:cb(x, y, *a),
                      *args)
    


    def set_pos(self, x, y):
    
        self.__position = (x, y)
        self.__check_zones()
        
        
    def get_pos(self):
    
        return self.__position
        
        
    def get_screen_pos(self):
    
        if (self.__parent):
            parx, pary = self.__parent.get_screen_pos()
        else:
            parx, pary = (0, 0)
        x, y = self.get_pos()
        
        return (parx + x, pary + y)
        
        
    def set_size(self, w, h):
    
        self.__size = (w, h)
        self.__check_zone()
        
        
    def get_size(self):
    
        return self.__size
        
        
    def set_geometry(self, x, y, w, h):
    
        self.set_pos(x, y)
        self.set_size(w, h)


    def get_physical_size(self):
    
        return self.__size

    
    def render_this(self):
    
        pass


    def render(self):
    
        if (not self.may_render()): return
        
        self.render_this()
        for c in self.__children:
            if (c.is_visible()):
                c.render()


    def render_at(self, screen, x = 0, y = 0):
    
        real_x, real_y = self.__position
        parent = self.__parent
        real_screen = self.__screen
        
        self.__parent = None
        self.set_screen(screen)
        self.set_pos(x, y)
        
        self.render()
        
        self.__parent = parent
        self.set_screen(real_screen)
        self.set_pos(real_x, real_y)
        
        
    def propagate_theme_change(self):
    
        self._reload()
        for c in self.__children:
            c.propagate_theme_change()
            
            
    def _reload(self):
    
        pass


    def get_event_sensor(self):
    
        return self.__event_sensor
        
        
    def get_window(self):
    
        return self.get_event_sensor()
        

    @staticmethod
    def set_event_sensor(esens):
        
        Widget._esens = esens

