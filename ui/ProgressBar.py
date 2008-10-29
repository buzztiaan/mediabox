from Widget import Widget
from Pixmap import Pixmap, TEMPORARY_PIXMAP, text_extents
import theme

import gtk


class ProgressBar(Widget):
    """
    Class for a progress bar with bookmark functions.
    """
    
    EVENT_CHANGED = "event-changed"
    EVENT_BOOKMARK_CHANGED = "event-bookmark-changed"
    
    
    def __init__(self):
        
        # background pixmap
        self.__bg_pmap = None
        
        # progress pixmap
        self.__progress_pmap = None

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
        
        # the current message if any
        self.__current_message = ""
       
        Widget.__init__(self)
        self.set_size(200, 64)

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
        self.__prepare()


    def __prepare(self):
    
        x, y = self.get_screen_pos()        
        screen = self.get_screen()
        if (not screen):
            return
    
        w, h = self.get_size()
        pbuf1 = theme.mb_progress.subpixbuf(0, 0, 5, 64)
        pbuf2 = theme.mb_progress.subpixbuf(5, 0, 5, 64)
    
        self.__bg_pmap = Pixmap(None, w, h)
        self.__bg_pmap.copy_pixmap(screen, x, y, 0, 0, w, h)
        #self.__bg_pmap.fill_area(0, 0, w, h, "#ff0000")
        self.__progress_pmap = Pixmap(None, w, h)
        self.__progress_pmap.copy_pixmap(screen, x, y, 0, 0, w, h)
        #self.__progress_pmap.fill_area(0, 0, w, h, "#ff0000")
        
        self.__bg_pmap.draw_pixbuf(pbuf1, 0, 0, w, h, True)
        self.__progress_pmap.draw_pixbuf(pbuf2, 0, 0, w, h, True)


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
    
        if (not self.__bg_pmap):
            self.__prepare()
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        pmap = TEMPORARY_PIXMAP
        pmap.copy_pixmap(self.__bg_pmap, 0, 0, 0, 0, w, h)
        self.__render_progress(pmap)
        self.__render_bookmarks(pmap)
        self.__render_message(pmap)
        screen.copy_pixmap(pmap, 0, 0, x, y, w, h)
        
        
    def __render_progress(self, pmap):
    
        w, h = self.get_size()
        
        progress_width = w * self.__progress
        if (self.__progress_pmap):
            pmap.copy_pixmap(self.__progress_pmap, 0, 0, 0, 0,
                             progress_width, 64)
        #end if


    def __render_bookmarks(self, pmap):
    
        w, h = self.get_size()
        for bm in self.__bookmarks:
            bm_pos = w * bm
            #pmap.fill_area(bm_pos - 1, 0, 2, 32, "#ff0000")
            pmap.draw_pixbuf(theme.mb_progress_bookmark,
                        bm_pos - theme.mb_progress_bookmark.get_width() / 2,
                        (h - theme.mb_progress_bookmark.get_height()) / 2)
        #end for
        
        
    def __render_message(self, pmap):
    
        if (self.__current_message):
            w, h = self.get_size()
            t_w, t_h = text_extents(self.__current_message, theme.font_plain)
            pmap.draw_text(self.__current_message, theme.font_plain,
                           (w - t_w) / 2, (h - t_h) / 2, "#ffffff")
        

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

        if (self.__is_dragging and self.__dragged_bookmark == -1): return
        if (not self.may_render()): return
        if (total == 0): return

        self.__progress = pos / float(total)
        self.render()
        #self.send_event(self.EVENT_CHANGED, self.__progress * 100)

