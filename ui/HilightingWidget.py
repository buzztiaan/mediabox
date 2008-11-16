from Widget import Widget
from Pixmap import Pixmap

import gobject


class HilightingWidget(Widget):
    """
    Base class for widgets with a hovering smoothly animated hilighting box.
    """

    def __init__(self):
    
        # buffer for rendering the motion
        self.__motion_buffer = Pixmap(None, 64, 64)
        
        # buffer for saving the background
        self.__buffer = None
        
        # pixbuf for the hilighting box
        self.__hilight_box = None
        
        # current position of the hilighting box
        self.__box_pos = (0, -1000)
        
        # handle of the motion timer
        self.__motion_timer = None
        
    
        Widget.__init__(self)
        
        
    def _reload(self):
    
        self.__buffer = None
        
        
    def overlay_this(self):
    
        x, y = self.__box_pos
        self.__move_cursor(x, y, 0, 0)


    def set_hilighting_box(self, pbuf):
        """
        Sets the hilighting box from a pixbuf image.
        
        @param pbuf: pixbuf image for the box
        """
    
        self.__hilight_box = pbuf


    def move_hilighting_box(self, new_x, new_y, cb, *user_args):
        """
        Moves the hilighting box to the given position.
        
        @param new_x:      x coordinate
        @param new_y:      y coordinate
        @param cb:         callback to invoke when finished
        @param *user_args: user arguments for the callback
        """
    
        def move_box(from_x, from_y, to_x, to_y):
            dx = (to_x - from_x) / 5
            dy = (to_y - from_y) / 5
            if (abs(dx) > 0 or abs(dy) > 0):
                self.__move_cursor(from_x, from_y, dx, dy)
                self.__box_pos = (from_x + dx, from_y + dy)
                self.__motion_timer = gobject.timeout_add(10, move_box,
                                                       from_x + dx, from_y + dy,
                                                       to_x, to_y)
            else:
                self.__move_cursor(from_x, from_y, to_x - from_x, to_y - from_y)
                self.__box_pos = (to_x, to_y)
                self.__motion_timer = None
                if (cb):
                    cb(*user_args)
    
    
        prev_x, prev_y = self.__box_pos
        if (self.__motion_timer):
            gobject.source_remove(self.__motion_timer)
            
        self.__motion_timer = gobject.timeout_add(10, move_box,
                                                  prev_x, prev_y, new_x, new_y)


    def __move_cursor(self, x1, y1, dx, dy):
        """
        Moves the cursor by the given amount.
        
        x,y                             
        +-----------------+  |       |     x,y     - position of motion buffer
        |x1,y1            |  |dy     |     w,h     - size of motion buffer          
        |                 |  v       |     x1,y1   - previous cursor position
        |   +-----------------+ |    |h    x2,y2   - new cursor position
        |   |x2,y2        |   | |    |     dx,dy   - offset between old and new
        +---|-------------+   | |bh  |               cursor position
            |                 | |    |     bw,bh   - size of cursor
        --->|                 | |    |     bx1,by1 - previous position of cursor
        dx  +-----------------+ V    v               in the motion buffer
                                           bx2,by2 - new position of cursor in
            ------------------>                      the motion buffer
                    bw
                   
        ---------------------->
                    w

        1. create motion buffer if necessary
        2. create buffer if necessary
        3. copy screen to motion buffer
        4. copy buffer to motion buffer at current cursor position
        5. save motion buffer at new cursor position to buffer
        6. draw cursor onto motion buffer
        7. copy motion buffer to screen
            
        """

        if (not self.may_render()): return

        screen = self.get_screen()
        scr_x, scr_y = self.get_screen_pos()
        
        x2 = x1 + dx
        y2 = y1 + dy
        bw = self.__hilight_box.get_width()
        bh = self.__hilight_box.get_height()
        x = x1 + min(dx, 0)
        y = y1 + min(dy, 0)
        w = bw + abs(dx)
        h = bh + abs(dy)
        bx1 = x1 - x
        by1 = y1 - y
        bx2 = x2 - x
        by2 = y2 - y

        if (x1 < 0 or y1 < 0): return        

        # 1. create motion buffer if necessary
        motion_buf_w, motion_buf_h = self.__motion_buffer.get_size()
        if (w > motion_buf_w or h > motion_buf_h or
            w < motion_buf_w / 2 or h < motion_buf_h / 2):
            self.__motion_buffer = Pixmap(None, w, h)

        # 2. create buffer if necessary
        if (not self.__buffer):
            self.__buffer = Pixmap(None, bw, bh)
            self.__buffer.copy_pixmap(screen, scr_x + x1, scr_y + y1,
                                      0, 0, bw, bh)
        
        # 3. copy screen to motion buffer
        self.__motion_buffer.copy_pixmap(screen, scr_x + x, scr_y + y,
                                         0, 0, w, h)
                                         
        # 4. copy buffer to motion buffer at current cursor position
        self.__motion_buffer.copy_pixmap(self.__buffer, 0, 0,
                                         bx1, by1, bw, bh)

        # 5. save motion buffer at new cursor position to buffer
        self.__buffer.copy_pixmap(self.__motion_buffer, bx2, by2,
                                  0, 0, bw, bh)

        # 6. draw cursor onto motion buffer
        #screen.copy_pixmap(self.__motion_buffer, 0, 0, 0, 0, w, h)
        self.__motion_buffer.draw_pixbuf(self.__hilight_box, x2 - x, y2 - y)
                                  
        # 7. copy motion buffer to screen        
        screen.copy_pixmap(self.__motion_buffer, 0, 0,
                           scr_x + x, scr_y + y, w, h)

