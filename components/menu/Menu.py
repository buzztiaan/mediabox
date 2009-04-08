from com import Widget, Viewer, msgs
from WindowControls import WindowControls
from ui.HilightingWidget import HilightingWidget
from ui.ImageButton import ImageButton
from ui.SequenceButton import SequenceButton
from ui.Label import Label
from ui.Pixmap import Pixmap
from ui.EventBox import EventBox
from ui import pixbuftools
from mediabox import config as mb_config
from mediabox import values
from theme import theme


class Menu(Widget):

    def __init__(self):
    
        # buffer for saving the screen
        self.__backing_buffer = None
        
        # buffer for caching the menu panel
        self.__panel_buffer = None
    
        # list of viewer components
        self.__viewers = []
        
        # list of icon objects
        self.__icons = []

        self.__position_matrix = [[]]
        self.__cursor_position = (0, 0)

        self.__index = 0
        self.__previous_index = 0

        # the index of the component that is currently playing
        self.__currently_playing = -1
        
        self.__is_prepared = False
    
    
        Widget.__init__(self)

        self.__panel = HilightingWidget()
        self.add(self.__panel)
        self.__panel.set_hilighting_box(
              pixbuftools.make_frame(theme.mb_selection_frame, 120, 120, True))

        self.__label = Label("%s ver %s - %s" \
                      % (values.NAME, values.VERSION, values.COPYRIGHT),
                      theme.font_mb_micro, theme.color_mb_menu_text)
        self.__panel.add(self.__label)


        repeat_mode = mb_config.repeat_mode()
        shuffle_mode = mb_config.shuffle_mode()

        btn_repeat = SequenceButton(
             [(theme.mb_repeat_none, mb_config.REPEAT_MODE_NONE),
              (theme.mb_repeat_one, mb_config.REPEAT_MODE_ONE),
              (theme.mb_repeat_all, mb_config.REPEAT_MODE_ALL)])
        btn_repeat.connect_changed(mb_config.set_repeat_mode)
        btn_repeat.set_size(48, 48)
        btn_repeat.set_value(repeat_mode)
        self.add(btn_repeat)
        
        btn_shuffle = SequenceButton(
             [(theme.mb_shuffle_none, mb_config.SHUFFLE_MODE_NONE),
              (theme.mb_shuffle_one, mb_config.SHUFFLE_MODE_ONE)])
        btn_shuffle.connect_changed(mb_config.set_shuffle_mode)
        btn_shuffle.set_size(48, 48)
        btn_shuffle.set_value(shuffle_mode)
        self.add(btn_shuffle)
        
        self.__buttons = [btn_repeat, btn_shuffle]


        self.__touch_back_area = EventBox()
        self.__touch_back_area.connect_button_pressed(
            lambda x,y:self.__hide_menu())
        self.add(self.__touch_back_area)


        # window controls
        self.__window_ctrls = WindowControls()
        self.__window_ctrls.add_observer(self.__on_observe_window_ctrls)
        self.add(self.__window_ctrls)
        

    def __on_observe_window_ctrls(self, src, cmd, *args):
    
        if (cmd == src.OBS_MINIMIZE_WINDOW):
            self.emit_message(msgs.CORE_ACT_APP_MINIMIZE)

        elif (cmd == src.OBS_CLOSE_WINDOW):
            self.emit_message(msgs.CORE_ACT_APP_CLOSE)


    def _reload(self):
    
        self.__is_prepared = False
        self.__panel.set_hilighting_box(
              pixbuftools.make_frame(theme.mb_selection_frame, 120, 120, True))
        

    def render_this(self):

        if (not self.__is_prepared):
            self.__prepare()

        x, y = self.__panel.get_screen_pos()
        w, h = self.__panel.get_size()
        screen = self.__panel.get_screen()
       
        screen.fill_area(x, y, w - 80, h, theme.color_mb_menu)
        screen.fill_area(w - 80, y, 80, h, theme.color_mb_menu_side)
        screen.fill_area(0, y, w, 2, "#000000")
        self.__label.set_geometry(8, h - 16, w - 16, 0)
        
        b_y = y + 10
        for btn in self.__buttons:
            b_w, b_h = btn.get_size()
            btn.set_pos(w - 80 + (80 - b_w) / 2, b_y)
            b_y += 70
        
        if (self.__currently_playing >= 0):
            icon = self.__icons[self.__currently_playing]
            i_x, i_y = icon.get_screen_pos()
            i_w, i_h = icon.get_size()
            screen.draw_frame(theme.mb_active_frame,
                              i_x, i_y, i_w, i_h, True)

        self.__window_ctrls.set_geometry(w - 210, 0, 210, 80)



    def __add_viewer(self, v):
    
        self.__viewers.append(v)


    def __generate_icons(self):
                
        self.__viewers.sort(lambda a,b:cmp(a.PRIORITY, b.PRIORITY))
        
        for v in self.__viewers:
            icon = ImageButton(v.ICON, v.ICON, manual = True)
            icon.set_size(120, 120)
            self.__panel.add(icon)
            icon.connect_button_pressed(self.__on_tab_selected, len(self.__icons))
            self.__icons.append(icon)
        #end for



    def __on_tab_selected(self, px, py, idx):

        self.__index = idx
        if (self.may_render()):
            self.__hilight_item(idx, self.__hide_menu)



    def __prepare(self):
           
        # compute size and position of icons
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
        self.set_geometry(0, 0, pw, ph)
        self.__panel.set_geometry(0, ph - h, w, h)
        self.__touch_back_area.set_geometry(0, 0, w, ph - h)

        # prepare buffers
        self.__backing_buffer = Pixmap(None, w, h)
        self.__panel_buffer = Pixmap(None, pw, ph)

        if (self.__icons):
            csrx, csry = self.__get_cursor_position(self.__index)
            x, y = self.__position_matrix[csry][csrx]
            self.__panel.place_hilighting_box(x, y)

        self.__is_prepared = True
        self.render_at(self.__panel_buffer)



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
        self.__panel.move_hilighting_box(new_x, new_y)
        try:
            cb(*args)
        except:
            pass

        
        
        
    def __show_menu(self):
    
        self.emit_message(msgs.UI_ACT_FREEZE)
        self.set_frozen(False)
        self.set_visible(True)
        self.__fx_raise()
        self.__window_ctrls.fx_slide_in()
        self.__previous_index = self.__index
        self.emit_message(msgs.INPUT_EV_CONTEXT_MENU)
        self.emit_message(msgs.UI_EV_VIEWER_CHANGED, -1)
        
        
        
    def __hide_menu(self):

        x, y = self.__panel.get_screen_pos()
        w, h = self.__panel.get_size()
        screen = self.__panel.get_screen()
        self.__panel_buffer.copy_pixmap(screen, x, y, x, y, w, h)
    
        self.set_visible(False)
        self.__window_ctrls.fx_slide_out()

        if (self.__index == self.__previous_index):
            self.__fx_lower()
            self.emit_message(msgs.UI_EV_VIEWER_CHANGED, self.__index)
        else:
            self.emit_message(msgs.UI_ACT_SELECT_VIEWER,
                              `self.__viewers[self.__index]`)
        self.emit_message(msgs.UI_ACT_THAW)
        self.emit_message(msgs.INPUT_ACT_REPORT_CONTEXT)



    def __navigate(self, dx, dy):
    
        csr_x, csr_y = self.__cursor_position
        idx = self.__get_index_from_cursor(csr_x + dx, csr_y + dy)
        self.__hilight_item(idx, None)
        

    def handle_COM_EV_COMPONENT_LOADED(self, component):

        # catch viewer objects
        if (isinstance(component, Viewer)):
            self.__add_viewer(component)

    
    def handle_CORE_EV_APP_STARTED(self):    

        if (not self.__icons):
            self.__generate_icons()


    def handle_UI_ACT_SELECT_VIEWER(self, viewer_name):

        if (not self.__icons): self.__generate_icons()
        viewers = [ v for v in self.__viewers if repr(v) == viewer_name ]
        if (viewers):
            self.__index = self.__viewers.index(viewers[0])
        else:
            self.__index = 0
        self.__hilight_item(self.__index, None)


    def handle_MEDIA_EV_LOADED(self, viewer, f):    

        self.__currently_playing = self.__viewers.index(viewer)


    def handle_INPUT_EV_MENU(self):    

        if (self.is_visible()):
            self.__hide_menu()
        else:
            self.__show_menu()


    def handle_INPUT_EV_ENTER(self):
    
        if (self.is_visible()):
            csr_x, csr_y = self.__cursor_position
            self.__index = self.__get_index_from_cursor(csr_x, csr_y)
            self.__hilight_item(self.__index, self.__hide_menu)



    def handle_INPUT_EV_LEFT(self):
    
        if (self.is_visible()):
            self.__navigate(-1, 0)


    def handle_INPUT_EV_RIGHT(self):
    
        if (self.is_visible()):
            self.__navigate(1, 0)


    def handle_INPUT_EV_UP(self):
    
        if (self.is_visible()):
            self.__navigate(0, -1)


    def handle_INPUT_EV_DOWN(self):
    
        if (self.is_visible()):
            self.__navigate(0, 1)




    def __fx_raise(self):

        if (not self.__is_prepared):
            self.__prepare()
    
        x, y = self.__panel.get_screen_pos()
        w, h = self.__panel.get_size()
        pw, ph = self.get_parent().get_size()
        screen = self.get_screen()

        buf = self.__panel_buffer #Pixmap(None, pw, ph)
        #self.render_at(buf)
        
        self.__backing_buffer.copy_pixmap(screen, 0, 0, 0, 0, pw, h)


        def fx(params):
            from_y, to_y = params
            dy = (to_y - from_y) / 3
            if (dy > 0):
                screen.move_area(0, dy, pw, ph - from_y - dy, 0, -dy)
                screen.copy_pixmap(buf, 0, y + h - from_y - dy, 0, ph - from_y - dy,
                                   pw, dy)
                params[0] = from_y + dy
                params[1] = to_y
                return True

            else:
                dy = to_y - from_y
                screen.move_area(0, dy, pw, ph - from_y - dy, 0, -dy)
                screen.copy_pixmap(buf, 0, y + h - from_y - dy, 0, ph - from_y - dy,
                                   pw, dy)
                return False
        

        self.animate(50, fx, [0, h])



    def __fx_lower(self):

        x, y = self.__panel.get_screen_pos()
        w, h = self.__panel.get_size()
        pw, ph = self.get_parent().get_size()
        screen = self.get_screen()
        
        def fx(params):
            from_y, to_y = params
            dy = (to_y - from_y) / 3
            if (dy > 0):
                screen.move_area(0, 0, pw, ph - h + from_y, 0, dy)
                screen.copy_pixmap(self.__backing_buffer,
                                   0, h - from_y - dy, 0, 0, pw, dy)
                params[0] = from_y + dy
                params[1] = to_y
                return True

            else:
                dy = to_y - from_y
                screen.move_area(0, 0, pw, ph - h + from_y, 0, dy)
                screen.copy_pixmap(self.__backing_buffer,
                                   0, h - from_y - dy, 0, 0, pw, dy)
                return False
        
        self.animate(50, fx, [0, h])

