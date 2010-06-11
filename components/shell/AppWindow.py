from com import Component, Player, Dialog, msgs
from ui.Pixmap import Pixmap
from ui import Window
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


class AppWindow(Component, Window):
    """
    Main window of the application.
    """

    def __init__(self):
    
        # buffer for offscreen renderings
        self.__buffer = Pixmap(None, 800, 480)
    
        # list of available dialog windows
        self.__dialogs = []
        
        # stack of windows
        #self.__window_stack = [self]

        # table: MIME type -> [handlers]
        self.__mime_handlers = {}
    
        self.__is_portrait = False

        # the currently active player component
        self.__current_player = None
        

        Component.__init__(self)
        Window.__init__(self, Window.TYPE_TOPLEVEL)
        self.set_flag(windowflags.CATCH_VOLUME_KEYS, True)
        self.connect_closed(self.__on_close_window)
        self.connect_key_pressed(self.__on_key_press)
        self.connect_clicked(lambda *a:self.__show_dialog("navigator.Navigator"))

        self.set_visible(True)

        self.set_title(values.NAME)

        # setup menu
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

        self.set_menu_item("select-output", "Select Media Renderer", True,
                           self.__on_menu_select_output)
        if (platforms.MAEMO5):
            self.set_menu_item("fmtx", "FM Transmitter", True,
                               self.__on_menu_fmtx)
        self.set_menu_item("downloads", "Downloads", True,
                           self.__on_menu_downloads)
        self.set_menu_item("info", "About", True,
                           self.__on_menu_info)
                           

    def __on_close_window(self):
    
        self.emit_message(msgs.MEDIA_ACT_STOP)
        self.emit_message(msgs.COM_EV_APP_SHUTDOWN)
        gtk.main_quit()


    def __on_raise_dialog(self, dlg):
        
        #if (not dlg in self.__window_stack):
        #    self.__window_stack.append(dlg)
        pass
        
        
    def __on_hide_dialog(self, dlg):
    
        #self.__window_stack.remove(dlg)
        #self.__window_stack[-1].set_visible(True)
        pass


    def __on_key_press(self, keycode):
    
        if (self.__is_portrait and 
              mb_config.portrait_swap_volume() and
              keycode in _PORTRAIT_MODE_KEYSWAP):
            keycode = _PORTRAIT_MODE_KEYSWAP[keycode]

        self.call_service(msgs.INPUT_SVC_SEND_KEY, keycode, True)


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


    def __on_menu_downloads(self):
    
        self.__show_dialog("downloader.DownloadManager")


    def __on_menu_info(self):
    
        dlg = InfoDialog(values.NAME + " " + \
                         values.VERSION + " - " + \
                         values.COPYRIGHT,
                         self)
        dlg.run()


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


    def set_size(self, w, h):
    
        self.__buffer = Pixmap(None, w, h)
        Window.set_size(self, w, h)


    def render_this(self):
    
        Window.render_this(self)
        
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
                    
        if (not self.__current_player):
            screen.fill_area(x, y, w, h, theme.color_mb_background)
            screen.draw_centered_text(values.NAME + " " + values.VERSION,
                                      theme.font_mb_headline,
                                      x, h / 2 - 30, w, 30, theme.color_mb_text)
            screen.draw_centered_text(values.COPYRIGHT,
                                      theme.font_mb_plain,
                                      x, h / 2, w, 30, theme.color_mb_text)

            screen.draw_centered_text("Tap here to access your media",
                                      theme.font_mb_plain,
                                      x, h - 80, w, 20, theme.color_mb_text)
            screen.fit_pixbuf(theme.mb_logo,
                              w - 120, h - 120, 120, 120)


    def __show_dialog(self, name):
        """
        Shows the dialog with the given name.
        """

        print name, self.__dialogs
        dialogs = [ d for d in self.__dialogs if repr(d) == name ]
        if (dialogs):
            dlg = dialogs[0]
            dlg.set_visible(True)
            print "SHOW", dlg
            #if (not platforms.MAEMO5):
            #    self.set_visible(False)
        #end if     


    def handle_COM_EV_APP_STARTED(self):

        #gobject.idle_add(self.__show_dialog, "navigator.Navigator")
        pass


    def handle_COM_EV_COMPONENT_LOADED(self, component):

        if (isinstance(component, Dialog)):
            if (repr(component) in [ repr(d) for d in self.__dialogs ]):
                logging.error("a dialog with ID '%s' exists already.",
                              repr(component))
            else:
                self.__dialogs.append(component)
                component.set_parent_window(self)
                #component.connect_raised(self.__on_raise_dialog, component)
                #component.connect_hid(self.__on_hide_dialog, component)

        elif (isinstance(component, Player)):
            self.__register_player(component)


    def handle_CORE_EV_THEME_CHANGED(self):
    
        self.render()


    def handle_UI_ACT_FULLSCREEN(self, v):
    
        self.set_flag(windowflags.FULLSCREEN, v)


    def handle_UI_ACT_SHOW_INFO(self, msg):
    
        dlg = InfoDialog(msg, self)
        dlg.run()


    def handle_UI_ACT_SHOW_DIALOG(self, name):
    
        self.__show_dialog(name)


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

        print "LOAD", f, mimetype, handlers

        new_player = handlers[0]
        if (new_player != self.__current_player):
            new_player.set_visible(True)
            if (self.__current_player):
                self.__current_player.set_visible(False)
            self.__current_player = new_player
            do_render = True
        else:
            do_render = False
            
        self.set_flag(windowflags.BUSY, True)
        gobject.timeout_add(0, loader, do_render)


    def handle_ASR_EV_LANDSCAPE(self):

        self.__is_portrait = False
        self.set_flag(windowflags.PORTRAIT, False)
        self.render()
        
    def handle_ASR_EV_PORTRAIT(self):

        self.__is_portrait = True
        self.set_flag(windowflags.PORTRAIT, True)
        self.render()
        
