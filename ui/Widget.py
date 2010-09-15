"""
Every widget is derived from this base class.
"""

from utils.EventEmitter import EventEmitter
from utils import logging

import time
import threading
import gtk
import gobject


class Widget(EventEmitter):
    """
    Base class for GDK based lightweight widgets.
    """

    EVENT_BUTTON_PRESS = "button-pressed"
    EVENT_BUTTON_RELEASE = "button-released"
    EVENT_MOTION = "motion"
    EVENT_KEY_PRESSED = "key-pressed"
    EVENT_KEY_RELEASED = "key-released"
    
    SLIDE_LEFT = 0
    SLIDE_RIGHT = 1
    SLIDE_UP = 2
    SLIDE_DOWN = 3
    
    # static lock for animations
    __animation_lock = threading.Event()

    # all widget instances
    __instances = []

    # event zones; table: ident -> (window, x, y, w, h, tstamp, cb)
    #_zones = {}

        

    def __init__(self):
        """
        Creates and initializes a new Widget object.
        Be sure to invoke this constructor when deriving from this class.
        """
    
        # known actors
        #self.__actors_stack = []
    
        # younger widgets have precedence over older ones in event handling
        #self.__age_tstamp = 0
    
        self.__children = []
        self.__parent = None
    
        self.__locked_zone = None
        #self.__need_to_check_zones = False
        
        self.__is_enabled = True
        self.__is_frozen = False
        self.__is_visible = True
        self.__can_be_visible = True
        self.__skip_next_render = False
        
        self._input_focus_widget = None
        
        self.__position = (0, 0)
        self.__size = (0, 0)

        # render overlay handlers
        self.__overlayers = []
        
        self.__clip_rect = None
        
        self.__screen = None
        self.__instances.append(self)

        EventEmitter.__init__(self)


    """
    def push_actor(self, w):
        ""
        Pushes an actor widget onto the actors stack. All but the topmost actor
        on the stack are frozen.
        @since: 0.96.5
        
        @param w: a widget
        ""
        
        if (self.__parent):
            self.__parent.push_actor(w)
        else:
            self.__actors_stack.append(w)
            self.__update_actors()
        
        
    def pop_actor(self):
        ""
        Pops the topmost actor widget from the actors stack.
        @since: 0.96.5
        ""
        
        if (self.__parent):
            self.__parent.pop_actor()
        elif (self.__actors_stack):
            actor = self.__actors_stack.pop()
            actor.set_frozen(True)
            self.__update_actors()
        
        
    def __update_actors(self):
        
        if (self.__actors_stack):
            for actor in self.__actors_stack[:-1]:
                actor.set_frozen(True)

            self.__actors_stack[-1].set_frozen(False)
    """
   
            
    def grab_focus(self):
        """
        Grabs the focus for keyboard input.
        """
        
        win = self.get_window()
        win._input_focus_widget = self
        
        
    def _find_zone_at(self, px, py, ev_name):
    
        #print "CHECKING", self
        if (self.is_frozen() or not self.is_visible()):
            return None
            
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        if (not x <= px <= x + w or not y <= py <= y + h):
            return None
            
        #print "CHILDREN", self.__children
        for i in range(len(self.__children) - 1, -1, -1):
            c = self.__children[i]
            zone = c._find_zone_at(px, py, ev_name)
            #print "CHILD", c, zone
            if (zone):
                return zone
        #end for
        
        if (self.has_events): #(ev_name)):
            return self.__on_action
        else:
            return None
        
        
          
    def _handle_event(self, ev, px, py, *args):
    
        zone = None
        #zone_tstamp = -1
        
        if (ev == Widget.EVENT_BUTTON_PRESS):
            zone = self._find_zone_at(px, py, ev)
            #print "ZONE", px, py, zone
                
            """
            for wdgt in self._zones:
                if (wdgt.is_frozen()):
                    continue
                
                window, x, y, w, h, tstamp, cb = self._zones[wdgt]

                if (window != self.get_window()):
                    continue

                if (x <= px <= x + w and y <= py <= y + h and tstamp > zone_tstamp):
                    zone = cb
                    zone_tstamp = tstamp
            #end for
            """
        
            if (zone):            
                self.__locked_zone = zone
            else:
                self.__locked_zone = None

        else:
            zone = self.__locked_zone
            

        if (zone):
            self.__locked_zone = zone
            cb = zone
            cb(ev, px, py, *args)

          
          
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
       
        self.emit_event(ev, *args)

        """
        if (ev in (self.EVENT_KEY_PRESS, self.EVENT_KEY_RELEASE) and
              self._input_focus_widget and
              self._input_focus_widget.is_visible()):
            self._input_focus_widget.send_event(ev, *args)
        
        else:
            self.emit_event(ev, *args)
        """
        
        
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

    
    def add_overlayer(self, overlayer):
    
        self.__overlayers.append(overlayer)


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
        #child.set_screen(self.get_screen())
        #self.__check_zone()
        
        
    def remove(self, child):
        """
        Removes the given child widget from this widget.
        
        @param child: child widget
        """
    
        self.__children.remove(child)
        child.set_visible(False)
        #self.__check_zone()
        
        
    def set_parent(self, parent):
        """
        Sets the parent of this widget. You usually don't need this method in
        your code.
        
        @param parent: new parent widget
        """
    
        self.__parent = parent
        self.__age_tstamp = time.time()
        
        
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
        #for c in self.__children:
        #    c.set_screen(screen)
        #self.__check_zones()
        
        
    def get_screen(self):
        """
        Returns the current screen pixmap for rendering.
        
        @return: screen pixmap for rendering
        """

        if (self.__screen or not self.__parent):
            return self.__screen
        else:
            return self.__parent.get_screen()
        
        
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
            
        
    def __set_zone(self, ident, x, y, w, h):
        """
        Registers an event zone. If the zone already exists, only its
        coordinates are updated.
        """
    
        #print "ZONE", x, y, w, h, ident, self.get_window()
        self._zones[ident] = (self.get_window(), x, y, w, h, self.__age_tstamp, self.__on_action)
        
        #if (self.__event_sensor):
        #    self.__event_sensor.set_zone(ident, x, y, w, h, time.time(),
        #                                 self.__on_action)
        
        
    def __remove_zone(self, ident):
        """
        Removes the given event zone.
        """
        
        if (ident in self._zones):
            del self._zones[ident]
    
        
    def set_enabled(self, value):
        """
        Enables or disables this widget. A disabled widget is still visible
        but does not react to user events.
        
        @param value: whether this widget is enabled
        """
        
        self.__is_enabled = value
        #print self, value
        #self.__check_zone()
        
        for c in self.__children:
            c.set_enabled(value)
            
            
    def is_enabled(self):
        """
        Returns whether this widget is currently enabled and reacts to user
        events.
        
        @return: whether this widget is currently enabled
        """
    
        if (not self.is_visible() or not self.get_window().has_focus()):
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
        #self.__check_zones()
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
        #self.__check_zone()
                
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
    
        return (self.get_screen() and self.is_visible() and
                not self.is_frozen() and
                self.__size[0] > 0 and self.__size[1] > 0)
        

    """
    def __check_zone(self):
    
        # don't check zone when widget does not have event handlers
        #if (not self.__event_handlers): return
        if (not self.has_events()): return
    
        if (self.is_enabled()):
            x, y = self.get_screen_pos()
            w, h = self.get_size()
            self.__set_zone(self, x, y, w, h)
        else:
            self.__remove_zone(self)
            
            
    def __check_zones(self):
    
        self.__need_to_check_zones = False
        self.__check_zone()
        for c in self.__children:
            c.__check_zones()
    """


        
    """
    def _connect(self, etype, cb, *args):
        ""
        Connects a callback to an event type. This is a low-level function
        and should only be used when implementing new widgets.
        ""
    
        EventEmitter._connect(self, etype, cb, *args)
        self.__check_zone()
    """


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


    def connect_key_pressed(self, cb, *args):
        """
        Connects a callback to pressing a key.
        
        @param cb: the callback function
        @param *args: variable list of user arguments
        """
    
        self._connect(self.EVENT_KEY_PRESSED,
                      lambda key,*a:cb(key, *a),
                      *args)
                      

    def connect_key_released(self, cb, *args):
        """
        Connects a callback to releasing a key.
        
        @param cb: the callback function
        @param *args: variable list of user arguments
        """
    
        self._connect(self.EVENT_KEY_RELEASED,
                      lambda key,*a:cb(key, *a),
                      *args)

    def set_pos(self, x, y):
        """
        Sets the position of this widget relative to its parent's coordinates.
        
        @param x: x coordinate
        @param y: y coordinate
        """
    
        if ((x, y) != self.__position):
            self.__position = (x, y)
            #self.__need_to_check_zones = True
            #self.__check_zones()
        
        
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
    
        if ((w, h) != self.__size):
            self.__size = (w, h)
            #self.__need_to_check_zones = True
            #self.__check_zone()
        
        
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


    def render_overlays(self, screen):
        """
        Invokes the registered overlay handlers on the given screen. The screen
        is usually an offscreen buffer.
        """
        
        for o in self.__overlayers:
            try:
                o(self, screen)
            except:
                pass
        #end for


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
        
        #logging.debug("rendering widget %s", `self`)
        #if (self.__need_to_check_zones):
        #    self.__check_zones()

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
        #self.__check_zones()


    def render_buffered(self, buf):
        """
        Renders this widget on screen using the given buffer for flicker-free
        rendering.
        
        @param buf: offscreen buffer
        """

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        self.render_at(buf)
        self.get_screen().copy_buffer(buf, 0, 0, x, y, w, h)

        
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
        Widgets which have to clear caches when the theme changes have to
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
        
        
    """
    def set_window(self, win):
    
        self.__window = win
        #try:
        #win.set_widget_for_events(self)
        self.__need_to_check_zones = True
        #except:
        #    logging.error("window object %s must implement method " \
        #                  "set_widget_for_events" % win)
    """ 
        
    def get_window(self):
        """
        Returns the GTK window of the widget hierarchy.
        
        @return: window
        """
    
        if (self.__parent):
            return self.__parent.get_window()
        else:
            return None
        

    def animate(self, fps, cb, *args):
        """
        Runs an animation with the given number of frames per second.
        Invokes the given callback for each frame.
        Events occuring during the animation get discarded.
        
        @param fps:   frames per second
        @param cb:    frame callback
        @param *args: variable list of arguments for callback
        """
    
        delta = 1.0 / float(fps)
        next = time.time()
        while (True):
            #print next
            while (time.time() < next): time.sleep(0.00001)
            ret = cb(*args)
            gtk.gdk.window_process_all_updates()
            next += delta
            if (not ret): break
        #end for
        
        # kill queued events
        while (True):
            e = gtk.gdk.event_get()
            if (not e): break


    def animate_with_events(self, fps, cb, *args):
        """
        Runs an animation with the given number of frames per second.
        Invokes the given callback for each frame.
        Events are detected during animation.
        
        @param fps:   frames per second
        @param cb:    frame callback
        @param *args: variable list of arguments for callback
        """
    
        delta = 1.0 / float(fps)
        next = time.time()
        while (True):
            # TODO: this stuff should be put into a function in utils
            gobject.timeout_add(int(delta*1000), lambda : False)
            while (time.time() < next):
                cnt = 0
                while (gtk.events_pending() and cnt < 10):
                    gtk.main_iteration(True)
                    cnt += 1
                    
            ret = cb(*args)
            gtk.gdk.window_process_all_updates()
            next += delta
            if (not ret): break
        #end for



    def fx_slide_horizontal(self, buf, x, y, w, h, direction):

        def fx(params):
            from_x, to_x = params
            dx = (to_x - from_x) / 3

            if (dx > 0):
                if (direction == self.SLIDE_LEFT):
                    screen.move_area(scr_x + x + dx, scr_y + y,
                                     w - dx, h,
                                     -dx, 0)
                    screen.copy_pixmap(buf,
                                       x + from_x, y,
                                       scr_x + x + w - dx, scr_y + y,
                                       dx, h)
                else:
                    screen.move_area(scr_x + x, scr_y + y,
                                     w - dx, h,
                                     dx, 0)
                    screen.copy_pixmap(buf,
                                       x + w - from_x - dx, y,
                                       scr_x + x, scr_y + y,
                                       dx, h)

                params[0] = from_x + dx
                params[1] = to_x
                return True

            else:
                dx = to_x - from_x
                if (direction == self.SLIDE_LEFT):
                    screen.move_area(scr_x + x + dx, scr_y + y,
                                     w - dx, h,
                                     -dx, 0)
                    screen.copy_pixmap(buf,
                                       x + from_x, y,
                                       scr_x + x + w - dx,
                                       scr_y + y,
                                       dx, h)
                else:
                    screen.move_area(scr_x + x, scr_y + y,
                                     w - dx, h,
                                     dx, 0)
                    screen.copy_pixmap(buf,
                                       x + w - from_x - dx, y,
                                       scr_y + x, scr_y + y,
                                       dx, h)
                
                return False


        if (not self.may_render()): return

        scr_x, scr_y = self.get_screen_pos()
        screen = self.get_screen()

        import platforms
        if (False): #not platforms.MAEMO5):
            screen.copy_pixmap(buf, x, y, scr_x + x, scr_y + y, w, h)
        else:
            self.animate(50, fx, [0, w])


    def fx_slide_vertical(self, buf, x, y, w, h, direction):

        def fx(params):
            from_y, to_y = params
            dy = (to_y - from_y) / 3

            if (dy > 0):
                if (direction == self.SLIDE_UP):
                    screen.move_area(scr_x + x, scr_y + y + dy,
                                     w, h - dy,
                                     0, -dy)
                    screen.copy_pixmap(buf,
                                       x, y + from_y,
                                       scr_x + x, scr_y + y + h - dy,
                                       w, dy)
                else:
                    screen.move_area(scr_x + x, scr_y + y,
                                     w, h - dy,
                                     0, dy)
                    screen.copy_pixmap(buf,
                                       x, y + h - from_y - dy,
                                       scr_x + x, scr_y + y,
                                       w, dy)

                params[0] = from_y + dy
                params[1] = to_y
                return True

            else:
                dy = to_y - from_y
                if (direction == self.SLIDE_UP):
                    screen.move_area(scr_x + x, scr_y + y + dy,
                                     w, h - dy,
                                     0, -dy)
                    screen.copy_pixmap(buf,
                                       x, y + from_y,
                                       scr_x + x,
                                       scr_y + y + h - dy,
                                       w, dy)
                else:
                    screen.move_area(scr_x + x, scr_y + y,
                                     w, h - dy,
                                     0, dy)
                    screen.copy_pixmap(buf,
                                       x, y + h - from_y,
                                       scr_y + x, scr_y + y,
                                       w, dy)
                
                return False


        if (not self.may_render()): return

        scr_x, scr_y = self.get_screen_pos()
        screen = self.get_screen()

        import platforms
        if (False): #not platforms.MAEMO5):
            screen.copy_pixmap(buf, x, y, scr_x + x, scr_y + y, w, h)
        else:
            self.animate(50, fx, [0, h])

