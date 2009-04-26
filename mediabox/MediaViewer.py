from com import msgs
from TabbedViewer import TabbedViewer
from StorageBrowser import StorageBrowser
from ui.BoxLayout import BoxLayout
from ui.HBox import HBox
from ui.ImageButton import ImageButton
from ui.Image import Image
from ui.Slider import Slider
from ui import dialogs
from utils import mimetypes
from utils import logging
from mediabox.MediaWidget import MediaWidget
from mediabox import viewmodes
from mediabox import config as mb_config
from theme import theme

import random


class MediaViewer(TabbedViewer):
    """
    Base class for media viewers.
    
    @since: 0.96.5
    """

    ICON = None
    PRIORITY = 0

    def __init__(self, root_device, tab_label_1, tab_label_2):

        self.__is_fullscreen = False

        # the file that is currently playing    
        self.__current_file = None
    
        # the current media widget
        self.__media_widget = None

        # whether we may advance to the next item
        self.__may_go_next = True
        
        # list for choosing random files from when in shuffle mode
        self.__random_files = []
        
        self.__is_searching = False
        self.__search_term = ""

    
        TabbedViewer.__init__(self)
        
        # file browser
        self.__browser = StorageBrowser()
        self.__browser.set_thumbnailer(self.__on_request_thumbnail)
        self.__browser.set_visible(False)
        self.add(self.__browser)
        self.__browser.connect_folder_opened(self.__on_open_folder)
        self.__browser.connect_file_opened(self.__on_open_file)
        self.__browser.connect_file_enqueued(self.__on_enqueue_file)

        hbox = HBox()
        hbox.set_visible(False)
        self.add(hbox)

        # volume/zoom slider
        self.__slider = Slider(theme.mb_slider_volume)
        self.__slider.set_mode(self.__slider.VERTICAL)
        self.__slider.set_value(0.5)
        self.__slider.connect_value_changed(self.__on_slider_changed)
        #self.__slider.set_visible(False)
        hbox.add(self.__slider, False)

        # media widget box
        self.__media_box = BoxLayout()
        #self.__media_box.set_visible(False)
        hbox.add(self.__media_box, True)


        # toolbar
        self.__btn_back = ImageButton(theme.mb_btn_dir_up_1,
                                      theme.mb_btn_dir_up_2)
        self.__btn_back.connect_clicked(self.__on_btn_back)

        self.__btn_add = ImageButton(theme.mb_btn_add_1,
                                     theme.mb_btn_add_2)
        self.__btn_add.set_visible(False)
        self.__btn_add.connect_clicked(self.__on_btn_add)

        self.__btn_prev = ImageButton(theme.mb_btn_previous_1,
                                      theme.mb_btn_previous_2)
        self.__btn_prev.connect_clicked(self.__go_previous)

        self.__btn_next = ImageButton(theme.mb_btn_next_1,
                                      theme.mb_btn_next_2)
        self.__btn_next.connect_clicked(self.__go_next)

        self.__btn_keep = ImageButton(theme.mb_btn_keep_1,
                                      theme.mb_btn_keep_2, True)
        self.__btn_keep.connect_clicked(self.__on_btn_keep)

        
        self.__browser.set_root_device(root_device)
        self.add_tab(tab_label_1, self.__browser, self.__on_browser_tab)
        self.add_tab(tab_label_2, hbox, self.__on_player_tab)


    def __update_toolbar(self):
        """
        Updates the contents of the toolbar.
        """
        
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



    def __on_browser_tab(self):
    
        names = [ p.name for p in self.__browser.get_path() ]
        title = u" \u00bb ".join(names)
        self.set_title(title)

        self.__update_toolbar()
        self.emit_message(msgs.INPUT_EV_CONTEXT_BROWSER)
        #self.emit_message(msgs.UI_ACT_RENDER)


    def __on_player_tab(self):
    
        if (self.__current_file):
            self.set_title(self.__current_file.name)
        else:
            self.set_title("")
        
        self.__update_toolbar()
        self.emit_message(msgs.INPUT_EV_CONTEXT_PLAYER)
        #self.emit_message(msgs.UI_ACT_RENDER)
        
        w, h = self.get_size()
        self.__slider.set_geometry(0, 0, 80, h)
        
        
    def __on_open_file(self, f):
    
        self.__load_file(f, MediaWidget.DIRECTION_NONE)


    def __on_open_folder(self, f):

        names = [ p.name for p in self.__browser.get_path() ]
        title = u" \u00bb ".join(names)
        names.reverse()
        acoustic_title = "Entering " + " in ".join(names)
        self.set_title(title)
        self.emit_message(msgs.UI_ACT_TALK, acoustic_title)

        self.__update_toolbar()


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


    def __on_toggle_fullscreen(self):
    
        self.__is_fullscreen = not self.__is_fullscreen
        if (self.__is_fullscreen):
            self.set_tabs_visible(False)
            self.__slider.set_visible(False)
            self.emit_message(msgs.UI_ACT_VIEW_MODE, viewmodes.FULLSCREEN)
            self.render()
        else:
            self.set_tabs_visible(True)
            self.__slider.set_visible(True)
            self.emit_message(msgs.UI_ACT_VIEW_MODE, viewmodes.NO_STRIP)
            self.emit_message(msgs.UI_ACT_RENDER)

        self.handle_INPUT_ACT_REPORT_CONTEXT()


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
        
        """
        if (self.__path_stack):
            path, nil = self.__path_stack[-1]
            f = path.new_file()
            if (f):
                self.__add_file(f, [], -1)
                #self._load_folder(path, None)
                #self.__list.invalidate_buffer()
                self.__list.render()
        """


    def __on_btn_keep(self):
        """
        Reacts on pressing the [Keep] button.
        """

        self.__btn_keep.set_active(True)

        if (self.__current_file):
            self.__current_file.keep()


    def __on_media_position(self, info):
        """
        Reacts when the media playback position has changed.
        """
    
        self.set_info(info)


    def __on_media_eof(self):
        """
        Reacts on media EOF.
        """
        
        logging.debug("reached EOF")
        self.__may_go_next = True
        
        self.emit_message(msgs.MEDIA_EV_EOF)
        self.__browser.hilight_file(None)

        folder = self.__browser.get_current_folder()
        if (folder.folder_flags & folder.ITEMS_SKIPPABLE):
            if (self.__may_go_next):
                logging.debug("going to next item")
                self.__go_next()


    def __on_media_scaled(self, v):
        """
        Reacts on changing the scaling value.
        """

        self.emit_message(msgs.MEDIA_EV_VOLUME_CHANGED, int(v * 100))
        self.__slider.set_value(v)


    def __on_slider_changed(self, v):
    
        if (self.__media_widget):
            self.__media_widget.set_scaling(v)


    def __go_previous(self):

        playable_files = [ f for f in self.__browser.get_files()
                           if not f.mimetype.endswith("-folder") ]

        try:
            idx = playable_files.index(self.__current_file)
        except ValueError:
            return False
            
        if (idx > 0):
            next_item = playable_files[idx - 1]
            self.__load_file(next_item, MediaWidget.DIRECTION_PREVIOUS)
            
            
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
            self.__play_same()

        elif (repeat_mode == mb_config.REPEAT_MODE_ALL):
            if (shuffle_mode == mb_config.SHUFFLE_MODE_NONE):
                self.__play_next(True)

            elif (shuffle_mode == mb_config.SHUFFLE_MODE_ONE):
                self.__play_shuffled(False)

            elif (shuffle_mode == mb_config.SHUFFLE_MODE_ALL):
                self.__play_shuffled(True)
            

    def __play_same(self):
    
        self.__load_file(self.__current_file, MediaWidget.DIRECTION_NONE)

        return True
        
        
    def __play_next(self, wraparound):
        
        playable_files = [ f for f in self.__browser.get_files()
                           if not f.mimetype.endswith("-folder") ]
        try:
            idx = playable_files.index(self.__current_file)
        except:
            idx = -1
        

        if (idx + 1 < len(playable_files)):
            next_item = playable_files[idx + 1]
            self.__load_file(next_item, MediaWidget.DIRECTION_NEXT)
            return True

        elif (wraparound):
            next_item = playable_files[0]
            self.__load_file(next_item, MediaWidget.DIRECTION_NEXT)
            return True
            
        else:
            return False

        
        
    def __play_shuffled(self, from_all):
    
        if (from_all):
            # TODO...
            pass

        if (not self.__random_files):
            self.__random_files = [ f for f in self.__browser.get_files()
                                    if not f.mimetype.endswith("-folder") ]

        idx = random.randint(0, len(self.__random_files) - 1)
        next_item = self.__random_files.pop(idx)
        self.__load_file(next_item, MediaWidget.DIRECTION_NEXT)
        
        return True



    def __load_file(self, f, direction):
        """
        Loads the given file.
        """

        self.__current_file = f

        if (not f.mimetype in mimetypes.get_image_types()):
            self.emit_message(msgs.MEDIA_ACT_STOP)
            self.__slider.set_image(theme.mb_slider_volume)
        else:
            self.__slider.set_image(theme.mb_slider_zoom)
            
        # request media widget
        media_widget = self.call_service(
                        msgs.MEDIAWIDGETREGISTRY_SVC_GET_WIDGET,
                        self, f.mimetype)

        if (not media_widget):
            dialogs.error("Unhandled Type",
                            "There is no handler for\n"
                            "MIME type '%s'" % f.mimetype)
            return
            
        # don't load video if the viewer is not visible
        if (f.mimetype in mimetypes.get_video_types() and not self.is_visible()):
            return
            
        # remove old media widget
        if (media_widget != self.__media_widget):
            if (self.__media_widget):
                self.__media_widget.stop()
                self.__media_box.remove(self.__media_widget)
            self.__media_widget = media_widget                
                        
        #self.__update_toolbar()
        #self.__update_title()
        
        self.__media_widget.set_visible(True)
        self.__media_widget.connect_media_position(self.__on_media_position)
        self.__media_widget.connect_media_eof(self.__on_media_eof)
        self.__media_widget.connect_media_scaled(self.__on_media_scaled)
        self.__media_widget.connect_media_previous(self.__go_previous)
        self.__media_widget.connect_media_next(self.__go_next)
        self.__media_widget.connect_fullscreen_toggled(
                                            self.__on_toggle_fullscreen)
        logging.debug("using media widget [%s] for MIME type %s" \
                        % (str(self.__media_widget), f.mimetype))
        if (not self.__media_widget in self.__media_box.get_children()):
            self.__media_box.add(self.__media_widget)

        if (not self.__media_box.is_visible()):
            self.select_tab(1)
        else:
            self.set_title(self.__current_file.name)

        volume = mb_config.volume()
        self.__slider.set_value(volume / 100.0)

        self.__browser.hilight_file(f)

        #self.emit_message(msgs.UI_ACT_RENDER)
        self.__media_widget.load(f, direction)
        self.emit_message(msgs.MEDIA_EV_LOADED, self, f)

        playable_files = [ fl for fl in self.__browser.get_files()
                           if not fl.mimetype.endswith("-folder") ]
        try:
            idx = playable_files.index(f)
        except:
            pass
        else:
            if (idx + 1 < len(playable_files)):
                self.__media_widget.preload(playable_files[idx + 1])


    def get_browser(self):
    
        return self.__browser
        
        
    def get_player(self):
    
        return self.__media_widget
        
        
    def show(self):
    
        TabbedViewer.show(self)
        self.__update_toolbar()
        
        
    def handle_CORE_EV_APP_SHUTDOWN(self):

        if (self.__media_widget):
            self.__media_widget.close()


    def handle_CORE_EV_FOLDER_INVALIDATED(self, folder):
    
        self.__browser.invalidate_folder(folder)


    def handle_CORE_ACT_SEARCH_ITEM(self, key):
    
        if (self.is_active()):
            self.__browser.set_message("Search: " + key)
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
    
        self.__browser.set_message("")
        self.__browser.render()
        self.__is_searching = False
        self.__search_term = ""

    
    def handle_MEDIA_EV_LOADED(self, viewer, f):
    
        self.__browser.hilight(-1)
        self.__current_file = None
        self.__may_go_next = False


    def handle_MEDIA_ACT_PLAY(self):

        if (self.__media_widget and self.is_visible()):
            self.__media_widget.stop()
            self.__media_widget.play_pause()
        
        
    def handle_MEDIA_ACT_STOP(self):
    
        if (self.__media_widget):
            self.__media_widget.stop()


    def handle_INPUT_ACT_REPORT_CONTEXT(self):
    
        if (self.is_active()):
            if (self.__browser.is_visible()):
                self.emit_message(msgs.INPUT_EV_CONTEXT_BROWSER)

            elif (self.__media_box.is_visible()):
                if (self.__is_fullscreen):
                    self.emit_message(msgs.INPUT_EV_CONTEXT_FULLSCREEN)
                else:
                    self.emit_message(msgs.INPUT_EV_CONTEXT_PLAYER)


    def handle_INPUT_EV_UP(self):

        if (not self.is_active()): return
       
        if (self.__is_searching):
            idx = self.__browser.search(self.__search_term, -1)
            if (idx != -1):
                self.__browser.set_cursor(idx)
                self.__browser.scroll_to_item(idx)
            
        else:
            cursor = self.__browser.get_cursor()
            if (cursor == -1): cursor = 1
            if (cursor > 0):
                cursor -= 1
            self.__browser.set_cursor(cursor)

            f = self.__browser.get_item(cursor).get_file()
            self.emit_message(msgs.UI_ACT_TALK, f.acoustic_name or f.name)
            

    def handle_INPUT_EV_PAGE_UP(self):

        if (self.is_active()):        
            idx = self.__browser.get_index_at(0)
            if (idx != -1):
                new_idx = max(0, idx - 2)
                self.__browser.scroll_to_item(new_idx)


    def handle_INPUT_EV_DOWN(self):

        if (not self.is_active()): return
        
        if (self.__is_searching):
            idx = self.__browser.search(self.__search_term, 1)
            if (idx != -1):            
                self.__browser.set_cursor(idx)
                self.__browser.scroll_to_item(idx)
            
        else:
            cursor = self.__browser.get_cursor()
            if (cursor == -1): cursor = 0
            if (cursor + 1 < len(self.__browser.get_items())):
                cursor += 1
            self.__browser.set_cursor(cursor)            

            f = self.__browser.get_item(cursor).get_file()
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
    
        if (self.is_active() and self.__browser.is_visible()):
            self.select_tab(1)


    def handle_INPUT_EV_ENTER(self):
    
        if (self.is_active() and self.__browser.is_visible()):
            cursor = self.__browser.get_cursor()
            if (cursor != -1):
                self.__browser.trigger_item_button(cursor)

    
    def handle_INPUT_EV_GO_PARENT(self):
    
        if (self.is_active()):
            if (self.__browser.is_visible()):
                self.__browser.go_parent()

    def handle_INPUT_EV_SWITCH_TAB(self):
    
        if (self.is_active()):
            self.switch_tab()


    def handle_INPUT_EV_PLAY(self):
    
        if (self.is_active() and self.__media_widget):
            self.__media_widget.play_pause()


    def handle_INPUT_EV_FULLSCREEN(self):
    
        if (self.is_active()):
            self.__on_toggle_fullscreen()

    
    def handle_INPUT_EV_VOLUME_UP(self):
    
        if (self.is_active() and self.__media_widget):
            self.__media_widget.increment()


    def handle_INPUT_EV_VOLUME_DOWN(self):
    
        if (self.is_active() and self.__media_widget):
            self.__media_widget.decrement()


    def handle_INPUT_EV_PREVIOUS(self):
    
        if (self.is_active()):
            self.__go_previous()


    def handle_INPUT_EV_NEXT(self):
    
        if (self.is_active()):
            self.__go_next()


    def handle_INPUT_EV_REWIND(self):
    
        if (self.is_active() and self.__media_widget):
            self.__media_widget.rewind()
            
            
    def handle_INPUT_EV_FORWARD(self):
    
        if (self.is_active() and self.__media_widget):
            self.__media_widget.forward()

