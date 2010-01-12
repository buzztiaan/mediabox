from com import Dialog, msgs
from RootDevice import RootDevice
from mediabox.StorageBrowser import StorageBrowser
from ui.Button import Button
from ui.ImageButton import ImageButton
from ui.Slider import Slider
from ui.Toolbar import Toolbar
from ui.dialog import OptionDialog
from ui.layout import Arrangement
from utils import mimetypes
from utils import logging
from mediabox import config as mb_config
from utils.ItemScheduler import ItemScheduler
import platforms
from theme import theme

import gobject
import random
import time


_LANDSCAPE_ARRANGEMENT = """
  <arrangement>
    <widget name="toolbar"
            x1="-80" y1="0" x2="100%" y2="100%"/>

    <if-visible name="btn_add">
      <widget name="btn_add"
              x1="0" y1="0" x2="-80" y2="80"/>
      <widget name="slider"
              x1="0" y1="80" x2="40" y2="100%"/>
      <widget name="browser"
              x1="40" y1="80" x2="-80" y2="100%"/>
    </if-visible>

    <if-invisible name="btn_add">
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

    <if-visible name="btn_add">
      <widget name="btn_add"
              x1="0" y1="0" x2="100%" y2="80"/>
      <widget name="slider"
              x1="0" y1="80" x2="40" y2="-80"/>
      <widget name="browser"
              x1="40" y1="80" x2="100%" y2="-80"/>
    </if-visible>

    <if-invisible name="btn_add">
      <widget name="slider"
              x1="0" y1="0" x2="40" y2="-80"/>
      <widget name="browser"
              x1="40" y1="0" x2="100%" y2="-80"/>
    </if-invisible>                
  </arrangement>
"""


class Navigator(Dialog):
    """
    Navigator dialog for browsing media.
    """

    def __init__(self):
    
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
        
        self.__root_dev = RootDevice()
        
    
        Dialog.__init__(self)

        # browser list slider
        self.__browser_slider = Slider(theme.mb_list_slider)
        self.__browser_slider.set_mode(Slider.VERTICAL)
        #self.add(self.__browser_slider)

        
        # file browser
        self.__browser = StorageBrowser()
        self.__browser.associate_with_slider(self.__browser_slider)
        self.__browser.connect_folder_begin(self.__on_begin_folder)
        self.__browser.connect_folder_progress(self.__on_progress_folder)
        self.__browser.connect_folder_complete(self.__on_complete_folder)
        #self.__browser.connect_file_added_to_library(self.__on_add_file_to_lib)
        self.__browser.connect_file_opened(self.__on_open_file)
        #self.__browser.connect_file_enqueued(self.__on_enqueue_file)
        #self.__browser.connect_file_bookmarked(self.__on_bookmark_file)
        self.__browser_slider.connect_button_pressed(
                                    lambda a,b:self.__browser.stop_scrolling())
        #self.add(self.__browser)

        # [Add] button
        self.__btn_add = Button("Add New")
        self.__btn_add.set_visible(False)
        self.__btn_add.connect_clicked(self.__on_btn_add)
        #self.add(self.__btn_add)

        # beta version!
        #self.__browser.add_overlay_renderer(self.__render_beta_mark)


        # toolbar
        self.__toolbar = Toolbar()
        #self.add(self.__toolbar)

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


        # arrangement
        self.__arr = Arrangement()
        self.__arr.connect_resized(self.__update_layout)
        self.__arr.add(self.__browser_slider, "slider")
        self.__arr.add(self.__browser, "browser")
        self.__arr.add(self.__btn_add, "btn_add")
        self.__arr.add(self.__toolbar, "toolbar")
        self.add(self.__arr)


    def __update_layout(self):
    
        w, h = self.get_size()
        if (w < h):
            # portrait mode
            self.__arr.set_xml(_PORTRAIT_ARRANGEMENT)
        else:
            # landscape mode
            self.__arr.set_xml(_LANDSCAPE_ARRANGEMENT)


    def __render_beta_mark(self, screen):
    
        x, y = self.__browser.get_screen_pos()
        w, h = self.__browser.get_size()
        screen.draw_pixbuf(theme.mb_beta_mark, w - 128, h - 48)


    def __update_toolbar(self):
        """
        Updates the contents of the toolbar.
        """

        cwd = self.__browser.get_current_folder()
        items = [self.__btn_home,
                 self.__btn_history,
                 self.__btn_back]
        
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



    """
    def __update_menu(self):
        ""
        Updates the contents of the window menu.
        ""

        cwd = self.__browser.get_current_folder()
        opts = []
        
        opts.append((None, "Select Output Device", self.__on_menu_select_output))
        
        if (cwd.folder_flags & cwd.ITEMS_SORTABLE):
            opts.append((None, "Rearrange", self.__on_menu_rearrange))
            
        opts.append((None, "Info", None))
        
        if (platforms.PLATFORM == platforms.MAEMO5):
            opts.append((None, "FM Transmitter", self.__on_menu_fmtx))
            
        self.set_window_menu(*opts)
    """
    
    
    """
    def show(self):
    
        SubView.show(self)
        names = [ p.name for p in self.__browser.get_path() ]
        #title = u" \u00bb ".join(names)
        title = names[-1]
        #self.set_title(title)

        self.__update_toolbar()
        #self.__update_menu()
        self.emit_message(msgs.INPUT_EV_CONTEXT_BROWSER)
    """
    

    def _visibility_changed(self):
        
        Dialog._visibility_changed(self)
        if (self.is_visible()):
            self.__tn_scheduler.resume()
        else:
            self.__tn_scheduler.halt()


    def __on_menu_select_output(self):
    
        self.emit_message(msgs.MEDIA_ACT_SELECT_OUTPUT, None)


    def __on_menu_rearrange(self):
    
        def on_done():
            self.__browser.set_drag_sort_enabled(False)
            self.__update_toolbar()
    
        self.__browser.set_drag_sort_enabled(True)
    
        btn_done = ImageButton(theme.mb_btn_history_1,
                               theme.mb_btn_history_2)
        btn_done.connect_clicked(on_done)
        self.__toolbar.set_toolbar(btn_done)
        
        
    def __on_menu_fmtx(self):
    
        import platforms
        platforms.plugin_execute("libcpfmtx.so")
          
       
    def __on_open_file(self, f):
            
        self.__load_file(f, True)
        #self.set_visible(False)


    def __on_begin_folder(self, f):
    
        self.__tn_scheduler.new_schedule(5, self.__on_load_thumbnail)
        self.__tn_scheduler.halt()
        
        #self.set_title(f.name)
        self.set_busy(True)
        
        if (f.folder_flags & f.ITEMS_ADDABLE):
            self.__btn_add.set_visible(True)
        else:
            self.__btn_add.set_visible(False)
                       
        self.__update_layout()
        self.render()
        self.__update_items_per_row(f)


    def __on_progress_folder(self, f, c):

        if (c.icon): return

        item = self.__browser.get_items()[-1]
        thumbpath, is_final = \
          self.call_service(msgs.THUMBNAIL_SVC_LOOKUP_THUMBNAIL, c)

        item.set_icon(thumbpath)
        
        if (not is_final):
            self.__tn_scheduler.add(item, c)


    def __on_complete_folder(self, f):

        self.set_busy(False)
        
        names = [ p.name for p in self.__browser.get_path() ]
        #title = u" \u00bb ".join(names)
        title = names[-1]
        names.reverse()
        acoustic_title = "Entering " + " in ".join(names)
        self.set_title(title)
        self.emit_message(msgs.UI_ACT_TALK, acoustic_title)
        self.emit_message(msgs.CORE_EV_FOLDER_VISITED, f)
        self.__update_toolbar()
        #self.__update_menu()

        if (self.is_visible()):
            self.__tn_scheduler.resume()

    """
    def __on_add_file_to_lib(self, f):
    
        self.emit_message(msgs.LIBRARY_ACT_ADD_MEDIAROOT, f)
        

    def __on_enqueue_file(self, f):
    
        dlg = OptionDialog("Select a Playlist")
        playlists = self.call_service(msgs.PLAYLIST_SVC_GET_LISTS)
        print playlists
        if (not playlists): return
        
        # select playlist
        if (len(playlists) == 1):
            playlist = playlists[0]
        
        else:
            for pl in playlists:
                dlg.add_option(None, pl)
            if (dlg.run() == 0):
                choice = dlg.get_choice()
                playlist = playlists[choice]
        #end for
    
        self.emit_message(msgs.PLAYLIST_ACT_APPEND, playlist, f)


    def __on_bookmark_file(self, f):
    
        f.bookmarked = True
    """


    def __update_thumbnail(self, item, thumbpath):
    
        item.set_icon(thumbpath)
        #idx = self.get_items().index(item)
        # TODO: only render if item is currently on screen
        self.__browser.invalidate()
        self.__browser.render()


    def __on_load_thumbnail(self, item, f):

        def on_loaded(thumbpath):
            if (thumbpath):
                self.__update_thumbnail(item, thumbpath)
            
            #if (self.is_visible()):
            self.__tn_scheduler.resume()
    
        # load thumbnail
        self.__tn_scheduler.halt()
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

            
            
    def __on_btn_add(self):
        """
        Reacts on pressing the [Add] button.
        """
        
        folder = self.__browser.get_current_folder()
        if (folder):
            f = folder.new_file()
        #    if (f):
        #        self.__browser.reload_current_folder()
        




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
            #if (not f.mimetype in mimetypes.get_image_types()):
            self.emit_message(msgs.MEDIA_ACT_STOP)
            self.emit_message(msgs.MEDIA_ACT_LOAD, f)

            # update set of play files
            self.__current_file = f
            self.__browser.hilight_file(f)

            self.set_visible(False)

            folder = self.__browser.get_current_folder()
            if (is_manual and folder != self.__play_folder):
                self.__play_folder = folder
                self.__play_files = [ fl for fl in self.__browser.get_files()
                                      if not fl.mimetype.endswith("-folder") ]
                self.__random_files = []
                


    def render_this(self):
    
        w, h = self.get_size()
        self.__arr.set_geometry(0, 0, w, h)


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


    def handle_CORE_EV_THEME_CHANGED(self):
    
        self.render()
      

    def handle_CORE_EV_FOLDER_INVALIDATED(self, folder):
    
        self.__browser.invalidate_folder(folder)
        if (folder and folder == self.__play_folder):
            self.__play_files = [ fl for fl in folder.get_children()
                                  if not fl.mimetype.endswith("-folder") ]
            self.__random_files = []


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

    
    def handle_CORE_EV_APP_STARTED(self):

        gobject.idle_add(self.__browser.set_root_device, self.__root_dev)


    def handle_CORE_EV_SEARCH_CLOSED(self):
    
        #self.__browser.set_message("")
        self.__browser.search("", 1)
        self.__browser.render()
        self.__is_searching = False
        self.__search_term = ""


    def handle_ASR_EV_PORTRAIT(self):
        
        self.__is_portrait = True
        self.set_visible(False)
        self.__update_items_per_row(self.__browser.get_current_folder())


    def handle_ASR_EV_LANDSCAPE(self):

        self.__is_portrait = False
        self.set_visible(False)
        self.__update_items_per_row(self.__browser.get_current_folder())
                    
    
    def handle_MEDIA_ACT_PREVIOUS(self):
    
        self.__go_previous()
  
  
    def handle_MEDIA_ACT_NEXT(self):
    
        self.__go_next()
  
          

    def handle_INPUT_ACT_REPORT_CONTEXT(self):
    
        if (self.is_active()):
            self.emit_message(msgs.INPUT_EV_CONTEXT_BROWSER)



    def handle_INPUT_EV_UP(self):

        if (not self.is_active()): return

        now = time.time()
        #if (now < self.__key_hold_down_timestamp + 0.1):
        #    self.__skip_letter = True
        #elif (now > self.__key_hold_down_timestamp + 0.5):
        self.__skip_letter = False
        self.__key_hold_down_timestamp = now

        if (self.__is_searching):
            idx = self.__browser.search(self.__search_term, -1)
            if (idx != -1):
                self.__browser.set_cursor(idx)
                #self.__browser.scroll_to_item(idx)
            
        else:
            self.__browser.move_cursor(-1, self.__skip_letter)
            cursor = self.__browser.get_cursor()
            item = self.__browser.get_item(cursor)
            f = item.get_file()
            self.emit_message(msgs.UI_ACT_TALK, f.acoustic_name or f.name)
            

    def handle_INPUT_EV_PAGE_UP(self):

        if (self.is_active()):        
            idx = self.__browser.get_index_at(0)
            if (idx != -1):
                new_idx = max(0, idx - 2)
                self.__browser.scroll_to_item(new_idx)


    def handle_INPUT_EV_DOWN(self):

        if (not self.is_active()): return

        now = time.time()
        #if (now < self.__key_hold_down_timestamp + 0.1):
        #    self.__skip_letter = True
        #elif (now > self.__key_hold_down_timestamp + 0.5):
        self.__skip_letter = False
        self.__key_hold_down_timestamp = now
        
        if (self.__is_searching):
            idx = self.__browser.search(self.__search_term, 1)
            if (idx != -1):            
                self.__browser.set_cursor(idx)
                #self.__browser.scroll_to_item(idx)
            
        else:
            self.__browser.move_cursor(1, self.__skip_letter)
            cursor = self.__browser.get_cursor()
            item = self.__browser.get_item(cursor)
            f = item.get_file()
            self.emit_message(msgs.UI_ACT_TALK, f.acoustic_name or f.name)



    def handle_INPUT_EV_PAGE_DOWN(self):
    
        if (self.is_active()):
            w, h = self.__browser.get_size()
            idx = self.__browser.get_index_at(h)
            if (idx != -1):
                items = self.__browser.get_items()
                new_idx = min(len(items), idx + 2)
                self.__browser.scroll_to_item(new_idx)


    def handle_INPUT_EV_RIGHT(self):
    
        if (self.is_active()):
            self.select_tab(1)


    def handle_INPUT_EV_ENTER(self):
    
        if (self.is_active()):
            cursor = self.__browser.get_cursor()
            if (cursor != -1):
                self.__browser.trigger_item_button(cursor)

    
    def handle_INPUT_EV_GO_PARENT(self):
    
        if (self.is_active()):
            self.__browser.go_parent()


    def handle_INPUT_EV_MENU(self):
    
        #if (self.is_active()):
        #self.emit_message(msgs.MEDIA_ACT_SELECT_OUTPUT, None)
        self.emit_message(msgs.UI_ACT_SHOW_DIALOG, "FMTXDialog")

