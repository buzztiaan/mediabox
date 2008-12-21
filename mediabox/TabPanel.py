from ui.HilightingWidget import HilightingWidget
from ui.HBox import HBox
from ui.ImageButton import ImageButton
from ui.SequenceButton import SequenceButton
from ui.Label import Label
from ui.Pixmap import Pixmap
from ui import pixbuftools
from utils.Observable import Observable
from utils import threads
import config as mb_config
import values
from theme import theme

import threading
import gtk
import gobject


class TabPanel(HilightingWidget, Observable):

    OBS_TAB_SELECTED = 0
    OBS_SHUFFLE_MODE = 1
    OBS_REPEAT_MODE = 2
    

    def __init__(self):
    
        self.__backing_buffer = None
        
        self.__position_matrix = [[]]
        self.__cursor_position = (0, 0)

        self.__index = 0

        # the index of the component that is currently playing
        self.__currently_playing = -1
        
        self.__lock = threading.Event()

        # icon widgets
        self.__icons = []
        self.__viewers = []
        self.__buttons = []
        
        # whether the widget is prepared for rendering
        self.__is_prepared = False

        self.__is_raised = False
        
        
        HilightingWidget.__init__(self)        
        self.set_hilighting_box(
              pixbuftools.make_frame(theme.mb_selection_frame, 120, 120, True))

        self.__label = Label("%s ver %s - %s" \
                      % (values.NAME, values.VERSION, values.COPYRIGHT),
                      theme.font_mb_micro, theme.color_mb_text)
        self.add(self.__label)
        #self.__label.set_alignment(self.__label.RIGHT)

        # playmode buttons
        repeat_mode = mb_config.repeat_mode()
        shuffle_mode = mb_config.shuffle_mode()

        btn_repeat = SequenceButton(
             [(theme.mb_repeat_none, mb_config.REPEAT_MODE_NONE),
              (theme.mb_repeat_one, mb_config.REPEAT_MODE_ONE),
              (theme.mb_repeat_all, mb_config.REPEAT_MODE_ALL)])
        btn_repeat.connect_changed(
              lambda v:self.update_observer(self.OBS_REPEAT_MODE, v))
        #btn_repeat.set_pos(730, 30)
        btn_repeat.set_size(48, 48)
        btn_repeat.set_value(repeat_mode)
        self.add(btn_repeat)
        
        btn_shuffle = SequenceButton(
             [(theme.mb_shuffle_none, mb_config.SHUFFLE_MODE_NONE),
              (theme.mb_shuffle_one, mb_config.SHUFFLE_MODE_ONE)])
        btn_shuffle.connect_changed(
              lambda v:self.update_observer(self.OBS_SHUFFLE_MODE, v))
        #btn_shuffle.set_pos(730, 100)
        btn_shuffle.set_size(48, 48)
        btn_shuffle.set_value(shuffle_mode)
        self.add(btn_shuffle)
        
        self.__buttons = [btn_repeat, btn_shuffle]



    def _reload(self):
    
        HilightingWidget._reload(self)
    
        self.set_hilighting_box(
              pixbuftools.make_frame(theme.mb_selection_frame, 120, 120, True))

        self.__buffer = None
        self.__is_prepared = False


    def set_size(self, w, h):
        
        HilightingWidget.set_size(self, w, h)
        self.__is_prepared = False


    def __on_tab_selected(self, px, py, idx):

        self.select_viewer(idx)
        if (self.may_render()):
            self.__hilight_item(idx, self.update_observer,
                                self.OBS_TAB_SELECTED, idx)
        


    def add_viewer(self, v):
    
        self.__viewers.append(v)
        #x, y = self.__pos
                
        icon = ImageButton(v.ICON, v.ICON, manual = True)
        icon.set_size(120, 120)
        self.add(icon)
        icon.connect_button_pressed(self.__on_tab_selected, len(self.__icons))
        self.__icons.append(icon)


    def __prepare(self):
           
        # compute size and position icons
        pw, ph = self.get_parent().get_size()
        i_x = i_y = i_w = i_h = 20

        self.__position_matrix = []
        row = []
        for icon in self.__icons:
            if (i_x + i_w > pw - 80):
                i_x = 20
                i_y += i_h + 20
                self.__position_matrix.append(row)
                row = []
                
            icon.set_pos(i_x, i_y)
            row.append((i_x, i_y))
            i_w, i_h = icon.get_size()
            i_x += i_w + 20
        #end for
        self.__position_matrix.append(row)
        w = pw
        h = i_y + i_h + 20
        self.set_size(w, h)

        # prepare backing buffer
        self.__backing_buffer = Pixmap(None, w, h)

        if (self.__icons):
            csrx, csry = self.__get_cursor_position(self.__index)
            x, y = self.__position_matrix[csry][csrx]
            self.place_hilighting_box(x, y)

        self.__is_prepared = True


    def render_this(self):

        if (not self.__is_prepared):
            self.__prepare()

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
       
        screen.fill_area(x, y, w - 80, h, theme.color_mb_background)
        screen.fill_area(w - 80, y, 80, h, "#aaaaaf")
        screen.fill_area(0, 0, w, 2, "#333333")
        self.__label.set_geometry(8, h - 16, w - 16, 0)
        
        b_y = 10
        for btn in self.__buttons:
            b_w, b_h = btn.get_size()
            btn.set_pos(w - 80 + (80 - b_w) / 2, b_y)
            b_y += 70
        
        if (self.__currently_playing >= 0):
            icon = self.__icons[self.__currently_playing]
            i_x, i_y = icon.get_screen_pos()
            screen.draw_pixbuf(theme.mb_btn_load, i_x + 120 - 32, i_y)


    def __get_cursor_position(self, index):
        """
        Returns the cursor position of the given item.
        """
    
        row_size = len(self.__position_matrix[0])
        if (row_size == 0):
            x = 0
            y = 0

        else:
            y = index / row_size
            x = index % row_size
        
        return (x, y)
        
        
    def __get_index_from_cursor(self, csr_x, csr_y):
        """
        Returns the index of the item at the given cursor.
        """
        
        try:
            idx = csr_y * len(self.__position_matrix[0]) + csr_x
        except:
            idx = 0
            
        return idx
        
        
    def __hilight_item(self, idx, cb, *args):
        """
        Hilights the item at the given position. Invokes the given callback
        when ready.
        """
    
        if (not self.__is_prepared): return

        csr_x, csr_y = self.__get_cursor_position(idx)
        prev_x, prev_y = self.__cursor_position
        try:
            new_x, new_y = self.__position_matrix[csr_y][csr_x]
        except:
            return
        
        self.__cursor_position = (csr_x, csr_y)
        self.move_hilighting_box(new_x, new_y)
        try:
            cb(*args)
        except:
            pass


    def select_viewer(self, idx):
        """
        Selects the given viewer.
        
        @param idx: index of the viewer
        """

        #if (self.may_render()):
        #    self.__hilight_item(idx,
        #                      self.update_observer, self.OBS_TAB_SELECTED, idx)

        self.__index = idx


    def select_current(self):
    
        csr_x, csr_y = self.__cursor_position
        idx = self.__get_index_from_cursor(csr_x, csr_y)
        self.update_observer(self.OBS_TAB_SELECTED, idx)


    def set_currently_playing(self, idx):
    
        self.__currently_playing = idx

        
        
    def close(self):
      
        self.__is_raised = False


    def up(self):
    
        csr_x, csr_y = self.__cursor_position
        idx = self.__get_index_from_cursor(csr_x, csr_y - 1)
        self.__hilight_item(idx, None)


    def down(self):

        csr_x, csr_y = self.__cursor_position
        idx = self.__get_index_from_cursor(csr_x, csr_y + 1)
        self.__hilight_item(idx, None)


    def left(self):

        csr_x, csr_y = self.__cursor_position
        idx = self.__get_index_from_cursor(csr_x - 1, csr_y)
        self.__hilight_item(idx, None)


    def right(self):
    
        csr_x, csr_y = self.__cursor_position
        idx = self.__get_index_from_cursor(csr_x + 1, csr_y)
        self.__hilight_item(idx, None)


    def fx_raise(self, wait = True):

        #if (self.have_animation_lock() or self.__is_raised): return
        #self.set_animation_lock(True)
        self.__is_raised = True

        if (not self.__is_prepared):
            self.__prepare()
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        pw, ph = self.get_parent().get_size()
        screen = self.get_screen()

        buf = Pixmap(None, pw, h)
        self.render_at(buf)
        
        self.__backing_buffer.copy_pixmap(screen, 0, 0, 0, 0, pw, h)
        #finished = threading.Event()


        def fx(params): #from_y, to_y):
            from_y, to_y = params
            dy = (to_y - from_y) / 5
            if (dy > 0):
                screen.move_area(0, dy, pw, ph - from_y - dy, 0, -dy)
                screen.copy_pixmap(buf, 0, h - from_y - dy, 0, ph - from_y - dy,
                                   pw, dy)
                params[0] = from_y + dy
                params[1] = to_y
                return True
                #gobject.timeout_add(10, fx, from_y + dy, to_y)
            else:
                dy = to_y - from_y
                screen.move_area(0, dy, pw, ph - from_y - dy, 0, -dy)
                screen.copy_pixmap(buf, 0, h - from_y - dy, 0, ph - from_y - dy,
                                   pw, dy)
                #finished.set()
                #self.__lock.clear()
                return False
        

        self.animate(50, fx, [0, h])
        #self.set_frozen(False)
        #self.set_animation_lock(False)
        #self.set_events_blocked(False)
        #gobject.timeout_add(250, self.set_events_blocked, False)


    def fx_lower(self, wait = True):

        #if (self.have_animation_lock() or not self.__is_raised): return
        #self.set_animation_lock(True)
        self.__is_raised = False

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        pw, ph = self.get_parent().get_size()
        screen = self.get_screen()

        #finished = threading.Event()
        
        def fx(params): #from_y, to_y):
            from_y, to_y = params
            dy = (to_y - from_y) / 5
            if (dy > 0):
                screen.move_area(0, 0, pw, ph - h + from_y, 0, dy)
                screen.copy_pixmap(self.__backing_buffer,
                                   0, h - from_y - dy, 0, 0, pw, dy)
                #gobject.timeout_add(10, fx, from_y + dy, to_y)
                params[0] = from_y + dy
                params[1] = to_y
                return True
            else:
                dy = to_y - from_y
                screen.move_area(0, 0, pw, ph - h + from_y, 0, dy)
                screen.copy_pixmap(self.__backing_buffer,
                                   0, h - from_y - dy, 0, 0, pw, dy)
                #finished.set()
                #self.__lock.clear()
                return False
        
        #self.set_events_blocked(True)
        #fx(0, h)
        #if (wait): threads.wait_for(lambda :finished.isSet(), "lowering menu")
        self.animate(50, fx, [0, h])
        #self.set_frozen(False)
        #self.set_animation_lock(False)
        #self.set_events_blocked(False)
        #gobject.timeout_add(250, self.set_events_blocked, False)

