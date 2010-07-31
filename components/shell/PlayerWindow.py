from com import Dialog, Player, msgs
from ui.Pixmap import Pixmap
from ui import windowflags
from ui import TitleBar
from ui.dialog import InfoDialog
from utils import logging
from mediabox import config as mb_config
from mediabox import values
import platforms
from theme import theme

import gobject
import gtk


# it's useful to swap the mapping of the increment and decrement keys in
# portrait mode
_PORTRAIT_MODE_KEYSWAP = {
    "F7": "F8",
    "F8": "F7"
}


class PlayerWindow(Dialog):
    """
    Player window of the application.
    """

    def __init__(self):
    
        # table: MIME type -> [handlers]
        self.__mime_handlers = {}
    
        self.__is_portrait = False

        # the currently active player component
        self.__current_player = None
        

        Dialog.__init__(self)
        self.set_flag(windowflags.CATCH_VOLUME_KEYS, True)
        #self.connect_closed(self.__on_close_window)
        self.connect_key_pressed(self.__on_key_press)

        self.__update_menu()


    def __update_menu(self):

        repeat_selected = [mb_config.REPEAT_MODE_NONE,
                           mb_config.REPEAT_MODE_ALL,
                           mb_config.REPEAT_MODE_ONE] \
                          .index(mb_config.repeat_mode())
        shuffle_selected = [mb_config.SHUFFLE_MODE_NONE,
                            mb_config.SHUFFLE_MODE_ONE] \
                           .index(mb_config.shuffle_mode())

        self.set_menu_choice("repeat", [(theme.mb_repeat_none, "No Repeat"),
                                        (theme.mb_repeat_all, "Repeat All"),
                                        (theme.mb_repeat_one, "Repeat One")],
                             repeat_selected, True,
                             self.__on_menu_repeat)
        self.set_menu_choice("shuffle", [(theme.mb_shuffle_none, "No Shuffle"),
                                        (theme.mb_shuffle_one, "Shuffle")],
                             shuffle_selected, True,
                             self.__on_menu_shuffle)

        self.set_menu_item("select-output", "Media Renderers", True,
                           self.__on_menu_select_output)
        if (platforms.MAEMO5):
            self.set_menu_item("fmtx", "FM Transmitter", True,
                               self.__on_menu_fmtx)
        self.set_menu_item("info", "About", True,
                           self.__on_menu_info)


    def __on_menu_repeat(self, choice):
    
        if (choice == 0):
            mb_config.set_repeat_mode(mb_config.REPEAT_MODE_NONE)
        elif (choice == 1):
            mb_config.set_repeat_mode(mb_config.REPEAT_MODE_ALL)
        elif (choice == 2):
            mb_config.set_repeat_mode(mb_config.REPEAT_MODE_ONE)
        
        
    def __on_menu_shuffle(self, choice):
    
        if (choice == 0):
            mb_config.set_shuffle_mode(mb_config.SHUFFLE_MODE_NONE)
        elif (choice == 1):
            mb_config.set_shuffle_mode(mb_config.SHUFFLE_MODE_ONE)


    def __on_menu_select_output(self):
    
        self.emit_message(msgs.MEDIA_ACT_SELECT_OUTPUT, None)
      
        
    def __on_menu_fmtx(self):
    
        #self.__show_dialog("FMTXDialog")
        import platforms
        platforms.plugin_execute("libcpfmtx.so")


    def __on_menu_info(self):
    
        dlg = InfoDialog(values.NAME + " " + \
                         values.VERSION + " - " + \
                         values.COPYRIGHT,
                         self)
        dlg.run()


    def __on_key_press(self, keycode):
    
        if (self.__is_portrait and 
              mb_config.portrait_swap_volume() and
              keycode in _PORTRAIT_MODE_KEYSWAP):
            keycode = _PORTRAIT_MODE_KEYSWAP[keycode]

        self.call_service(msgs.INPUT_SVC_SEND_KEY, keycode, True)
        

    def __register_player(self, player):
    
        # ask player for MIME types
        for mt in player.get_mime_types():
            l = self.__mime_handlers.get(mt, [])
            l.append(player)
            self.__mime_handlers[mt] = l
        #end for
        
        # add player widget
        player.set_visible(False)
        self.add(player)


    def handle_COM_EV_COMPONENT_LOADED(self, component):

        if (isinstance(component, Player)):
            self.__register_player(component)


    def handle_CORE_EV_THEME_CHANGED(self):
    
        self.render()


    def handle_UI_ACT_FULLSCREEN(self, v):
    
        self.set_flag(windowflags.FULLSCREEN, v)


    def handle_MEDIA_ACT_LOAD(self, f):
    
        def loader(do_render):
            if (do_render): self.render()
            self.__current_player.load(f)
            self.set_title(f.name)
            self.set_flag(windowflags.BUSY, False)
        
    
        mimetype = f.mimetype
        handlers = self.__mime_handlers.get(mimetype)


        if (not handlers):
            m1, m2 = mimetype.split("/")
            handlers = self.__mime_handlers.get(m1 + "/*")

        if (not handlers):
            return

        #print "LOAD", f, mimetype, handlers

        new_player = handlers[0]
        if (new_player != self.__current_player):
            new_player.set_visible(True)
            if (self.__current_player):
                self.__current_player.set_visible(False)
            self.__current_player = new_player
            do_render = True
        else:
            do_render = False
            
        self.set_visible(True)
        self.set_flag(windowflags.BUSY, True)
        gobject.timeout_add(0, loader, do_render)


    """
    def handle_ASR_ACT_ENABLE(self, value):
    
        self.set_flag(windowflags.ASR, value)
    """


    def handle_ASR_EV_LANDSCAPE(self):

        self.__is_portrait = False
        #self.set_flag(windowflags.PORTRAIT, False)
        self.render()
        
        
    def handle_ASR_EV_PORTRAIT(self):

        self.__is_portrait = True
        #self.set_flag(windowflags.PORTRAIT, True)
        self.render()

