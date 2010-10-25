from Widget import Widget
from Pixmap import Pixmap, TEMPORARY_PIXMAP, text_extents
from theme import theme

import gtk


class MediaProgressBar(Widget):
    """
    Class for a progress bar with bookmark functions.
    """
    
    EVENT_CHANGED = "event-changed"
    EVENT_BOOKMARK_CHANGED = "event-bookmark-changed"
    
    
    def __init__(self):

        # background pbuf
        self.__background = None
        
        # offscreen buffer
        self.__buffer = None

        # list of bookmarks. a bookmark is a position between 0.0 and 1.0
        self.__bookmarks = []
        
        # whether the user is currently dragging
        self.__is_dragging = False
        
        # the index of the currently dragged bookmark or -1
        self.__dragged_bookmark = -1
        self.__dragged_bookmark_pos = 0.0
        self.__is_dragging_bookmark = False
        
        # the current progress as a value between 0.0 and 1.0
        self.__progress = 0
        
        # the current amount, if any
        self.__amount = 0.0
        
        # the current message if any
        self.__current_message = ""
       
        Widget.__init__(self)
        self.set_size(180, 64)

        self.connect_button_pressed(self.__on_button_press)
        self.connect_button_released(self.__on_button_release)
        self.connect_pointer_moved(self.__on_motion)


    def _reload(self):
    
        #w, h = self.get_size()
        self.__bg_pmap = None
        self.__bg_progress = None
        #self.set_size(w, h)


    def set_size(self, w, h):
    
        Widget.set_size(self, w, h)
        self.__buffer = None


    def connect_changed(self, cb, *args):
    
        self._connect(self.EVENT_CHANGED, cb, *args)


    def connect_bookmark_changed(self, cb, *args):
    
        self._connect(self.EVENT_BOOKMARK_CHANGED, cb, *args)


    def __on_button_press(self, px, py):
    
        self.__is_dragging = True
        self.__is_dragging_bookmark = False
        
        # check if the click is next to a bookmark
        w, h = self.get_size()
        cnt = 0
        for bm in self.__bookmarks:
            distance = abs(w * bm - px)
            if (distance < 20):
                self.__dragged_bookmark = cnt
                self.__dragged_bookmark_pos = bm
                break
            cnt += 1
        #end for

        self.__on_motion(px, py)


    def __on_button_release(self, px, py):
        
        if (self.__dragged_bookmark == -1):
            self.send_event(self.EVENT_CHANGED, self.__progress * 100)

        else:
            w, h = self.get_size()
            bm = self.__bookmarks[self.__dragged_bookmark]
            bm_pos = w * bm
            bm_prev_pos = w * self.__dragged_bookmark_pos

            # has the bookmark been deleted?
            if (bm < 0.001 or bm > 0.999):
                del self.__bookmarks[self.__dragged_bookmark]
                self.render()
                print "DELETED BOOKMARK"
                self.__dragged_bookmark = -1
                self.send_event(self.EVENT_BOOKMARK_CHANGED)
            
            # has the bookmark been selected?
            elif (not self.__is_dragging_bookmark):
                self.__progress = self.__dragged_bookmark_pos
                self.__bookmarks[self.__dragged_bookmark] = \
                     self.__dragged_bookmark_pos
                self.render()
                self.send_event(self.EVENT_CHANGED, self.__progress * 100)
                
            # has the bookmark been moved
            else:
                self.send_event(self.EVENT_BOOKMARK_CHANGED)
        #end if  
            
        self.__is_dragging = False
        self.__dragged_bookmark = -1


    def __on_motion(self, px, py):
            
        if (self.__is_dragging):
            w, h = self.get_size()
            px = min(w, max(0, px))
            pos = px / float(w)
            
            if (self.__dragged_bookmark != -1):
                bm_pos = px
                bm_prev_pos = w * self.__dragged_bookmark_pos

                if (not self.__is_dragging_bookmark and \
                    abs(bm_pos - bm_prev_pos) > 20):
                    self.__is_dragging_bookmark = True
                    
                # drag bookmark
                if (self.__is_dragging_bookmark):
                    self.__bookmarks[self.__dragged_bookmark] = pos
                    self.render()
                
            else:
                # drag progress slider
                self.__progress = pos
                self.render()
                
            #end if
            
            #self.set_position(px, w, dragged = True)

        #end if


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        if (not self.__buffer):
            self.__buffer = Pixmap(None, w, h)

        if (self.__background):
            self.__buffer.draw_pixbuf(self.__background, 0, 0)
        else:
            self.__buffer.fill_area(0, 0, w, h, theme.color_mb_background)
        
        #screen.fill_area(x, y + h - 24, w, 24, "#000000a0")
        self.__buffer.fill_area(0, 0, w, 48, "#00000060")
        self.__buffer.fill_area(0, 48, w, 24, "#000000")

        # render bookmarks
        for bm in self.__bookmarks:
            if (bm > 0):
                bm_pos = 16 + int((w - 32) * bm)
                self.__buffer.draw_pixbuf(theme.mb_progress_bookmark,
                        bm_pos - theme.mb_progress_bookmark.get_width() / 2,
                        16)
        #end for        

        # render position marker
        #screen.fill_area(x, y, w, 32, "#00000080")
        pos = int((w - 48) * self.__progress)
        self.__buffer.draw_pixbuf(theme.mb_progress_position_down, pos, 0)
        
        # render message
        if (self.__current_message):
            t_w, t_h = text_extents(self.__current_message, theme.font_mb_plain)
            self.__buffer.draw_text(self.__current_message, theme.font_mb_plain,
                             (w - t_w), (h - t_h) + 2,
                             theme.color_mb_gauge)

        screen.copy_buffer(self.__buffer, 0, 0, x, y, w, h)


    def set_background(self, pbuf):
    
        self.__background = pbuf


    def add_bookmark(self):
        """
        Bookmarks the current position.
        """
        
        self.__bookmarks.append(self.__progress)
        self.render()
        self.send_event(self.EVENT_BOOKMARK_CHANGED)
        
        
    def set_bookmarks(self, bookmarks):
        """
        Sets the given list of bookmarks. Pass an empty list to clear all
        bookmarks.
        
        @param bookmarks: list of bookmark positions
        """
        
        self.__bookmarks = bookmarks[:]
        self.render()


    def get_bookmarks(self):
        """
        Returns the list of bookmarks.
        
        @return: list of bookmark positions
        """
        
        return self.__bookmarks[:]
    
    
    def set_message(self, message):
    
        if (self.__current_message != message):
            self.__current_message = message
            self.render()


    def set_position(self, pos, total):

        #self.set_message("")
        if (self.__is_dragging and self.__dragged_bookmark == -1): return
        if (not self.may_render()): return
        if (total == 0): return

        new_progress = pos/float(total)
        if (abs(self.__progress - new_progress) > 0.001):            
            self.__progress = min(new_progress, 1.0)
            self.render()
        #self.send_event(self.EVENT_CHANGED, self.__progress * 100)


    def set_amount(self, amount):
        """
        Sets the amount as a value between 0.0 and 1.0.
        @since: 0.96.5
        
        @param amount: the amount value
        """

        #self.set_message("")
        if (self.__is_dragging and self.__dragged_bookmark == -1): return
        if (not self.may_render()): return
        
        if (abs(amount - self.__amount) > 0.001):
            self.__amount = amount
            self.render()

