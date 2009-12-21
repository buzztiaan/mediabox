from com import Component, Player, Dialog, msgs
from ui.Pixmap import Pixmap
from ui.Window import Window
from utils import logging
from mediabox import config as mb_config
import platforms
from theme import theme

import gobject
import gtk


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
    <item id="select-output" label="Select Output Device"/>
    <item id="fmtx" label="FM Transmitter"/>
    <item id="info" label="Info"/>
  </menu>
"""


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
                           "fmtx": self.__on_menu_fmtx})

        gobject.timeout_add(0, self.__init)
        

    def __on_close_window(self):
    
        self.emit_message(msgs.MEDIA_ACT_STOP)
        self.emit_message(msgs.CORE_EV_APP_SHUTDOWN)
        gtk.main_quit()


    def __on_key_press(self, keycode):
    
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

    
    def __init(self):
        """
        Initializes the application.
        """
       
        self.render()
        self.emit_message(msgs.CORE_EV_APP_STARTED)
        self.__show_dialog("Navigator")



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
            self.__dialogs.append(component)

        elif (isinstance(component, Player)):
            self.__register_player(component)


    def handle_UI_ACT_FULLSCREEN(self, v):
    
        self.set_fullscreen(v)


    def handle_UI_ACT_SHOW_DIALOG(self, name):
    
        self.__show_dialog(name)


    def handle_MEDIA_ACT_LOAD(self, f):
    
        mimetype = f.mimetype
        handlers = self.__mime_handlers.get(mimetype)

        if (not handlers):
            m1, m2 = mimetype.split("/")
            handlers = self.__mime_handlers.get(m1 + "/*")

        if (not handlers):
            return

        if (self.__current_player):
            self.__current_player.set_visible(False)
            
        self.__current_player = handlers[0]
        self.__current_player.set_visible(True)
        self.__current_player.load(f)
        self.set_title(f.name)
        self.render()


    def handle_ASR_EV_LANDSCAPE(self):

        self.set_portrait_mode(False)
        
        
    def handle_ASR_EV_PORTRAIT(self):

        self.set_portrait_mode(True)















"""
from com import Component, Viewer, View, Widget, msgs
from utils import logging

from TitlePanel import TitlePanel
#from ViewerState import ViewerState
from ui.layout import VBox
from ui.Image import Image
from ui.Window import Window
from ui.Button import Button
from ui.Pixmap import Pixmap
from ui.Tabs import Tabs
from ui.Widget import Widget as UIWidget
from mediabox import config
from mediabox import values
import platforms
from mediabox import viewmodes
from theme import theme

import gtk
import gobject
import os
import time
"""

# interval for hw key autorepeater in ms
_AUTOREPEATER_INTERVAL = 200


class XAppWindow(Component):
    """
    Main window of the application.
    """

    def __init__(self):

        self.__views = []
        self.__current_view = None
        self.__initial_view = None
      
        # auto repeat handler for hw keys without auto repeat
        self.__autorepeater = None
                
        # flag for indicating whether initialization has finished
        self.__is_initialized = False
    
        if (platforms.PLATFORM == platforms.MAEMO4):
            platforms.create_osso_context(values.OSSO_NAME, "1.0", False)
            import hildon
            self.__program = hildon.Program()
            
        elif (platforms.PLATFORM == platforms.MAEMO5):
            platforms.create_osso_context(values.OSSO_NAME, "1.0", False)

        
        Component.__init__(self)

        gobject.idle_add(self.__startup)

        
       
    def __startup(self):
        """
        Runs a queue of actions to take for startup.
        """

        actions = [#(self.render, []),
                   #(gtk.main_quit, []),
                   #(self.show_overlay, ["%s %s" % (values.NAME, values.VERSION),
                   #                     "",
                   #                     theme.mb_viewer_audio]),
                   #(self.__window.set_visible, [True]),
                   #(time.sleep, [5]),
                   (self.__register_views, []),
                   (self.__select_initial_view, []),
                   #(self.show_overlay, ["%s %s" % (values.NAME, values.VERSION),
                   #                     "- starting -",
                   #                     theme.mb_viewer_audio]),
                   #(self.hide_overlay, []),
                   (self.emit_message, [msgs.CORE_EV_APP_STARTED]),
                   ]
                   
        def f():
            if (actions):                
                act, args = actions.pop(0)
                logging.info("running startup action %s, %s", `act`, `args`)
                try:
                    act(*args)
                except:
                    import traceback; traceback.print_exc()
                    pass
                return True
            else:
                logging.info("startup complete, took %0.2f seconds" \
                              % (time.time() - values.START_TIME))
                return False
                
        for act, args in actions:
            logging.info("running startup action %s, %s", `act`, `args`)
            try:
                act(*args)
            except:
                logging.error("an error occured:\n%s", logging.stacktrace())
        #end for
        
        logging.info("startup complete, took %0.2f seconds" \
                        % (time.time() - values.START_TIME))



    def __select_initial_view(self):
        """
        Selects the view that is initially shown.
        """
        
        self.__initial_view = self.__views[0]
        self.__select_view_by_name(`self.__initial_view`)


    def __register_views(self):
        """
        Sorts and registers the views.
        """

        self.__views.sort(lambda a,b:cmp(a.PRIORITY, b.PRIORITY))

        cnt = 0
        for view in self.__views:
            logging.info("registering view [%s]", view)
            view.set_visible(False)
            
            if (cnt == 0):
                view.connect_closed(self.__try_quit)
            else:
                view.connect_closed(self.__close_view)
            
            cnt += 1
         #end for


    def __on_show_view(self, view):
    
        if (self.__current_view):
            self.__current_view.set_visible(False)
    
        self.__current_view = view
        self.__current_view.set_visible(True)
        self.render()

                        
    def __on_close_window(self):
    
        self.__try_quit()
        return True


    def __autorepeat_start(self, key_msg):
    
        def f():
            self.emit_message(key_msg)
            return True
            
        if (self.__autorepeater):
            gobject.source_remove(self.__autorepeater)
        self.__autorepeater = gobject.timeout_add(_AUTOREPEATER_INTERVAL, f)
        
        
    def __autorepeat_stop(self):

        if (self.__autorepeater):
            gobject.source_remove(self.__autorepeater)
            self.__autorepeater = None    
    

    def __on_key(self, key):
   
        logging.debug("key pressed: [%s]", key)
        
        if (key == "space"): key = " "
        
        if (key == "Escape"):
            self.emit_message(msgs.HWKEY_EV_ESCAPE)
        
        elif (key == "Return"):
            self.emit_message(msgs.HWKEY_EV_ENTER)

        elif (key == "F1"):
            self.emit_message(msgs.HWKEY_EV_F1)
        elif (key == "F2"):
            self.emit_message(msgs.HWKEY_EV_F2)
        elif (key == "F3"):
            self.emit_message(msgs.HWKEY_EV_F3)
        elif (key == "F4"):
            self.emit_message(msgs.HWKEY_EV_F4)
        elif (key == "F5"):
            self.emit_message(msgs.HWKEY_EV_F5)
        elif (key == "F6"):
            self.emit_message(msgs.HWKEY_EV_F6)
            self.emit_message(msgs.HWKEY_EV_FULLSCREEN)  # deprecated
        elif (key == "F7"):
            self.__autorepeat_start(msgs.HWKEY_EV_F7)
            self.emit_message(msgs.HWKEY_EV_F7)
            self.emit_message(msgs.HWKEY_EV_INCREMENT)  # deprecated
        elif (key == "F8"):
            self.__autorepeat_start(msgs.HWKEY_EV_F8)
            self.emit_message(msgs.HWKEY_EV_F8)
            self.emit_message(msgs.HWKEY_EV_DECREMENT)  # deprecated
        elif (key == "F9"):
            self.emit_message(msgs.HWKEY_EV_F9)
        elif (key == "F10"):
            self.emit_message(msgs.HWKEY_EV_F10)
        elif (key == "F11"):
            self.emit_message(msgs.HWKEY_EV_F11)
        elif (key == "F12"):
            self.emit_message(msgs.HWKEY_EV_F12)
            self.emit_message(msgs.HWKEY_EV_EJECT)  # deprecated
            
        elif (key == "Up"):
            self.__reset_search_timeout()
            self.emit_message(msgs.HWKEY_EV_UP)
        elif (key == "Down"):
            self.__reset_search_timeout()
            self.emit_message(msgs.HWKEY_EV_DOWN)
        elif (key == "Left"):
            self.emit_message(msgs.HWKEY_EV_LEFT)
        elif (key == "Right"):
             self.emit_message(msgs.HWKEY_EV_RIGHT)

            
        elif (key == "XF86Headset"):
            self.emit_message(msgs.HWKEY_EV_HEADSET)
            
        
        elif (key == "BackSpace"):
            self.emit_message(msgs.HWKEY_EV_BACKSPACE)
            term = self.__get_search_term()
            if (term):
                term = term[:-1]
                self.__set_search_term(term)
       
        elif (len(key) == 1 and ord(key) > 31):
            #print "KEY", key
            self.emit_message(msgs.HWKEY_EV_KEY, key)
            term = self.__get_search_term()
            term += key.lower()
            self.__set_search_term(term)
           

           
    def __select_view_by_name(self, name):
        """
        Selects the current view by name.
        """
        
        views = [ v for v in self.__views if repr(v) == name ]
        if (views):
            view = views[0]
            
            if (view == self.__current_view):
                return
            
            if (self.__current_view and self.__current_view != self.__initial_view):
                self.__current_view.set_visible(False)
    
            self.__current_view = view
            self.__current_view.set_visible(True)
            self.__current_view.render()
        #end if


    def __close_view(self):
    
        self.__select_view_by_name(`self.__initial_view`)

        
    def __try_quit(self):
    
        #self.__window.present()
        #result = self.call_service(msgs.DIALOG_SVC_QUESTION,
        #                           "Exit",
        #                           "Do you want to quit?")
        result = 0
        
        if (result == 0):
            #config.set_current_viewer(self.__current_viewer)
            #config.set_current_device(self.__current_device_id)
            self.emit_message(msgs.MEDIA_ACT_STOP)
            self.emit_message(msgs.CORE_EV_APP_SHUTDOWN)
            gtk.main_quit()
        else:
            pass


    def handle_COM_EV_COMPONENT_LOADED(self, component):
    
        if (isinstance(component, View)):
            self.__views.append(component)
            

    def handle_CORE_ACT_APP_CLOSE(self):

        self.__try_quit()


    def handle_CORE_EV_THEME_CHANGED(self):

        from mediabox import thumbnail
        thumbnail.clear_cache()
        self.propagate_theme_change()


    def handle_HWKEY_EV_BACKSPACE(self):

        term = self.__get_search_term()
        if (term):
            term = term[:-1]
            self.__set_search_term(term)

    def handle_HWKEY_EV_KEY(self, key):

        term = self.__get_search_term()
        term += key.lower()
        self.__set_search_term(term)


    def handle_UI_ACT_SELECT_VIEW(self, name):

        self.__select_view_by_name(name)


    def handle_ASR_EV_LANDSCAPE(self):
    
        for view in self.__views:
            gobject.idle_add(view.set_portrait_mode, False)
        
        
    def handle_ASR_EV_PORTRAIT(self):

        for view in self.__views:    
            gobject.idle_add(view.set_portrait_mode, True)

