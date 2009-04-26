from OSDComponent import OSDComponent
from com import msgs
from ui import pixbuftools
from ui.ImageButton import ImageButton
from ui.HBox import HBox
from theme import theme

import gtk
import gobject
import pango


class OSDControls(OSDComponent):

    def __init__(self):
    
        self.__timeout_handler = None
        self.__index = 0
        
        self.__actions = []
    
        OSDComponent.__init__(self)
        
        x = 0
        for icon, action in [(theme.osd_btn_play_1, msgs.INPUT_EV_PLAY),
                             (theme.osd_btn_previous_1, msgs.INPUT_EV_PREVIOUS),
                             (theme.osd_btn_next_1, msgs.INPUT_EV_NEXT),
                             (theme.osd_btn_dir_up_1, msgs.INPUT_EV_NAV_MENU),
                             (theme.osd_btn_eject_1, msgs.INPUT_EV_EJECT)]:
            btn = ImageButton(icon, icon)
            btn.set_geometry(x, 0, 128, 128)
            self.__actions.append(action)
            self.add(btn)
            x += 160

        w = x - 32
        h = 128
        self.set_size(w, h)
        self.set_pos((gtk.gdk.screen_width() - w) / 2,
                     (gtk.gdk.screen_height() - h) / 2)

        self.set_hilighting_box(pixbuftools.make_frame(
            theme.mb_selection_frame, 128, 128, True))
        self.place_hilighting_box(0, 0)



    def render_this(self):
    
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.clear_translucent()
        screen.fill_area(0, 0, w, h, "#000000a0")
        
        
        
    def __show(self):

        if (not self.__timeout_handler):
            self.set_visible(True)
            self.render()
        else:
            gobject.source_remove(self.__timeout_handler)
        
        self.__timeout_handler = gobject.timeout_add(5000, self.__hide)
        self.emit_message(msgs.INPUT_EV_CONTEXT_MENU)


    def __hide(self):
    
        self.__timeout_handler = None
        self.set_visible(False)

        self.emit_message(msgs.INPUT_EV_CONTEXT_FULLSCREEN)



    def __run_action(self, index):
    
        action = self.__actions[index]
        self.emit_message(action)


    def handle_message(self, msg, *args):
    
        if (msg == msgs.INPUT_EV_MENU):
            self.__show()

        if (not self.is_visible()): return
        
        
        if (msg == msgs.INPUT_EV_LEFT):
            self.__show()
            if (self.__index > 0):
                self.__index -= 1
                self.move_hilighting_box(self.__index * 160, 0)
                
        elif (msg == msgs.INPUT_EV_RIGHT):
            self.__show()
            if (self.__index + 1 < len(self.__actions)):
                self.__index += 1
                self.move_hilighting_box(self.__index * 160, 0)

        elif (msg == msgs.INPUT_EV_UP):
            self.emit_message(msgs.INPUT_EV_VOLUME_UP)

        elif (msg == msgs.INPUT_EV_DOWN):
            self.emit_message(msgs.INPUT_EV_VOLUME_DOWN)

        elif (msg == msgs.INPUT_EV_ENTER):
            self.__run_action(self.__index)
