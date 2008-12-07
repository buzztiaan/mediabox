"""
Every widget is derived from this base class.
"""

import time
import threading


class Widget(object):
    """
    Base class for GDK based lightweight widgets.
    """

    EVENT_BUTTON_PRESS = 0
    EVENT_BUTTON_RELEASE = 1
    EVENT_MOTION = 2
    
    
    # static lock for blocking event handling
    __events_lock = threading.Event()

    # static lock for animations
    __animation_lock = threading.Event()

    # widget instances
    __instances = []

    _esens = None
        

    def __init__(self):
        """
        Creates and initializes a new Widget object.
        Be sure to invoke this constructor when deriving from this class.
        """
    
        self.__children = []
        self.__parent = None
    
        self.__event_sensor = self._esens
        self.__event_handlers = {}
        self.__is_enabled = True
        self.__is_frozen = False
        self.__is_visible = True
        self.__can_be_visible = True
        self.__skip_next_render = False
        
        self.__position = (0, 0)
        self.__size = (0, 0)
        
        self.__clip_rect = None
        
        self.__screen = None
        self.__instances.append(self)
          
          
    def send_event(self, ev, *args):
        """
        Sends the given event to this widget.
        The widget emits the event to all event handlers that are registered
        for the event.
        
        Use this method in your own widgets for emitting events.
        
        @param ev:      Type of event
        @param *args:   variable number of arguments (depending on the
                        event type)
        """

        if (self.__events_lock.isSet() or self.__animation_lock.isSet()): return
        
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


    def set_animation_lock(self, value):
        """
        Sets the global lock for blocking animations.
        
        @param value: whether the lock is set.
        """
        
        if (value):
            self.__animation_lock.set()
        else:
            self.__animation_lock.clear()
            
            
    def have_animation_lock(self):
        """
        Returns whether the animation lock is set.
        
        @return: whether the lock is set
        """
        
        return self.__animation_lock.isSet()
        


    def set_events_blocked(self, value):
        """
        Sets the global lock for blocking events. While events are blocked,
        no event handling takes place by the Widget class.
        
        @param value: whether events are blocked (True) or not (False)
        """
    
        if (value):
            self.__events_lock.set()
        else:
            self.__events_lock.clear()
    
    
    def get_children(self):
        """
        Returns a list of all child widgets of this widget.
        """
    
        return self.__children[:]
    
    
    def add(self, child):
        """
        Adds a new child to this widget. Every widget is a container and may
        thus have child widgets.
        
        @param child: child widget
        """
        
        self.__children.append(child)
        child.set_parent(self)
        child.set_screen(self.get_screen())
        self.__check_zone()
        
        
    def remove(self, child):
        """
        Removes the given child widget from this widget.
        
        @param child: child widget
        """
    
        self.__children.remove(child)
        child.set_visible(False)
        self.__check_zone()
        
        
    def set_parent(self, parent):
        """
        Sets the parent of this widget. You usually don't need this method in
        your code.
        
        @param parent: new parent widget
        """
    
        self.__parent = parent
        
        
    def get_parent(self):
        """
        Returns the parent of this widget. The parent of the root widget is
        always C{None}.
        
        @return: parent widget
        """
    
        return self.__parent
                
                
    def set_screen(self, screen):
        """
        Changes the screen pixmap to render on.
        
        @param screen: screen pixmap for rendering
        """
    
        self.__screen = screen
        for c in self.__children:
            c.set_screen(screen)
        self.__check_zones()
        
        
    def get_screen(self):
        """
        Returns the current screen pixmap for rendering.
        
        @return: screen pixmap for rendering
        """
    
        return self.__screen
        
        
    def set_clip_rect(self, *args):
        """
        Sets the clipping rectangle that can be used for this widget.
        """
    
        self.__clip_rect = args
        
        
    def use_clipping(self, value):
        """
        Activates or deactivates clipping.
        
        @param value: whether to activate (True) or deactivate (False) clipping
        """
    
        if (not self.__clip_rect): return
    
        screen = self.get_screen()
        if (value):
            screen.set_clip_rect(*self.__clip_rect)
        else:
            screen.set_clip_rect(None)
            
        
    def set_zone(self, ident, x, y, w, h):
        """
        Registers a zone at the event sensor. If the zone already exists,
        only its coordinates are updated.
        """
    
        #print "ZONE", x, y, w, h, ident
        self.__event_sensor.set_zone(ident, x, y, w, h, time.time(),
                                     self.__on_action)
        
        
    def set_enabled(self, value):
        """
        Enables or disables this widget. A disabled widget is still visible
        but does not react to user events.
        
        @param value: whether this widget is enabled
        """
        
        self.__is_enabled = value
        #print self, value
        self.__check_zone()
        
        for c in self.__children:
            c.set_enabled(value)
            
            
    def is_enabled(self):
        """
        Returns whether this widget is currently enabled and reacts to user
        events.
        
        @return: whether this widget is currently enabled
        """
    
        if (not self.is_visible()):
            return False
        else:
            return self.__is_enabled
        
        
    def set_frozen(self, value):
        """
        Freezes or thaws this widget. A frozen widget does not get rendered.
        This is useful for big update operations where you don't want the
        widget to render itself after every single step.
        
        Freezing a widget freezes all child widgets as well.
        
        @param value: whether to freeze (True) or thaw (False) this widget
        """
    
        self.__is_frozen = value
        self._visibility_changed()
        for c in self.__children:
            c.set_frozen(value)
        
        
    def is_frozen(self):
        """
        Returns whether this widget is currently frozen.
        
        @return: whether this widget is currently frozen.
        """

        return self.__is_frozen
        

    def set_visible(self, value):
        """
        Shows or hides this widget. An invisible widget does not get rendered
        and does not react to events and all descendants are invisible as well.
        
        Newly created widgets are initially visible.
        
        @param value: whether this widget is visible
        """
    
        def f(w):
            w._visibility_changed()
            for c in w.get_children():
                f(c)
    
        self.__is_visible = value
        self.__check_zones()
        f(self)


    def is_visible(self):
        """
        Returns whether this widget is currently visible.
        
        @return: whether this widget is currently visible
        """
    
        if (not self._can_be_visible()):
            return False
        else:
            return self.__is_visible
        
        
    def _visibility_changed(self):
        """
        Widgets can override this method if they want to get notified when
        the visibility changes, e.g. if an ancestor widget became invisible.
        """

        pass


    def _can_be_visible(self):
        """
        Internal method for determining whether this widget can be visible.
        If ancestor widget is invisible, then this widget is invisible as well.
        """
    
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
        """
        Returns whether this widget may currently render itself.
        
        If your widget is rendering without being initiated by the
        C{render_this} method, you have to use this method to check whether
        the widget may currently render on screen.
        
        A widget may only render if it has a screen, is visible, and is not
        frozen.
        
        @return: whether this widget may currently render
        """
    
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
            
        # don't allow the same callback twice
        for c, a in self.__event_handlers[etype]:
            if (c == cb):
                return
        #end for
            
        self.__event_handlers[etype].append((cb, args))
        self.__check_zone()


    def connect_clicked(self, cb, *args):
        """
        Connects a callback to mouse clicks. A click consists of pressing
        and releasing a button.
        
        @param cb: the callback function
        @param *args: variable list of user arguments
        """
        
        self._connect(self.EVENT_BUTTON_RELEASE,
                      lambda x,y,*a:cb(*a),
                      *args)


    def connect_button_pressed(self, cb, *args):
        """
        Connects a callback to pressing a mouse button.
        
        @param cb: the callback function
        @param *args: variable list of user arguments
        """
    
        self._connect(self.EVENT_BUTTON_PRESS,
                      lambda x,y,*a:cb(x, y, *a),
                      *args)
                     
                     
    def connect_button_released(self, cb, *args):
        """
        Connects a callback to releasing a mouse button.
        
        @param cb: the callback function
        @param *args: variable list of user arguments
        """

    
        self._connect(self.EVENT_BUTTON_RELEASE,
                      lambda x,y,*a:cb(x, y, *a),
                      *args)


    def connect_pointer_moved(self, cb, *args):
        """
        Connects a callback to moving the mouse.
        
        @param cb: the callback function
        @param *args: variable list of user arguments
        """
    
        self._connect(self.EVENT_MOTION,
                      lambda x,y,*a:cb(x, y, *a),
                      *args)
    


    def set_pos(self, x, y):
        """
        Sets the position of this widget relative to its parent's coordinates.
        
        @param x: x coordinate
        @param y: y coordinate
        """
    
        self.__position = (x, y)
        self.__check_zones()
        
        
    def get_pos(self):
        """
        Returns the position of this widget relative to its parent's
        coordinates.
        
        @return: a tuple (x, y) containing the coordinates
        """
    
        return self.__position
        
        
    def get_screen_pos(self):
        """
        Returns the absolute position of this widget, i.e. the position it
        has on the root widget.
        
        @return: a tuple (x, y) containing the coordinates
        """
    
        if (self.__parent):
            parx, pary = self.__parent.get_screen_pos()
        else:
            parx, pary = (0, 0)
        x, y = self.get_pos()
        
        return (parx + x, pary + y)
        
        
    def set_size(self, w, h):
        """
        Sets the size of this widget.
        
        @param w: width
        @param h: height
        """
    
        self.__size = (w, h)
        self.__check_zone()
        
        
    def get_size(self):
        """
        Returns the size of this widget. With some widgets this may differ
        from the actual physical size.
        
        @return: a tuple (width, height) holding the size
        """
    
        return self.__size
        
        
    def set_geometry(self, x, y, w, h):
        """
        Convenience method for setting the position and size at the same time.
        
        @param x: x coordinate
        @param y: y coordinate
        @param w: width
        @param h: height
        """
    
        self.set_pos(x, y)
        self.set_size(w, h)


    def get_physical_size(self):
        """
        Returns the physical size of this widget. Widgets whose physical size
        can differ from the size must override this method. E.g. a height of
        '0' means dynamic height for a label, but the physical size contains
        the actual height.
        
        @return: a tuple (width, height) holding the size
        """
    
        return self.get_size()

    
    def render_this(self):
        """
        Widgets override this method for drawing operations. This is also the
        correct place for layouters to change the geometry of their child
        widgets dynamically.

        This method gets invoked automatically by the framework. Do not place
        calls of this method in your code. Use the C{render} method instead.
        """
    
        pass


    def overlay_this(self):
        """
        Widgets may override this method for overlay effects. This method is
        invoked after all children of this widget have been rendered.

        This method gets invoked automatically by the framework. Do not place
        calls of this method in your code. Use the C{render} method instead.
        """
    
        pass


    def render(self):
        """
        Renders this widget onto the current screen pixmap.
        """
    
        if (self.__skip_next_render):
            self.__skip_next_render = False
            return
            
        if (not self.may_render()):
            return
        
        self.render_this()
        for c in self.__children:
            if (c.is_visible()):
                c.render()

        self.overlay_this()


    def render_all(self):
        """
        Renders the whole widget hierarchy beginning at the root widget.
        """
    
        if (self.__parent):
            self.__parent.render_all()
        else:
            self.render()


    def render_at(self, screen, x = 0, y = 0):
        """
        Renders this widget onto the given pixmap at the given position.
        This is used for offscreen rendering.
        
        @param screen: screen pixmap to render on
        @param x: x coordinate
        @param y: y coordinate
        """
    
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
        
        
    def skip_next_render(self):
        """
        Skips the next rendering action.

        @todo: this sounds like a hack. is this method still used?
        """
        
        self.__skip_next_render = True
        
        
        
    def propagate_theme_change(self):
        """
        Propagates a theme change along the entire widget hierarchy when
        issued on the root widget. This causes all widgets to reload their
        graphics.
        """
    
        #self._reload()
        for c in self.__instances:
            c._reload()
            #c.propagate_theme_change()
            
            
    def _reload(self):
        """
        Widgets which have to reload graphics when the theme changes have to
        override this method so that they can get notified about a theme
        change.
        """
    
        pass


    def get_event_sensor(self):
        """
        Returns the event sensor of the widget hierarchy. This is a GTK widget.
        
        @return: event sensor
        """
    
        return self.__event_sensor
        
        
    def get_window(self):
        """
        Returns the GTK window of the widget hierarchy.
        
        @return: window
        """
    
        return self.get_event_sensor()
        

    @staticmethod
    def set_event_sensor(esens):
        """
        Sets the event sensor of this widget hierarchy. This has only to be
        done once.
        
        @param esens: event sensor
        """
        
        Widget._esens = esens

