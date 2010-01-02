from com import Component, Player, Dialog, msgs
from ui.Pixmap import Pixmap
from ui.Window import Window
from ui.dialog import InfoDialog
from utils import logging
from mediabox import config as mb_config
from mediabox import values
import platforms
from theme import theme

import gobject
import gtk
try:
    import hildon
except:
    hildon = None


_APP_MENU = """
  <menu>
    <choice id="repeat" selected="%d">
      <option label="" icon="mb_repeat_none"/>
      <option label="" icon="mb_repeat_all"/>
      <option label="" icon="mb_repeat_one"/>
    </choice>
    <choice id="shuffle" selected="%d">
      <option label="" icon="mb_shuffle_none"/>
      <option label="" icon="mb_shuffle_one"/>
    </choice>
    <item id="select-output" label="Select Media Renderer"/>
    <item id="fmtx" label="FM Transmitter"/>
    <item id="info" label="About"/>
  </menu>
"""

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

        # table: MIME type -> [handlers]
        self.__mime_handlers = {}
    
        self.__is_portrait = False
        
        self.__current_player = None
        

        Component.__init__(self)
        Window.__init__(self, Window.TYPE_TOPLEVEL)
        self.connect_closed(self.__on_close_window)
        self.connect_key_pressed(self.__on_key_press)
        self.connect_clicked(lambda *a:self.__show_dialog("Navigator"))
      
        self.set_visible(True)

        # setup menu
        repeat_selected = [mb_config.REPEAT_MODE_NONE,
                           mb_config.REPEAT_MODE_ALL,
                           mb_config.REPEAT_MODE_ONE] \
                          .index(mb_config.repeat_mode())
        shuffle_selected = [mb_config.SHUFFLE_MODE_NONE,
                            mb_config.SHUFFLE_MODE_ONE] \
                           .index(mb_config.shuffle_mode())

        self.set_menu_xml(_APP_MENU % (repeat_selected, shuffle_selected),
                          {"repeat": self.__on_menu_repeat,
                           "shuffle": self.__on_menu_shuffle,
                           "select-output": self.__on_menu_select_output,
                           "fmtx": self.__on_menu_fmtx,
                           "info": self.__on_menu_info})

        gobject.timeout_add(0, self.__init)
        

    def __on_close_window(self):
    
        self.emit_message(msgs.MEDIA_ACT_STOP)
        self.emit_message(msgs.CORE_EV_APP_SHUTDOWN)
        gtk.main_quit()


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


    def __on_menu_info(self):
    
        dlg = InfoDialog(values.NAME + " " + \
                         values.VERSION + " - " + \
                         values.COPYRIGHT,
                         self)
        dlg.run()

    
    def __init(self):
        """
        Initializes the application.
        """
       
        self.render()
        self.emit_message(msgs.CORE_EV_APP_STARTED)
        gobject.idle_add(self.__show_dialog, "Navigator")



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
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        if (self.__current_player):
            self.__current_player.set_geometry(0, 0, w, h)
            
        else:
            screen.fill_area(x, y, w, h, theme.color_mb_background)
            screen.draw_centered_text(values.NAME + " " + values.VERSION,
                                      theme.font_mb_headline,
                                      0, h / 2 - 30, w, 30, theme.color_mb_text)
            screen.draw_centered_text(values.COPYRIGHT,
                                      theme.font_mb_plain,
                                      0, h / 2, w, 30, theme.color_mb_text)

            #screen.draw_pixbuf(theme.mb_btn_navigator_1, 0, h - 64)
            screen.draw_centered_text("Tap here to access your media",
                                      theme.font_mb_plain,
                                      0, h - 80, w, 20, theme.color_mb_text)
            screen.fit_pixbuf(theme.mb_logo,
                              w - 120, h - 120, 120, 120)


    def __show_dialog(self, name):
        """
        Shows the dialog with the given name.
        """

        dialogs = [ d for d in self.__dialogs if repr(d) == name ]
        if (dialogs):
            dlg = dialogs[0]
            dlg.set_visible(True)
        #end if     
        

    def handle_COM_EV_COMPONENT_LOADED(self, component):

        if (isinstance(component, Dialog)):
            if (repr(component) in [ repr(d) for d in self.__dialogs ]):
                logging.error("a dialog with ID '%s' exists already.",
                              repr(component))
            else:
                self.__dialogs.append(component)
                component.get_gtk_window().set_transient_for(self.get_gtk_window())

        elif (isinstance(component, Player)):
            self.__register_player(component)


    def handle_CORE_EV_THEME_CHANGED(self):
    
        self.render()


    def handle_UI_ACT_FULLSCREEN(self, v):
    
        self.set_fullscreen(v)


    def handle_UI_ACT_SHOW_INFO(self, msg):
    
        dlg = InfoDialog(msg, self)
        dlg.run()


    def handle_UI_ACT_SHOW_DIALOG(self, name):
    
        self.__show_dialog(name)


    def handle_MEDIA_ACT_LOAD(self, f):
    
        def loader():
            self.__current_player.load(f)
            self.set_title(f.name)
            self.render()
            self.set_busy(False)
        
    
        mimetype = f.mimetype
        handlers = self.__mime_handlers.get(mimetype)

        print "LOAD", f, mimetype, handlers

        if (not handlers):
            m1, m2 = mimetype.split("/")
            handlers = self.__mime_handlers.get(m1 + "/*")

        if (not handlers):
            return

        if (self.__current_player):
            self.__current_player.set_visible(False)
            
        self.__current_player = handlers[0]
        self.__current_player.set_visible(True)
        self.set_busy(True)
        gobject.timeout_add(0, loader)


    def handle_ASR_EV_LANDSCAPE(self):

        self.__is_portrait = False
        self.set_portrait_mode(False)
        
        
    def handle_ASR_EV_PORTRAIT(self):

        self.__is_portrait = True
        self.set_portrait_mode(True)


    def handle_INPUT_EV_MENU(self):
    
        self.emit_message(msgs.MEDIA_ACT_SELECT_OUTPUT, None)

