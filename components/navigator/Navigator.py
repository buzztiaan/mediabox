from com import Component, Dialog, msgs
from NowPlaying import NowPlaying
from RootDevice import RootDevice
from mediabox.StorageBrowser import StorageBrowser
from ui.Button import Button
from ui.ImageButton import ImageButton
from ui.Slider import Slider
from ui.Toolbar import Toolbar
from ui.dialog import InputDialog
from ui.dialog import InfoDialog
from ui.layout import Arrangement
from ui import Window
from ui import windowflags
from utils import mimetypes
from utils import logging
from storage import File
from mediabox import config as mb_config
from mediabox import values
from utils.ItemScheduler import ItemScheduler
from utils import mimetypes
import platforms
from theme import theme

import gobject
import gtk
import random
import time
import os


_LANDSCAPE_ARRANGEMENT = """
  <arrangement>
    <widget name="toolbar"
            x1="-80" y1="0" x2="100%" y2="100%"/>

    <if-visible name="now-playing">
      <widget name="now-playing"
              x1="0" y1="0" x2="-80" y2="80"/>

      <widget name="slider"
              x1="0" y1="80" x2="40" y2="100%"/>

      <widget name="browser"
              x1="40" y1="80" x2="-80" y2="100%"/>
    </if-visible>

    <if-invisible name="now-playing">
      <widget name="slider"
              x1="0" y1="0" x2="40" y2="100%"/>

      <widget name="browser"
              x1="40" y1="0" x2="-80" y2="100%"/>
    </if-invisible>
  </arrangement>
"""


_PORTRAIT_ARRANGEMENT = """
  <arrangement>
    <widget name="toolbar"
            x1="0" y1="-80" x2="100%" y2="100%"/>

    <if-visible name="now-playing">
      <widget name="now-playing"
              x1="0" y1="0" x2="100%" y2="80"/>

      <widget name="slider"
              x1="0" y1="80" x2="40" y2="-80"/>

      <widget name="browser"
              x1="40" y1="80" x2="100%" y2="-80"/>
    </if-visible>

    <if-invisible name="now-playing">
      <widget name="slider"
              x1="0" y1="0" x2="40" y2="-80"/>

      <widget name="browser"
              x1="40" y1="0" x2="100%" y2="-80"/>
    </if-invisible>
  </arrangement>
"""

_PERSISTED_PATH = os.path.join(values.USER_DIR, "navigator-path")

_MODE_NORMAL = 0
_MODE_SELECT = 1


class Navigator(Component, Window):
    """
    Navigator dialog for browsing media.
    """

    def __init__(self):
    
        # the current mode
        self.__mode = _MODE_NORMAL
        
        # list of available dialog windows
        self.__dialogs = []
        
        # the file that is currently playing    
        self.__current_file = None

        # list of files for playing
        self.__play_folder = None
        self.__play_files = []

        # list for choosing random files from when in shuffle mode
        self.__random_files = []
        
        self.__is_searching = False
        self.__search_term = ""
        
        self.__key_hold_down_timestamp = 0
        self.__skip_letter = False
        
        self.__is_portrait = False

        # scheduler for creating thumbnails one by one
        self.__tn_scheduler = ItemScheduler()
        
    
        Component.__init__(self)
        Window.__init__(self, Window.TYPE_TOPLEVEL)
        self.connect_key_pressed(self.__on_key_press)
        self.connect_closed(self.__on_close_window)

        # [Now Playing] button
        self.__now_playing = NowPlaying()
        self.__now_playing.set_visible(False)
        self.__now_playing.connect_clicked(
               lambda :self.__show_dialog("player.PlayerWindow"))

        # browser list slider
        self.__browser_slider = Slider(theme.mb_list_slider)
        self.__browser_slider.set_mode(Slider.VERTICAL)
        #self.add(self.__browser_slider)

        
        # file browser
        self.__browser = StorageBrowser()
        #self.__browser.set_root_device(self.__root_dev)
        self.__browser.associate_with_slider(self.__browser_slider)
        self.__browser.connect_folder_begin(self.__on_begin_folder)
        self.__browser.connect_folder_progress(self.__on_progress_folder)
        self.__browser.connect_folder_complete(self.__on_complete_folder)
        self.__browser.connect_file_opened(self.__on_open_file)
        self.__browser_slider.connect_button_pressed(
                                    lambda a,b:self.__browser.stop_scrolling())

        # toolbar
        self.__toolbar = Toolbar()

        self.__btn_home = ImageButton(theme.mb_btn_home_1,
                                      theme.mb_btn_home_2)
        self.__btn_home.connect_clicked(self.__on_btn_home)
        
        self.__btn_history = ImageButton(theme.mb_btn_history_1,
                                         theme.mb_btn_history_2)
        self.__btn_history.connect_clicked(self.__on_btn_history)

        self.__btn_bookmarks = ImageButton(theme.mb_btn_bookmark_1,
                                           theme.mb_btn_bookmark_2)
        self.__btn_bookmarks.connect_clicked(self.__on_btn_bookmarks)

        self.__btn_back = ImageButton(theme.mb_btn_dir_up_1,
                                      theme.mb_btn_dir_up_2)
        self.__btn_back.connect_clicked(self.__on_btn_back)

        self.__btn_select_all = ImageButton(theme.mb_btn_select_all_1,
                                            theme.mb_btn_select_all_2)
        self.__btn_select_all.connect_clicked(self.__on_btn_select_all)

        self.__btn_select_none = ImageButton(theme.mb_btn_select_none_1,
                                             theme.mb_btn_select_none_2)
        self.__btn_select_none.connect_clicked(self.__on_btn_select_none)

        self.__btn_select_done = ImageButton(theme.mb_btn_select_done_1,
                                             theme.mb_btn_select_done_2)
        self.__btn_select_done.connect_clicked(self.__on_btn_select_done)


        # arrangement
        self.__arr = Arrangement()
        self.__arr.connect_resized(self.__update_layout)
        self.__arr.add(self.__now_playing, "now-playing")
        self.__arr.add(self.__browser_slider, "slider")
        self.__arr.add(self.__browser, "browser")
        self.__arr.add(self.__toolbar, "toolbar")
        self.add(self.__arr)
        self.__arr.set_visible(False)

        # we have to fill the menu with content before showing the window on
        # Maemo5 or the window will show no menu at all
        self.__update_menu()
        
        self.set_visible(True)


    def __update_menu(self):

        folder = self.__browser.get_current_folder()
        
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
        
        if (folder and folder.folder_flags & folder.ITEMS_ADDABLE):          
            self.set_menu_item("add", "Add New", True,
                               self.__on_menu_add)
        else:
            self.set_menu_item("add", "Add New", False,
                               self.__on_menu_add)
        
        self.set_menu_item("openurl", "Open URL...", True,
                           self.__on_menu_open_url)
        
        self.set_menu_item("downloads", "Active Downloads", True,
                           self.__on_menu_downloads)

        self.set_menu_item("select", "Select Items for Action", True,
                           self.__on_menu_select)
        
        #self.set_menu_item("rearrange", "Rearrange Items", True,
        #                   self.__on_menu_rearrange)
        #self.set_menu_item("info", "About", True,
        #                   self.__on_menu_info)


    def __update_layout(self):
    
        w, h = self.get_size()
        if (w < h):
            # portrait mode
            self.__arr.set_xml(_PORTRAIT_ARRANGEMENT)
        else:
            # landscape mode
            self.__arr.set_xml(_LANDSCAPE_ARRANGEMENT)


    def __update_toolbar(self):
        """
        Updates the contents of the toolbar.
        """

        cwd = self.__browser.get_current_folder()
        if (self.__mode == _MODE_NORMAL):
            items = [self.__btn_home,
                     self.__btn_history,
                     self.__btn_back]
        else:
            items = [self.__btn_select_all,
                     self.__btn_select_none,
                     self.__btn_select_done]
        
        self.__toolbar.set_toolbar(*items)


    def __update_items_per_row(self, folder):

        w, h = self.get_size()
        
        if (folder and folder.folder_flags & folder.ITEMS_COMPACT):
            if (self.__is_portrait):
                self.__browser.set_items_per_row(2)
            else:
                self.__browser.set_items_per_row(4)
        else:
            self.__browser.set_items_per_row(1)
            
        self.__browser.invalidate()
        #self.__browser.render()
   

    def _visibility_changed(self):
        
        Window._visibility_changed(self)
        if (self.is_visible()):
            self.__tn_scheduler.resume()
            
        else:
            self.__tn_scheduler.halt()


    def __on_key_press(self, keycode):

        self.call_service(msgs.INPUT_SVC_SEND_KEY, keycode, True)


    def __on_close_window(self):
    
        self.emit_message(msgs.MEDIA_ACT_STOP)
        self.emit_message(msgs.COM_EV_APP_SHUTDOWN)
        gtk.main_quit()


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


    def __on_menu_rearrange(self):
    
        def on_done():
            for item in self.__browser.get_items():
                item.set_draggable(False)
            self.__browser.invalidate()
                
            self.__update_toolbar()
    
        for item in self.__browser.get_items():
            item.set_draggable(True)
        self.__browser.invalidate()
    
        btn_done = ImageButton(theme.mb_btn_history_1,
                               theme.mb_btn_history_2)
        btn_done.connect_clicked(on_done)
        self.__toolbar.set_toolbar(btn_done)


    def __on_menu_open_url(self):
    
        dlg = InputDialog("URL to open")
        dlg.add_input("URL", "http://")
        
        if (dlg.run() == dlg.RETURN_OK):
            url = dlg.get_values()[0]
            self.__load_url(url)
        #end if
        

    def __on_menu_downloads(self):
    
        self.emit_message(msgs.UI_ACT_SHOW_DIALOG, "downloader.DownloadManager")
        
        
    def __on_menu_fmtx(self):
    
        import platforms
        platforms.plugin_execute("libcpfmtx.so")


    def __on_menu_select(self):
        
        if (self.__browser.begin_bulk_action()):
            self.__mode = _MODE_SELECT
            self.__update_toolbar()
        #end if


    def __on_menu_add(self):
        
        folder = self.__browser.get_current_folder()
        if (folder):
            folder.new_file()
 
 
    def __on_menu_info(self):
    
        self.__show_dialog("core.AboutDialog")
 
       
    def __on_open_file(self, f):
            
        self.__load_file(f, True)


    def __on_begin_folder(self, f):
    
        self.__tn_scheduler.new_schedule(5, self.__on_load_thumbnail)
        self.__tn_scheduler.halt()
        
        #self.set_title(f.name)
        self.set_flag(windowflags.BUSY, True)
        
        self.__update_layout()
        self.__update_menu()
        self.render()
        
        self.__update_items_per_row(f)

        # set platform-specific click behavior
        if (platforms.MAEMO4):
            self.__browser.set_click_behavior(
              self.__browser.CLICK_BEHAVIOR_DOUBLE)
        else:
            self.__browser.set_click_behavior(
              self.__browser.CLICK_BEHAVIOR_SINGLE)
        

    def __on_progress_folder(self, f, c):

        if (c.icon): return

        item = self.__browser.get_items()[-1]
        thumbpath, is_final = \
          self.call_service(msgs.THUMBNAIL_SVC_LOOKUP_THUMBNAIL, c)

        item.set_icon(thumbpath)
        
        if (not is_final):
            #print "SCHEDULING THUMBNAIL", c
            self.__tn_scheduler.add(item, c)


    def __on_complete_folder(self, f):

        self.set_flag(windowflags.BUSY, False)
        
        names = [ p.name for p in self.__browser.get_path() ]
        #title = u" \u00bb ".join(names)
        title = names[-1]
        names.reverse()
        acoustic_title = "Entering " + " in ".join(names)
        self.set_title(title)
        self.emit_message(msgs.UI_ACT_TALK, acoustic_title)
        self.emit_message(msgs.CORE_EV_FOLDER_VISITED, f)
        self.__update_toolbar()

        if (self.is_visible()):
            self.__tn_scheduler.resume()


    def __update_thumbnail(self, item, thumbpath):
    
        #pass
        item.set_icon(thumbpath)
        idx = self.__browser.get_items().index(item)
        self.__browser.invalidate_item(idx)


    def __on_load_thumbnail(self, item, f):

        def on_loaded(thumbpath):
            #print "LOADED THUMBNAIL", thumbpath
            if (thumbpath):
                self.__update_thumbnail(item, thumbpath)
            
            #if (self.is_visible()):
            self.__tn_scheduler.resume()
            #print "RESUMING SCHEDULER"
    
        # load thumbnail
        self.__tn_scheduler.halt()
        #print "HALTING SCHEDULER"
        self.call_service(msgs.THUMBNAIL_SVC_LOAD_THUMBNAIL, f, on_loaded)
        

    def __on_btn_home(self):
        """
        Reacts on pressing the [Home] button.
        """

        self.emit_message(msgs.SSDP_ACT_SEARCH_DEVICES)
        self.__browser.go_root()
        
        
    def __on_btn_history(self):
        """
        Reacts on pressing the [History] button.
        """
        
        f = self.call_service(msgs.CORE_SVC_GET_FILE, "history:///")
        if (f):
            self.__browser.load_folder(f, self.__browser.GO_CHILD, True)


    def __on_btn_bookmarks(self):
        """
        Reacts on pressing the [Bookmarks] button.
        """
        
        f = self.call_service(msgs.CORE_SVC_GET_FILE, "bookmarks://generic/")
        if (f):
            self.__browser.load_folder(f, self.__browser.GO_PARENT, True)


    def __on_btn_back(self):
        """
        Reacts on pressing the [Back] button.
        """

        self.__browser.go_parent()
        #self.__update_items_per_row(self.__browser.get_current_folder())


    def __on_btn_select_all(self):  
        """
        Reacts on pressing the [Select All] button.
        """
        
        self.__browser.select_all()
        
        
    def __on_btn_select_none(self):
        """
        Reacts on pressing the [Select None] button.
        """
        
        self.__browser.unselect_all()
        
        
    def __on_btn_select_done(self):
        """
        Reacts on pressing the [Select Done] button.
        """

        self.__mode = _MODE_NORMAL
        self.__update_toolbar()
        self.__browser.perform_bulk_action()


    def __load_uri(self, uri, mimetype):
    
        if (not mimetype):
            ext = os.path.splitext(uri)[1]
            mimetype = mimetypes.ext_to_mimetype(ext)
    
        f = self.call_service(msgs.CORE_SVC_GET_FILE,
                              "adhoc://" + File.pack_path("/", uri, mimetype))
        print "Loading URI:", f
        if (f):
            self.__load_file(f, True)



    def __load_file(self, f, is_manual):
        """
        Loads the given file.
        """

        #if (f.mimetype == "application/x-applet"):
        #    applet_id = f.resource
        #    self.call_service(msgs.CORE_SVC_LAUNCH_APPLET, applet_id)

        if (f.mimetype == f.CONFIGURATOR):
            cfg_name = f.resource
            self.emit_message(msgs.UI_ACT_SHOW_DIALOG, cfg_name)

        else:
            if (is_manual):
                self.__show_dialog("player.PlayerWindow")
                
            #if (not f.mimetype in mimetypes.get_image_types()):
            self.emit_message(msgs.MEDIA_ACT_STOP)
            self.emit_message(msgs.MEDIA_ACT_LOAD, f)

            # update set of play files
            self.__current_file = f
            self.__browser.hilight_file(f)
            self.__browser.render()

            folder = self.__browser.get_current_folder()
            if (is_manual and folder != self.__play_folder):
                self.__play_folder = folder
                self.__play_files = [ fl for fl in self.__browser.get_files()
                                      if not fl.mimetype.endswith("-folder") ]
                self.__filter_play_files()
                self.__random_files = []

            if (not self.__now_playing.is_visible()):
                self.__now_playing.set_visible(True)
                self.__update_layout()
                self.render()



    def __go_previous(self):

        try:
            idx = self.__play_files.index(self.__current_file)
        except ValueError:
            return False
            
        if (idx > 0):
            next_item = self.__play_files[idx - 1]
            self.__load_file(next_item, False)
            
            
    def __go_next(self):

        repeat_mode = mb_config.repeat_mode()
        shuffle_mode = mb_config.shuffle_mode()
        
        if (repeat_mode == mb_config.REPEAT_MODE_NONE):
            if (shuffle_mode == mb_config.SHUFFLE_MODE_NONE):
                self.__play_next(False)

            elif (shuffle_mode == mb_config.SHUFFLE_MODE_ONE):
                self.__play_shuffled(False)
                
            elif (shuffle_mode == mb_config.SHUFFLE_MODE_ALL):
                self.__play_shuffled(True)
            
        elif (repeat_mode == mb_config.REPEAT_MODE_ONE):
            if (self.__current_file):
                self.__play_same()
            else:
                self.__play_next(True)

        elif (repeat_mode == mb_config.REPEAT_MODE_ALL):
            if (shuffle_mode == mb_config.SHUFFLE_MODE_NONE):
                self.__play_next(True)

            elif (shuffle_mode == mb_config.SHUFFLE_MODE_ONE):
                self.__play_shuffled(False)

            elif (shuffle_mode == mb_config.SHUFFLE_MODE_ALL):
                self.__play_shuffled(True)
            

    def __play_same(self):
    
        self.__load_file(self.__current_file, False)

        return True
        
        
    def __play_next(self, wraparound):
    
        try:
            idx = self.__play_files.index(self.__current_file)
        except:
            idx = -1
        

        if (idx + 1 < len(self.__play_files)):
            next_item = self.__play_files[idx + 1]
            self.__load_file(next_item, False)
            return True

        elif (wraparound):
            next_item = self.__play_files[0]
            self.__load_file(next_item, False)
            return True
            
        else:
            return False

        
        
    def __play_shuffled(self, from_all):
    
        if (from_all):
            # TODO...
            pass

        if (not self.__random_files):
            self.__random_files = self.__play_files[:]

        idx = random.randint(0, len(self.__random_files) - 1)
        next_item = self.__random_files.pop(idx)
        print self.__random_files
        print idx, "->", next_item
        self.__load_file(next_item, False)
        
        return True


    def __filter_play_files(self):
        """
        Filters the list of playfiles to see if there's cover art to remove
        from the list.
        """
        
        size = len(self.__play_files)
        img_size = len([f for f in self.__play_files
                        if f.mimetype in mimetypes.get_image_types() ])
        ratio = img_size / float(size)
        
        if (ratio < 0.5):
            self.__play_files = [ f for f in self.__play_files
                             if not f.mimetype in mimetypes.get_image_types() ]


    def __show_dialog(self, name):
        """
        Shows the dialog with the given name.
        """

        #print name, self.__dialogs
        dialogs = [ d for d in self.__dialogs if repr(d) == name ]
        if (dialogs):
            dlg = dialogs[0]
            dlg.set_visible(True)
        #end if


    def render_this(self):
    
        if (self.__arr.is_visible()):
            Window.render_this(self)
            
        else:
            x, y = self.get_screen_pos()
            w, h = self.get_size()
            screen = self.get_screen()
        
            screen.fill_area(x, y, w, h, theme.color_mb_background)
            screen.draw_centered_text(values.NAME + " " + values.VERSION,
                                      theme.font_mb_headline,
                                      x, h / 2 - 30, w, 30, theme.color_mb_text)
            screen.draw_centered_text(values.COPYRIGHT,
                                      theme.font_mb_plain,
                                      x, h / 2, w, 30, theme.color_mb_text)
            screen.draw_centered_text("Loading... Please Wait",
                                      theme.font_mb_plain,
                                      x, h - 80, w, 20, theme.color_mb_text)
            screen.fit_pixbuf(theme.mb_logo,
                              w - 120, h - 120, 120, 120)


    def handle_COM_EV_COMPONENT_LOADED(self, component):

        if (isinstance(component, Dialog)):
            if (repr(component) in [ repr(d) for d in self.__dialogs ]):
                logging.error("a dialog with ID '%s' exists already.",
                              repr(component))
            else:
                self.__dialogs.append(component)
                #component.set_parent_window(self)


    def handle_COM_EV_APP_STARTED(self):
    
        # try to restore previous path stack
        try:
            data = open(_PERSISTED_PATH, "r").read()
            path_stack = []
            for d in data.split("\n"):
                f = self.call_service(msgs.CORE_SVC_GET_FILE, d)
                if (f):
                    path_stack.append(f)
                    self.emit_message(msgs.CORE_EV_FOLDER_VISITED, f)
                #end if
            #end for
            self.__browser.set_path_stack(path_stack)
        except:
            pass
    
        self.__arr.set_visible(True)
        self.render()
        
        if (values.uri and (values.uri.startswith("http://") or
                            os.path.exists(values.uri))):
            ext = os.path.splitext(values.uri)[1]
            mimetype = mimetypes.ext_to_mimetype(ext)
            f = self.call_service(msgs.CORE_SVC_GET_FILE,
                                  "adhoc://" + File.pack_path("/", values.uri,
                                                              mimetype))
            print f
            self.__load_file(f, True)
        #end if

    
    def handle_COM_EV_APP_SHUTDOWN(self):

        # save path stack for next start
        data = [ f.full_path for f in self.__browser.get_path_stack() ]
    
        try:
            open(_PERSISTED_PATH, "w").write("\n".join(data))
        except:
            import traceback; traceback.print_exc()
            pass


    def handle_CORE_EV_DEVICE_ADDED(self, ident, device):
            
        if (repr(device) == "navigator.RootDevice"):
            self.__browser.set_root_device(device)
         

    def handle_UI_ACT_SHOW_INFO(self, msg):
    
        dlg = InfoDialog(msg, self)
        dlg.run()


    def handle_UI_ACT_SHOW_DIALOG(self, name):
    
        self.__show_dialog(name)


    def handle_CORE_EV_THEME_CHANGED(self):
    
        self.render()
      

    def handle_CORE_EV_FOLDER_INVALIDATED(self, folder):

        if (self.is_visible()):
            self.__browser.invalidate_folder(folder)
        if (folder and folder == self.__play_folder):
            prev_play_files = self.__play_files[:]
            self.__play_files = [ fl for fl in folder.get_children()
                                  if not fl.mimetype.endswith("-folder") ]
            self.__filter_play_files()
            # remove from random files what's no longer there and add to random
            # files what's new in play files
            self.__random_files = [ f for f in self.__play_files
                                    if f in self.__random_files or
                                       f not in prev_play_files ]


    def handle_CORE_EV_DEVICE_REMOVED(self, dev_id):
    
        folder = self.__browser.get_current_folder()
        if (folder.device_id == dev_id):
            self.__browser.go_root()
        


    def handle_CORE_ACT_SEARCH_ITEM(self, key):
    
        if (self.is_active()):
            #self.__browser.set_message("Search: " + key)
            if (key != self.__search_term):
                self.__browser.set_cursor(1)
            idx = self.__browser.search(key, 1)
            if (idx != -1):
                self.__browser.set_cursor(idx)
                self.__browser.scroll_to_item(idx)
            self.__is_searching = True
            self.__search_term = key
        #end if


    def handle_CORE_EV_SEARCH_CLOSED(self):
    
        #self.__browser.set_message("")
        self.__browser.search("", 1)
        self.__browser.render()
        self.__is_searching = False
        self.__search_term = ""


    def handle_ASR_ACT_ENABLE(self, value):
    
        self.set_flag(windowflags.ASR, value)


    def handle_ASR_EV_PORTRAIT(self):
        
        self.__is_portrait = True
        self.set_flag(windowflags.PORTRAIT, True)
        self.__update_items_per_row(self.__browser.get_current_folder())


    def handle_ASR_EV_LANDSCAPE(self):

        self.__is_portrait = False
        self.set_flag(windowflags.PORTRAIT, False)
        self.__update_items_per_row(self.__browser.get_current_folder())
                    

    def handle_MEDIA_ACT_LOAD_URI(self, uri, mimetype):
    
        self.__load_uri(uri, mimetype)
                    
    
    def handle_MEDIA_ACT_PREVIOUS(self):
    
        self.__go_previous()
  
  
    def handle_MEDIA_ACT_NEXT(self):
    
        self.__go_next()


    def handle_INPUT_EV_UP(self, pressed):

        if (self.is_visible()):
            self.__browser.move(0, -80)


    def handle_INPUT_EV_DOWN(self, pressed):

        if (self.is_visible()):
            self.__browser.move(0, 80)

