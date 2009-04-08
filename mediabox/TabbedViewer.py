from com import Viewer, msgs
from ui.SideTabs import SideTabs
from utils import logging
from theme import theme

import gobject


class TabbedViewer(Viewer):
    """
    Base class for a viewer with tabs.

    @since: 0.96.5
    """

    def __init__(self):
    
        # the currently visible tab element
        self.__current_tab_element = None


        Viewer.__init__(self)
        
        # side tabs
        self.__side_tabs = SideTabs()
        self.add(self.__side_tabs)
        #gobject.timeout_add(0, self.__side_tabs.select_tab, 0)


        
    def add_tab(self, name, element, cb, *args):
        """
        Adds a new tab with the given name for the given view mode.
        """    

        def f():
            if (self.__current_tab_element):
                self.__current_tab_element.set_visible(False)
            element.set_visible(True)
            self.__current_tab_element = element

            if (cb):
                cb(*args)

            self.render()

        self.__side_tabs.add_tab(None, name, f)


    def select_tab(self, idx):
        """
        Selects the given tab.
        """
        
        self.__side_tabs.select_tab(idx)
        

    def set_tabs_visible(self, v):
    
        self.__side_tabs.set_visible(v)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
               
        if (self.__side_tabs.is_visible()):
            self.__side_tabs.set_geometry(w - 70 + 4, 4, 70 - 8, h - 8)
            if (self.__current_tab_element):
                self.__current_tab_element.set_geometry(0, 0, w - 70, h)
        else:
            if (self.__current_tab_element):
                self.__current_tab_element.set_geometry(0, 0, w, h)
       
        



    def handle_message(self, msg, *args):
        """
        Handles incoming messages.
        """
    
        Viewer.handle_message(self, msg, *args)
        
       
        #if (msg == msgs.MEDIASCANNER_EV_SCANNING_FINISHED):
        #    if (self.__current_device and self.__path_stack):
        #        #self.__load_device(self.__current_device)
        #        path = self.__path_stack[-1][0]
        #        #self._load_folder(path, self.__GO_NEW)
        
        """
        # watch for new storage devices
        if (msg == msgs.CORE_EV_DEVICE_ADDED):
            ident, device = args
            #if (device.CATEGORY == device.CATEGORY_INDEX):
            #    gobject.idle_add(self.__add_device, ident, device)
        
        # remove gone storage devices
        elif (msg == msgs.CORE_EV_DEVICE_REMOVED):
            ident = args[0]
            #self.__remove_device(ident)
        """

        """
        if (msg == msgs.MEDIA_ACT_STOP):
            if (self.__media_widget):
                self.__media_widget.stop()
        """   
             
        """
        if (msg == msgs.MEDIA_EV_LOADED):
            self.__list.hilight(-1)
            self.__current_file = None
            self.__may_go_next = False
        """
        
        
        # the following messages are only accepted when the viewer is active
        if (not self.is_active()): return
        
        """
        if (msg == msgs.INPUT_ACT_REPORT_CONTEXT):
            self.__update_input_context()
        """
        
        """
        elif (msg == msgs.INPUT_EV_DOWN):
            w, h = self.__list.get_size()
            idx = self.__list.get_index_at(h)
            if (idx != -1):
                items = self.__list.get_items()
                new_idx = min(len(items), idx + 2)
                self.__list.scroll_to_item(new_idx)
                #self.emit_message(msgs.CORE_ACT_SCROLL_UP)
            
        elif (msg == msgs.INPUT_EV_UP):
            idx = self.__list.get_index_at(0)
            if (idx != -1):
                new_idx = max(0, idx - 2)
                self.__list.scroll_to_item(new_idx)
                #self.emit_message(msgs.CORE_ACT_SCROLL_DOWN)
        """
        
        # load selected device or file
        """
        if (msg == msgs.CORE_ACT_LOAD_ITEM):
            idx = args[0]
            #if (self.__view_mode == self._VIEWMODE_BROWSER):
            #    dev = self.__device_items[idx]
            #    if (dev != self.__current_device):
            #        self.__load_device(dev)

            #elif (self.__view_mode == self._VIEWMODE_SPLIT_BROWSER):
            #    if (len(self.__path_stack) > 1):
            #        folder = self.__sibling_folders[idx]
            #        if (self.__path_stack):
            #            self.__path_stack.pop()
            #        self._load_folder(folder, None)
            #    else:
            #        dev = self.__device_items[idx]
            #        if (dev != self.__current_device):
            #            self.__load_device(dev)               
                    
            if (self.__view_mode == self._VIEWMODE_PLAYER_NORMAL):
                item = self.__playable_items[idx]
                if (item != self.__current_file):
                    self.__load_file(item, MediaWidget.DIRECTION_NONE)
        """

        """
        # provide search-as-you-type
        if (msg == msgs.CORE_ACT_SEARCH_ITEM):
            key = args[0]
            self.__search(key)
        """
    
        """
        # select a device
        if (msg == msgs.UI_ACT_SELECT_DEVICE):
            dev_id = args[0]
            print "SELECT", dev_id
        """


        """
        # go to previous
        elif (msg == msgs.MEDIA_ACT_PREVIOUS):
            self.__go_previous()
            
        # go to next
        elif (msg == msgs.MEDIA_ACT_NEXT):
            self.__go_next()


        # the following messages are only accepted when we have a media widget
        if (not self.__media_widget): return


        # watch FULLSCREEN hw key
        if (msg == msgs.INPUT_EV_FULLSCREEN):
            #if (self.__view_mode in \
            #  (self._VIEWMODE_PLAYER_NORMAL, self._VIEWMODE_PLAYER_FULLSCREEN)):
            self.__on_toggle_fullscreen()
                
        # watch INCREMENT hw key
        elif (msg == msgs.INPUT_EV_VOLUME_UP):
            self.__media_widget.increment()
            
        # watch DECREMENT hw key
        elif (msg == msgs.INPUT_EV_VOLUME_DOWN):
            self.__media_widget.decrement()

                
        elif (msg == msgs.INPUT_EV_PLAY):
            self.__media_widget.play_pause()

        # go to previous
        elif (msg == msgs.INPUT_EV_PREVIOUS):
            self.__go_previous()
            
        # go to next
        elif (msg == msgs.INPUT_EV_NEXT):
            self.__go_next()
        """
   

    def show(self):
    
        Viewer.show(self)
        
        if (not self.__current_tab_element):
            self.select_tab(0)

