class Widget(object):

    EVENT_BUTTON_PRESS = 0
    EVENT_BUTTON_RELEASE = 1
    EVENT_MOTION = 2
    

    def __init__(self, esens):
    
        self.__children = []
        self.__parent = None
    
        self.__event_sensor = esens
        self.__event_handlers = {}
        self.__is_enabled = True
        self.__is_frozen = False
        self.__is_visible = True
        self.__can_be_visible = True
        
        self.__position = (0, 0)
        self.__size = (0, 0)
        
        self.__screen = None
          
        
    def __on_action(self, etype, px, py):
    
        x, y = self.get_screen_pos()
        handlers = self.__event_handlers.get(etype, [])
        for cb, args in handlers:
            try:
                px -= x
                py -= y
                cb(px, py, *args)
            except:
                import traceback; traceback.print_exc()
                pass
        #end for
    
    
    def add(self, child):
        
        self.__children.append(child)
        child.set_parent(self)
        child.set_screen(self.get_screen())
        self.__check_zone()
        
        
    def set_parent(self, parent):
    
        self.__parent = parent
                
                
    def set_screen(self, screen):
    
        self.__screen = screen
        for c in self.__children:
            c.set_screen(screen)
        self.__check_zones()
        
        
    def get_screen(self):
    
        return self.__screen
        
        
    def set_zone(self, ident, x, y, w, h):
    
        #print "ZONE", x, y, w, h, ident
        self.__event_sensor.set_zone(ident, x, y, w, h, self.__on_action)
        
        
    def set_enabled(self, value):
        
        self.__is_enabled = value
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

        
    def connect(self, etype, cb, *args):
    
        if (not etype in self.__event_handlers):
            self.__event_handlers[etype] = []
            
        self.__event_handlers[etype].append((cb, args))
        self.__check_zone()


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
        
