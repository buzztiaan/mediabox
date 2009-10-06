from com import Component, Viewer, View, Widget, msgs
from utils import logging

from RootPane import RootPane
from TitlePanel import TitlePanel
from ViewerState import ViewerState
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


# interval for hw key autorepeater in ms
_AUTOREPEATER_INTERVAL = 200


class AppWindow(Component, RootPane):
    """
    Main window of the application.
    """

    def __init__(self):

        self.__views = []
        self.__current_view = None
        self.__initial_view = None

        #self.__viewers = []
        self.__current_viewer = None
        self.__current_device_id = ""
        self.__view_mode = viewmodes.NORMAL
        self.__battery_remaining = 100.0
        
        # auto repeat handler for hw keys without auto repeat
        self.__autorepeater = None
        
        self.__is_fullscreen = True
        
        # mapping: viewer -> state
        self.__viewer_states = {}

        # search string for finding items with the keyboard
        self.__keyboard_search_string = ""
        # timer for clearing the search term
        self.__keyboard_search_reset_timer = None

        self.__hildon_input_replace = True
        
        # flag for indicating whether initialization has finished
        self.__is_initialized = False
    
        if (platforms.PLATFORM == platforms.MAEMO4):
            platforms.create_osso_context(values.OSSO_NAME, "1.0", False)
            import hildon
            self.__program = hildon.Program()
            
        elif (platforms.PLATFORM == platforms.MAEMO5):
            platforms.create_osso_context(values.OSSO_NAME, "1.0", False)

        # window
        #self.__window = Window(True)
        #self.__window.set_title("MediaBox")
        #self.__window.set_size(800, 480)
        #self.__window.set_size(480, 800)
        #self.__window.set_visible(True)

        #if (platforms.PLATFORM == platforms.MAEMO4):
        #    self.__program.add_window(self.__window.get_gtk_window())

        #self.__window.connect_key_pressed(self.__on_key)
        #self.__window.connect_key_released(lambda *a:self.__autorepeat_stop())
        #self.__window.connect_closed(self.__on_close_window)

        # screen pixmap
        #screen = Pixmap(self.__window.window)
        
        Component.__init__(self)
        RootPane.__init__(self)
        #self.__window.add(self)
        #w, h = self.__window.get_size()
        
        #self.set_window(self.__window)
        #self.set_size(w, h)
        #self.set_screen(screen)

        # viewer tabs
        self.__tabs = Tabs()
        self.add(self.__tabs)

        # content box
        self.__box = UIWidget()
        self.add(self.__box)
        self.push_actor(self.__box)
       
        # title panel
        #self.__title_panel = TitlePanel()
        #self.__title_panel.set_title("Initializing")
        #self.__title_panel.set_visible(False)
        #self.__title_panel.connect_clicked(self.__on_click_title)
        #self.__box.add(self.__title_panel)
       
        #self.__status_current_viewer = Image(None)

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
                   (self.__scan_at_startup, []),
                   #(self.hide_overlay, []),
                   #(self.__add_panels, []),
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

        #gobject.timeout_add(0, f)



    def __scan_at_startup(self):
        """
        Scans the media at startup if the user wants it so.
        """
    
        if (config.scan_at_startup()):
            self.__scan_media(True)
        else:
            self.__scan_media(False)



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
            #self.add(view)
            view.set_visible(False)
            #view.set_title(`view`)
            #self.__tabs.add_tab(None, view.TITLE, self.__on_show_view, view)
            
            if (cnt == 0):
                view.connect_closed(self.__try_quit)
            else:
                view.connect_closed(self.__close_view)
            
            cnt += 1
         #end for


    def __add_panels(self):
        """
        Adds the panel components.
        """
    
        #self.__box.add(self.__title_panel)
        #self.__title_panel.set_status_icon(self.__status_current_viewer)
        pass


    def render_this(self):
    
        RootPane.render_this(self)
    
        w, h = self.get_size()
        screen = self.get_screen()

        #self.__title_panel.set_geometry(0, 0, w, 40)
        
        #if (self.__tabs.is_visible()):
        if (w < h):
            # portrait mode
            #self.__tabs.set_orientation(Tabs.HORIZONTAL)
            #self.__tabs.set_geometry(0, 0, w, 42)
            if (self.__current_view):
                self.__current_view.set_geometry(0, 0, w, h)
        else:
            # landscape mode
            #self.__tabs.set_orientation(Tabs.VERTICAL)
            #self.__tabs.set_geometry(0, 0, 42, h)
            if (self.__current_view):
                self.__current_view.set_geometry(0, 0, w, h)

        #else:
        #    if (self.__current_view):
        #        self.__current_view.set_geometry(0, 0, w, h)

        
    def __set_view_mode(self, view_mode):
        """
        Sets the view mode.
        """

        if (not self.__is_initialized): return
        if (view_mode == self.__view_mode): return

        w, h = self.get_size()

        if (view_mode == viewmodes.NORMAL):
            pass #self.__title_panel.set_visible(True)
                       
        elif (view_mode == viewmodes.FULLSCREEN):
            #self.__title_panel.set_visible(False)
            #if (self.__current_viewer):
            #    self.__current_viewer.set_geometry(0, 0, w, h)
            pass

        self.__view_mode = view_mode
        #if (self.__current_viewer):
        #    self.__get_vstate().view_mode = view_mode


    def __on_click_title(self):
        """
        Reacts on clicking the title panel.
        """

        self.__show_virtual_keyboard()
        

                 
    def __on_menu_button(self, px, py):
        """
        Reacts on pressing the menu button.
        """
        
        #self.__show_tabs()
        if (px < 80):
            self.emit_message(msgs.INPUT_EV_MENU)



    def __scan_media(self, force_rebuild):
        """
        Scans the media root locations for media files.
        
        @param force_scan: scan even if mediaroots and types haven't changed
        """
        
        mediaroots = config.mediaroot()        
    
        if (not mediaroots):
        #    dialogs.warning("No media library specified!",
        #                    "Please specify the contents of your\n"
        #                    "media library in the folder viewer.")
            return
        #end if


        #self.show_overlay("Scanning Media", "", theme.mb_viewer_audio)

        self.emit_message(msgs.MEDIASCANNER_ACT_SCAN, mediaroots, force_rebuild)
        

        #for v in self.__viewers:
        #    vstate = self.__get_vstate(v)
        #    vstate.selected_item = -1
        #    vstate.item_offset = 0


        #import gc; gc.collect()
        #self.hide_overlay()


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
   
        #keyval = ev.keyval
        #key = gtk.gdk.keyval_name(keyval)

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

        


    def __show_virtual_keyboard(self):
        """
        Displays the virtual keyboard.
        """
       
        pass #self.emit_message(msgs.VKB_ACT_SHOW, self.__window)



    def __reset_search_timeout(self):
        """
        Resets the timeout after which the search gets cleared.
        """

        def f():
            self.__keyboard_search_string = ""
            self.__keyboard_search_reset_timer = None
            self.emit_message(msgs.CORE_EV_SEARCH_CLOSED)

        if (self.__keyboard_search_reset_timer):
            gobject.source_remove(self.__keyboard_search_reset_timer)
        self.__keyboard_search_reset_timer = gobject.timeout_add(2000, f)



    def __get_search_term(self):
        """
        Returns the current search term.
        """
    
        return self.__keyboard_search_string


    def __set_search_term(self, term):
        """
        Sets the search term to the given value.
        """
        
        self.__keyboard_search_string = term

        #if (not term): return
        
        #self.__title_panel.set_title_with_timeout("Search: " + term, 2000)
        self.__reset_search_timeout()
        
        self.emit_message(msgs.CORE_ACT_SEARCH_ITEM, term)
            


    def __get_vstate(self, viewer = None):
    
        if (not viewer):
            viewer = self.__current_viewer
       
        if (not viewer in self.__viewer_states):
            vstate = ViewerState()
            self.__viewer_states[viewer] = vstate
        
        return self.__viewer_states[viewer]
                
            
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

            
    """
    def __select_viewer(self, idx):
        ""
        Selects the current viewer by index number.
        ""        
      
        viewer = self.__viewers[idx]
        
        if (self.__current_viewer):
            self.__current_viewer.hide()
                
        self.__current_view = viewer

        vstate = self.__get_vstate()
        self.__set_view_mode(vstate.view_mode)

        self.set_frozen(True)
        viewer.show()
        
        icon = viewer.ICON.scale_simple(32, 32, gtk.gdk.INTERP_TILES)
        self.__status_current_viewer.set_image(icon)
        self.__title_panel.set_status_icon(self.__status_current_viewer)
        
        self.set_frozen(False)
        self.fx_slide_in()
        
        self.emit_message(msgs.INPUT_ACT_REPORT_CONTEXT)
        self.emit_message(msgs.UI_EV_VIEWER_CHANGED, idx)
    """

    """
    def __stack_window(self):
    
        self.__window.remove(self)
        win = Window(True)
        win.add(self)
        win.set_visible(True)
        self.set_visible(True)
        win.render()
    """
        
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
            
        elif (isinstance(component, Widget)):
            self.add(component)


    def handle_CORE_ACT_APP_MINIMIZE(self):

        pass #self.__window.iconify()
        
        
    def handle_CORE_ACT_APP_CLOSE(self):

        self.__try_quit()


    def handle_CORE_ACT_SCAN_MEDIA(self, force_rebuild):

        self.__scan_media(force_rebuild)



    def handle_CORE_EV_THEME_CHANGED(self):

        from mediabox import thumbnail
        thumbnail.clear_cache()
        #self.set_frozen(True)
        self.propagate_theme_change()
        #self.__prepare_collection_caps()
        #self.__root_pane.render_buffered()            
        self.fx_slide_in()


    def handle_CORE_ACT_SET_TITLE(self, title):

        #self.__title_panel.set_title(title)
        pass #self.__window.set_title(title)


    def handle_CORE_ACT_SET_INFO(self, info):

        pass #self.__title_panel.set_info(info)


    def handle_HWKEY_EV_BACKSPACE(self):

        term = self.__get_search_term()
        if (term):
            term = term[:-1]
            self.__set_search_term(term)

    def handle_HWKEY_EV_KEY(self, key):

        term = self.__get_search_term()
        term += key.lower()
        self.__set_search_term(term)

    """
    def handle_INPUT_EV_PREVIOUS_VIEWER(self):            

        idx = self.__viewers.index(self.__current_viewer)
        if (idx > 0):
            self.__select_viewer(idx - 1)
                
    def handle_INPUT_EV_NEXT_VIEWER(self):

        idx = self.__viewers.index(self.__current_viewer)
        if (idx < len(self.__viewers) - 1):
            self.__select_viewer(idx + 1)
    """


    def handle_MEDIASCANNER_EV_SCANNING_STARTED(self):

        pass #self.show_overlay("Scanning Media", "", theme.mb_viewer_audio)
        
        
    def handle_MEDIASCANNER_EV_SCANNING_PROGRESS(self, name):

        pass #self.show_overlay("Scanning Media", "- %s -" % name,
        #                  theme.mb_viewer_audio)

    
    def handle_MEDIASCANNER_EV_SCANNING_FINISHED(self):

        pass #self.hide_overlay()


    def handle_SYSTEM_EV_BATTERY_REMAINING(self, percent):                

        self.__battery_remaining = percent
        #self.__prepare_collection_caps()


    def handle_UI_EV_DEVICE_SELECTED(self, dev_id):    

        self.__current_device_id = dev_id


    def handle_UI_ACT_FREEZE(self):
    
        self.__box.set_frozen(True)

    
    def handle_UI_ACT_THAW(self):            

        self.__box.set_frozen(False)
        self.render_buffered()

    
    def handle_UI_ACT_RENDER(self):            

        self.render_buffered()


    def handle_UI_ACT_SHOW_MESSAGE(self, text, subtext, icon):

        pass #self.show_overlay(text, subtext, icon)


    def handle_UI_ACT_HIDE_MESSAGE(self):

        pass #self.hide_overlay()


    def handle_UI_ACT_SELECT_VIEW(self, name):

        self.__select_view_by_name(name)


    def handle_UI_ACT_VIEW_MODE(self, mode):

        self.__set_view_mode(mode)


    def handle_UI_ACT_SET_STATUS_ICON(self, w):
    
        pass #self.__title_panel.set_status_icon(w)
        

    def handle_UI_ACT_UNSET_STATUS_ICON(self, w):
    
        pass #self.__title_panel.unset_status_icon(w)


    def handle_ASR_EV_LANDSCAPE(self):
    
        for view in self.__views:
            view.set_portrait_mode(False)
        
        
    def handle_ASR_EV_PORTRAIT(self):

        for view in self.__views:    
            view.set_portrait_mode(True)

