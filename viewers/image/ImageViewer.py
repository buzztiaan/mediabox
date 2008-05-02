from viewers.Viewer import Viewer
from ui.KineticScroller import KineticScroller
from ui.Label import Label
from mediabox.ThrobberDialog import ThrobberDialog
from ImageThumbnail import ImageThumbnail
from Image import Image
from OverlayControls import OverlayControls
from mediabox import caps
import theme

import gtk
import gobject
import os


_BACKGROUND_COLOR = gtk.gdk.color_parse("#ffffff")
_BACKGROUND_COLOR_FS = gtk.gdk.color_parse("#101010")


class ImageViewer(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_image
    ICON_ACTIVE = theme.viewer_image_active
    CAPS = caps.ZOOMING | caps.SKIPPING
    PRIORITY = 30


    def __init__(self, esens):
            
        self.__is_fullscreen = False
            
        self.__uri = ""
        self.__items = []
        self.__current_item = -1
    
        Viewer.__init__(self, esens)
        
        self.__layout = esens
        
        # image
        self.__image = Image(esens)
        self.__image.add_observer(self.__on_observe_image)
        self.__image.set_geometry(15, 42, 584, 366)
        #self.__image.set_size(558, 340)
        self.__image.set_background(_BACKGROUND_COLOR)
        self.add(self.__image)

        kscr = KineticScroller(self.__image)
        kscr.set_touch_area(0, 730)

        # not supported on maemo but nice to have elsewhere
        #kscr.connect("scroll-event", self.__on_mouse_wheel)

        self.__overlay_ctrls = OverlayControls(esens)
        self.__overlay_ctrls.add_observer(self.__on_observe_overlay_ctrls)
        self.__image.add(self.__overlay_ctrls)
        self.__overlay_ctrls.set_visible(False)

        self.__throbber = ThrobberDialog(esens)
        self.__throbber.set_throbber(theme.throbber)
        self.__throbber.set_text("Loading")
        self.add(self.__throbber)
        self.__throbber.set_visible(False)
        
        #self.__label = Label(esens, "", theme.font_plain,
        #                                theme.color_fg_photo_label)
        #self.add(self.__label)
        #self.__label.set_alignment(self.__label.CENTERED)
        #self.__label.set_pos(20, 380)


    def render_this(self):
        
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        #self.__image.set_size(584, 336) #w - 20, h - 60)
        #self.__throbber.set_size(584, 336) #w - 20, h - 60)
        #self.__label.set_size(w - 60, 0)
        
        if (not self.__is_fullscreen):
            screen.draw_frame(theme.viewer_image_frame, x + 4, y + 30,
                              612, 397, False)
        

    def __on_mouse_wheel(self, src, ev):        
    
        if (ev.direction == gtk.gdk.SCROLL_UP):
            self.increment()
        elif (ev.direction == gtk.gdk.SCROLL_DOWN):
            self.decrement()


    def __on_observe_image(self, src, cmd, *args):
    
        if (cmd == src.OBS_BEGIN_LOADING):
            #self.update_observer(self.OBS_SHOW_MESSAGE, "Loading...")
            self.__throbber.set_visible(True)
            self.__throbber.render()            
            
        elif (cmd == src.OBS_END_LOADING):
            #self.update_observer(self.OBS_SHOW_PANEL)
            self.__throbber.set_visible(False)
            self.__image.render()
           
        elif (cmd == src.OBS_PROGRESS):        
            self.update_observer(self.OBS_SHOW_PROGRESS, *args)
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
        self.update_observer(self.OBS_SELECT_ITEM, idx)


    def __next_image(self):

        if (not self.__items): return
                    
        idx = self.__current_item       
        idx += 1
        idx %= len(self.__items)
        self.__image.slide_from_right()
        self.update_observer(self.OBS_SELECT_ITEM, idx)
            

    def clear_items(self):
    
        self.__items = []


    def update_media(self, mscanner):
    
        self.__items = []
        self.__current_item = -1
        for item in mscanner.get_media(mscanner.MEDIA_IMAGE):
            if (not item.thumbnail_pmap):
                tn = ImageThumbnail(item.thumbnail)
                item.thumbnail_pmap = tn
            self.__items.append(item)


    def load(self, item):

        uri = item.uri
        self.__image.load(uri)        
        #self.__label.set_text(self.__get_name(uri))
        self.__current_item = self.__items.index(item)
        self.__image.slide_from_right()
        self.update_observer(self.OBS_TITLE, self.__get_name(uri))
        self.update_observer(self.OBS_POSITION,
                             self.__current_item + 1, len(self.__items))


    def do_enter(self):
    
        self.__next_image()
        

    def do_increment(self):
    
        self.__image.zoom_in()
        
        
    def do_decrement(self):
    
        self.__image.zoom_out()

    
    def do_zoom_in(self):
    
        self.__image.zoom_in()


    def do_zoom_out(self):
    
        self.__image.zoom_out()


    def do_zoom_100(self):
    
        self.__image.zoom_100()


    def do_zoom_fit(self):
    
        self.__image.zoom_fit()


    def do_previous(self):
    
        self.__previous_image()


    def do_next(self):
    
        self.__next_image()


    def show(self):
    
        Viewer.show(self)
        self.update_observer(self.OBS_SET_COLLECTION, self.__items)
        

    def do_fullscreen(self):
        
        self.__is_fullscreen = not self.__is_fullscreen        
        
        if (self.__is_fullscreen):
            self.update_observer(self.OBS_FULLSCREEN)
            #self.__label.set_visible(False)
            self.__overlay_ctrls.set_visible(True)
            self.__image.set_background(_BACKGROUND_COLOR_FS)
            self.__image.set_geometry(0, 0, 800, 480)
        else:
            self.update_observer(self.OBS_UNFULLSCREEN)
            #self.__label.set_visible(True)
            self.__overlay_ctrls.set_visible(False)
            self.__image.set_background(_BACKGROUND_COLOR)            
            self.__image.set_geometry(15, 42, 584, 366)
            
        self.update_observer(self.OBS_RENDER)

