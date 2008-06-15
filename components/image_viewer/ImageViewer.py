from com import Viewer, events
from ui.KineticScroller import KineticScroller
from ui.Label import Label
from ui.ImageButton import ImageButton
from mediabox.ThrobberDialog import ThrobberDialog
from mediabox import viewmodes
from ImageThumbnail import ImageThumbnail
from Image import Image
from OverlayControls import OverlayControls
import theme

import gtk
import gobject
import os


_BACKGROUND_COLOR = "#ffffff"
_BACKGROUND_COLOR_FS = "#101010"


class ImageViewer(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_image
    ICON_ACTIVE = theme.viewer_image_active
    PRIORITY = 30


    def __init__(self):
            
        self.__is_fullscreen = False
            
        self.__uri = ""
        self.__items = []
        self.__current_item = -1
    
        Viewer.__init__(self)
        
        self.__layout = self.get_window()
        
        # image
        self.__image = Image()
        self.__image.add_observer(self.__on_observe_image)
        self.__image.set_geometry(15, 42, 584, 366)
        self.__image.set_background(_BACKGROUND_COLOR)
        self.add(self.__image)

        kscr = KineticScroller(self.__image)
        kscr.set_touch_area(0, 730)

        # not supported on maemo but nice to have elsewhere
        #kscr.connect("scroll-event", self.__on_mouse_wheel)

        self.__overlay_ctrls = OverlayControls()
        self.__overlay_ctrls.add_observer(self.__on_observe_overlay_ctrls)
        self.__image.add(self.__overlay_ctrls)
        self.__overlay_ctrls.set_visible(False)

        self.__throbber = ThrobberDialog()
        self.__throbber.set_throbber(theme.throbber)
        self.__throbber.set_text("Loading")
        self.add(self.__throbber)
        self.__throbber.set_visible(False)
        

        # toolbar
        self.__tbset = self.new_toolbar_set()
        for icon1, icon2, action in [
          (theme.btn_zoom_in_1, theme.btn_zoom_in_2, self.__zoom_in),
          (theme.btn_zoom_out_1, theme.btn_zoom_out_2, self.__zoom_out),
          (theme.btn_zoom_fit_1, theme.btn_zoom_fit_2, self.__zoom_fit),
          (theme.btn_zoom_100_1, theme.btn_zoom_100_2, self.__zoom_100),
          (theme.btn_previous_1, theme.btn_previous_2, self.__previous_image),
          (theme.btn_next_1, theme.btn_next_2, self.__next_image)]:
            btn = ImageButton(icon1, icon2)
            btn.connect_clicked(action)
            self.__tbset.add_widget(btn)
        self.set_toolbar_set(self.__tbset)            
            

    def render_this(self):
        
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        if (not self.__is_fullscreen):
            screen.draw_frame(theme.viewer_image_frame, x + 4, y + 30,
                              612, 397, False)


    def handle_event(self, event, *args):
               
        if (event == events.CORE_EV_MEDIA_SCANNING_FINISHED):
            mscanner = args[0]
            self.__update_media(mscanner)

        if (self.is_active()):
            if (event == events.CORE_ACT_LOAD_ITEM):
                item = args[0]
                self.__load(item)
        
            if (event == events.HWKEY_EV_INCREMENT):
                self.__zoom_in()
                
            elif (event == events.HWKEY_EV_DECREMENT):
                self.__zoom_out()
                
            elif (event == events.HWKEY_EV_ENTER):
                self.__next_image()
                
            elif (event == events.HWKEY_EV_FULLSCREEN):
                self.__on_fullscreen()
                
        #end if        


    def __on_mouse_wheel(self, src, ev):        
    
        if (ev.direction == gtk.gdk.SCROLL_UP):
            self.increment()
        elif (ev.direction == gtk.gdk.SCROLL_DOWN):
            self.decrement()


    def __on_observe_image(self, src, cmd, *args):
    
        if (cmd == src.OBS_BEGIN_LOADING):
            self.__throbber.set_visible(True)
            self.__throbber.render()            
            
        elif (cmd == src.OBS_END_LOADING):
            self.__throbber.set_visible(False)
            self.__image.render()
           
        elif (cmd == src.OBS_PROGRESS):        
            self.__throbber.rotate()


    def __on_observe_overlay_ctrls(self, src, cmd, *args):
    
        if (cmd == src.OBS_PREVIOUS):
            self.__previous_image()
            
        elif (cmd == src.OBS_NEXT):
            self.__next_image()
            
            
    def __get_name(self, uri):
    
        basename = os.path.basename(uri)
        name = os.path.splitext(basename)[0]
        name = name.replace("_", " ")
        
        return name
            
            
    def __previous_image(self):

        if (not self.__items): return
        
        idx = self.__current_item
        if (idx == -1): idx = 0
        idx -= 1
        if (idx == -1): idx = len(self.__items) - 1
        self.__image.slide_from_left()
        self.emit_event(events.CORE_ACT_SELECT_ITEM, idx)


    def __next_image(self):

        if (not self.__items): return
                    
        idx = self.__current_item       
        idx += 1
        idx %= len(self.__items)
        self.__image.slide_from_right()
        self.emit_event(events.CORE_ACT_SELECT_ITEM, idx)
            

    def clear_items(self):
    
        self.__items = []


    def __update_media(self, mscanner):
    
        self.__items = []
        self.__current_item = -1
        for item in mscanner.get_media(mscanner.MEDIA_IMAGE):
            if (not item.thumbnail_pmap):
                tn = ImageThumbnail(item.thumbnail)
                item.thumbnail_pmap = tn
            self.__items.append(item)
        #end for
        self.set_collection(self.__items)


    def __load(self, item):

        uri = item.uri
        self.__image.load(uri)        
        #self.__label.set_text(self.__get_name(uri))
        self.__current_item = self.__items.index(item)
        self.__image.slide_from_right()
        self.set_title(self.__get_name(uri))
        self.set_info("%d / %d" % (self.__current_item + 1, len(self.__items)))


       
    
    def __zoom_in(self):
    
        self.__image.zoom_in()


    def __zoom_out(self):
    
        self.__image.zoom_out()


    def __zoom_100(self):
    
        self.__image.zoom_100()


    def __zoom_fit(self):
    
        self.__image.zoom_fit()
     

    def __on_fullscreen(self):
        
        self.__is_fullscreen = not self.__is_fullscreen        
        
        if (self.__is_fullscreen):
            #self.__label.set_visible(False)
            self.emit_event(events.CORE_ACT_VIEW_MODE, viewmodes.FULLSCREEN)
            self.__overlay_ctrls.set_visible(True)
            self.__image.set_background(_BACKGROUND_COLOR_FS)
            self.__image.set_geometry(0, 0, 800, 480)
        else:
            #self.__label.set_visible(True)
            self.emit_event(events.CORE_ACT_VIEW_MODE, viewmodes.NORMAL)
            self.__overlay_ctrls.set_visible(False)
            self.__image.set_background(_BACKGROUND_COLOR)            
            self.__image.set_geometry(15, 42, 584, 366)
        
        self.emit_event(events.CORE_ACT_RENDER_ALL)            

