from com import Widget, msgs
from ui.ImageStrip import ImageStrip
from ui.KineticScroller import KineticScroller
from ui.EventBox import EventBox
from ui.Pixmap import Pixmap

from theme import theme

import gtk
import gobject


class SideStrip(Widget):

    def __init__(self):
    
        self.__hide_handler = None
        self.__backing_buffer = Pixmap(None, 180 + 64, 480 - 110)
        
    
        Widget.__init__(self)
        

        # image strip
        self.__strip = ImageStrip(5)
        self.__strip.set_bg_color(theme.color_mb_background)
        self.__strip.set_caps(theme.mb_list_top, theme.mb_list_bottom)
        self.__strip.set_visible(True)
        self.add(self.__strip)
        
        self.__kscr = KineticScroller(self.__strip)
        self.__kscr.set_touch_area(0, 108)
        self.__kscr.add_observer(self.__on_observe_strip)

        #self.set_geometry(0, 40, 180, 480 - 110)

        self.__touch_back_area = EventBox()
        self.__touch_back_area.connect_button_pressed(
            lambda x,y:self.__hide_strip())
        self.add(self.__touch_back_area)





    def render_this(self):
    
        pass
        

    def __on_observe_strip(self, src, cmd, *args):

        w, h = self.get_size()
        handled = False
        if (cmd == src.OBS_SCROLLING):
            self.__delay_hiding()
    
        elif (cmd == src.OBS_CLICKED):
            px, py = args
            if (px > 108):
                idx = self.__strip.get_index_at(py)
                self.__hide_strip()
                self.emit_event(msgs.CORE_ACT_LOAD_ITEM, idx)           
                handled = True
            #elif (0 <= px <= 80 and py >= h - 60):
            #    self.emit_message(msgs.INPUT_EV_MENU)
            #    handled = True

        return handled   



    def __delay_hiding(self):
    
        if (self.__hide_handler):
            gobject.source_remove(self.__hide_handler)
        self.__hide_handler = gobject.timeout_add(3000, self.__hide_strip)
        


    def __show_strip(self):
    
        self.emit_message(msgs.UI_ACT_FREEZE)
        self.set_frozen(False)
        #self.__strip.set_frozen(False)
        self.set_visible(True)
        self.__fx_slide_in()
        #self.render()

        self.emit_message(msgs.INPUT_EV_CONTEXT_MENU)
        self.__delay_hiding()


    def __hide_strip(self):

        if (self.__hide_handler):
            gobject.source_remove(self.__hide_handler)
        self.__hide_handler = None
        
        self.__fx_slide_out()
        self.set_visible(False)
        self.emit_message(msgs.UI_ACT_THAW)
        self.emit_message(msgs.INPUT_ACT_REPORT_CONTEXT)

        


    def __set_items(self, items):
        """
        Loads the given items into the side strip.
        """

        self.__strip.hilight(-1)
        self.__strip.set_images(items)
        self.__strip.render()


    def handle_message(self, msg, *args):
    
        if (msg == msgs.UI_ACT_SHOW_STRIP):
            self.__show_strip()

        elif (msg == msgs.UI_ACT_SET_STRIP):
            viewer, items = args
            self.__set_items(items)
                
        elif (msg == msgs.UI_ACT_CHANGE_STRIP):
            owner = args[0]
            self.__strip.change_image_set(owner)
            
        elif (msg == msgs.UI_ACT_HILIGHT_STRIP_ITEM):
            viewer, idx = args
            self.__strip.hilight(idx)

        """               
        elif (event == msgs.UI_ACT_SELECT_STRIP_ITEM):
            viewer, idx = args
            vstate = self.__get_vstate(viewer)
            vstate.selected_item = idx
            if (viewer == self.__current_viewer):
                self.__select_item(idx)

        elif (event == msgs.UI_ACT_SHOW_STRIP_ITEM):
            viewer, idx = args
            if (viewer == self.__current_viewer):
                self.__strip.scroll_to_item(idx)
        """
        
        
    def __fx_slide_in(self):

        pw, ph = self.get_parent().get_size()
        
        self.set_geometry(0, 0, pw, ph)
        self.__strip.set_geometry(0, 40, 180, ph - 110)
        self.__touch_back_area.set_geometry(180, 40, pw - 180, ph - 110)
    
        x, y = self.__strip.get_screen_pos()
        w, h = self.__strip.get_size()
        screen = self.get_screen()

        buf = Pixmap(None, w, h)
        self.__strip.render_at(buf)
        self.__backing_buffer.copy_pixmap(screen, x + 64, y, 0, 0, w, h)
        

        def fx(params):
            from_x, to_x = params
            dx = (to_x- from_x) / 3
            if (dx > 0):
                screen.move_area(x, y, 64 + from_x, h, dx, 0)
                screen.copy_pixmap(buf, to_x - from_x - dx, 0, x, y, dx, h)
                params[0] = from_x + dx
                params[1] = to_x
                return True

            else:
                dx = to_x - from_x
                screen.move_area(x, y, 64 + from_x, h, dx, 0)
                screen.copy_pixmap(buf, to_x - from_x - dx, 0, x, y, dx, h)
                return False
        

        self.animate(50, fx, [0, w])



    def __fx_slide_out(self):

        x, y = self.__strip.get_screen_pos()
        w, h = self.__strip.get_size()
        screen = self.get_screen()

        buf = Pixmap(None, w, h)
        self.render_at(buf)
        

        def fx(params):
            from_x, to_x = params
            dx = (to_x- from_x) / 3
            if (dx > 0):
                screen.move_area(x + dx, y, to_x - from_x + 64 - dx, h, -dx, 0)
                screen.copy_pixmap(self.__backing_buffer,
                                   to_x - from_x - dx, 0,
                                   x + 64 + to_x - from_x - dx, y,
                                   dx, h)
                params[0] = from_x + dx
                params[1] = to_x
                return True

            else:
                dx = to_x - from_x
                screen.move_area(x + dx, y, to_x - from_x + 64 - dx, h, -dx, 0)
                screen.copy_pixmap(self.__backing_buffer,
                                   to_x - from_x - dx, 0,
                                   x + 64 + to_x - from_x - dx, y,
                                   dx, h)
                return False
        

        self.animate(50, fx, [0, w])

