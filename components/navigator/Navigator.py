from com import View, msgs
from RootDevice import RootDevice
from mediabox.StorageBrowser import StorageBrowser
from ui.layout import HBox
from ui.ImageButton import ImageButton
from ui.Image import Image
from ui.Slider import Slider
from ui.Toolbar import Toolbar
from ui.Widget import Widget
from utils import mimetypes
from utils import logging
from mediabox import config as mb_config
from theme import theme

import random
import time


class Navigator(View):

    ICON = theme.mb_viewer_audio
    TITLE = "Navigator"
    PRIORITY = 0

    def __init__(self):
    
        # the file that is currently playing    
        self.__current_file = None

        # list for choosing random files from when in shuffle mode
        self.__random_files = []
        
        self.__is_searching = False
        self.__search_term = ""
        
        self.__key_hold_down_timestamp = 0
        self.__skip_letter = False

    
        View.__init__(self)

        # browser list slider
        self.__browser_slider = Slider(theme.mb_list_slider)
        self.__browser_slider.set_mode(self.__browser_slider.VERTICAL)
        #if (show_sliders):
        #    browser_hbox.add(self.__browser_slider, False)
        
        # file browser
        self.__browser = StorageBrowser()
        self.__browser.associate_with_slider(self.__browser_slider)
        self.__browser.set_thumbnailer(self.__on_request_thumbnail)
        #browser_hbox.add(self.__browser, True)
        self.__browser.connect_folder_opened(self.__on_open_folder)
        self.__browser.connect_file_opened(self.__on_open_file)
        self.__browser.connect_file_enqueued(self.__on_enqueue_file)
        self.__browser_slider.connect_button_pressed(
                                    lambda a,b:self.__browser.stop_scrolling())
        self.add(self.__browser)

        #hbox = HBox()
        #hbox.set_visible(False)
        #self.add(hbox)


        # toolbar
        self.__toolbar = Toolbar()
        self.add(self.__toolbar)

        self.__btn_home = ImageButton(theme.mb_btn_home_1,
                                      theme.mb_btn_home_2)
        self.__btn_home.connect_clicked(self.__on_btn_home)
        
        self.__btn_history = ImageButton(theme.mb_btn_home_1,
                                         theme.mb_btn_home_2)
        self.__btn_history.connect_clicked(self.__on_btn_history)

        self.__btn_bookmarks = ImageButton(theme.mb_btn_bookmark_1,
                                           theme.mb_btn_bookmark_2)
        self.__btn_bookmarks.connect_clicked(self.__on_btn_bookmarks)

        self.__btn_back = ImageButton(theme.mb_btn_dir_up_1,
                                      theme.mb_btn_dir_up_2)
        self.__btn_back.connect_clicked(self.__on_btn_back)

        self.__btn_add = ImageButton(theme.mb_btn_add_1,
                                     theme.mb_btn_add_2)
        self.__btn_add.set_visible(False)
        self.__btn_add.connect_clicked(self.__on_btn_add)

       
        self.__browser.set_root_device(RootDevice())
        #self.add_tab(tab_label_1, browser_hbox, self.__on_browser_tab)
        #self.add_tab(tab_label_2, self.__media_box, self.__on_player_tab)


    def __update_toolbar(self):
        """
        Updates the contents of the toolbar.
        """

        if (self.__browser.is_visible()):
            self.__toolbar.set_toolbar(self.__btn_home,
                                       #self.__btn_history,
                                       self.__btn_bookmarks,
                                       self.__btn_back)
            
        return
        
        items = []
        
        current_folder = self.__browser.get_current_folder()

        if (current_folder):
            if (current_folder.folder_flags & current_folder.ITEMS_DOWNLOADABLE):
                self.__btn_keep.set_active(False)
                items.append(self.__btn_keep)        

            if (current_folder.folder_flags & current_folder.ITEMS_ADDABLE):
                items.append(Image(theme.mb_toolbar_space_1))
                items.append(self.__btn_add)
        
            if (self.__media_box.is_visible()):
                if (self.__media_widget):
                    items += self.__media_widget.get_controls()
        
                if (current_folder.folder_flags & current_folder.ITEMS_SKIPPABLE):            
                    items.append(Image(theme.mb_toolbar_space_1))
                    items.append(self.__btn_prev)
                    items.append(self.__btn_next)

        if (self.__browser.is_visible()):
            items.append(Image(theme.mb_toolbar_space_1))
            items.append(self.__btn_back)

        self.set_toolbar(items)



    def show(self):
    
        View.show(self)
        names = [ p.name for p in self.__browser.get_path() ]
        #title = u" \u00bb ".join(names)
        title = names[-1]
        #self.set_title(title)

        self.__update_toolbar()
        self.emit_message(msgs.INPUT_EV_CONTEXT_BROWSER)

       
    def __on_open_file(self, f):
    
        self.__load_file(f)


    def __on_open_folder(self, f):

        if (self.__browser.is_visible()):
            names = [ p.name for p in self.__browser.get_path() ]
            #title = u" \u00bb ".join(names)
            title = names[-1]
            names.reverse()
            acoustic_title = "Entering " + " in ".join(names)
            #self.set_title(title)
            self.emit_message(msgs.UI_ACT_TALK, acoustic_title)
            self.emit_message(msgs.CORE_EV_FOLDER_VISITED, f)
            self.__update_toolbar()
        #end if
        
        self.__random_files = []


    def __on_enqueue_file(self, f):
    
        self.emit_message(msgs.PLAYLIST_ACT_APPEND, f)
        

    def __on_request_thumbnail(self, f, cb, *args):

        if (cb):
            # create thumbnail
            self.call_service(msgs.MEDIASCANNER_SVC_LOAD_THUMBNAIL, f,
                              cb, *args)
            return None
            
        else:
            # lookup existing thumbnail
            thumbnail = self.call_service(
                msgs.MEDIASCANNER_SVC_LOOKUP_THUMBNAIL, f) or None
            return thumbnail


    def __on_btn_home(self):
        """
        Reacts on pressing the [Home] button.
        """

        self.__browser.go_root()
        
        
    def __on_btn_history(self):
        """
        Reacts on pressing the [History] button.
        """
        
        f = self.call_service(msgs.CORE_SVC_GET_FILE, "history:///")
        if (f):
            self.__browser.load_folder(f, self.__browser.GO_PARENT, True)


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

            
            
    def __on_btn_add(self):
        """
        Reacts on pressing the [Add] button.
        """
        
        folder = self.__browser.get_current_folder()
        if (folder):
            f = folder.new_file()
        #    if (f):
        #        self.__browser.reload_current_folder()
        




    def __load_file(self, f):
        """
        Loads the given file.
        """

        self.__current_file = f

        if (not f.mimetype in mimetypes.get_image_types()):
            self.emit_message(msgs.MEDIA_ACT_STOP)

        self.emit_message(msgs.MEDIA_ACT_LOAD, f)
        self.emit_message(msgs.MEDIA_EV_LOADED, self, f)


    def render_this(self):
    
        w, h = self.get_size()
        self.__browser.set_geometry(0, 0, w, h - 70)
        self.__toolbar.set_geometry(0, h - 70, w, 70)


    def get_browser(self):
    
        return self.__browser
      

    def handle_CORE_EV_FOLDER_INVALIDATED(self, folder):
    
        self.__browser.invalidate_folder(folder)


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

    
    def handle_MEDIA_EV_LOADED(self, viewer, f):
    
        self.__browser.set_hilight(-1)
        self.__current_file = None
        self.__may_go_next = False
  
          

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

