from mediabox.MediaWidget import MediaWidget
from ui.KineticScroller import KineticScroller
from ui.Label import Label
from ui.ImageButton import ImageButton
from mediabox.ThrobberDialog import ThrobberDialog
from mediabox import viewmodes
from Image import Image
from OverlayControls import OverlayControls
import theme

import gtk
import gobject
import os


_BACKGROUND_COLOR = "#ffffff"
_BACKGROUND_COLOR_FS = "#101010"


class ImageWidget(MediaWidget):

    def __init__(self):
            
        self.__is_fullscreen = False
            
        self.__uri = ""
    
        MediaWidget.__init__(self)
        
        self.__layout = self.get_window()
        
        # image
        self.__image = Image()
        self.__image.add_observer(self.__on_observe_image)
        self.__image.set_background(_BACKGROUND_COLOR)
        self.add(self.__image)

        kscr = KineticScroller(self.__image)
        kscr.set_touch_area(0, 730)

        self.__overlay_ctrls = OverlayControls()
        self.__overlay_ctrls.add_observer(self.__on_observe_overlay_ctrls)
        self.__image.add(self.__overlay_ctrls)
        self.__overlay_ctrls.set_visible(False)

        self.__throbber = ThrobberDialog()
        self.__throbber.set_throbber(theme.throbber)
        self.__throbber.set_text("Loading")
        self.add(self.__throbber)
        self.__throbber.set_visible(False)
        

        # controls
        ctrls = []
        for icon1, icon2, action in [
          (theme.btn_zoom_in_1, theme.btn_zoom_in_2, self.__zoom_in),
          (theme.btn_zoom_out_1, theme.btn_zoom_out_2, self.__zoom_out),
          (theme.btn_zoom_fit_1, theme.btn_zoom_fit_2, self.__zoom_fit),
          (theme.btn_zoom_100_1, theme.btn_zoom_100_2, self.__zoom_100)]:
            btn = ImageButton(icon1, icon2)
            btn.connect_clicked(action)
            ctrls.append(btn)
            
        self._set_controls(*ctrls)


    def render_this(self):
        
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        if (w < 800):
            screen.draw_frame(theme.viewer_image_frame, x, y,
                              w, h, False)
            self.__image.set_geometry(11, 11, w - 28, h - 28)
            self.__image.set_background(_BACKGROUND_COLOR)
        else:
            self.__image.set_geometry(0, 0, w, h)
            self.__image.set_background(_BACKGROUND_COLOR_FS)


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
            


    def load(self, item):

        #uri = item.get_resource()
        
        self.__image.load(item)
        #self.__label.set_text(self.__get_name(uri))
        #self.__current_item = self.__items.index(item)
        self.__image.slide_from_right()
        #self.set_title(self.__get_name(uri))
        #self.set_info("%d / %d" % (self.__current_item + 1, len(self.__items)))

        gobject.timeout_add(3000, self.send_event, self.EVENT_MEDIA_EOF)



    def increment(self):
        
        self.__zoom_in()
        
        
    def decrement(self):
        
        self.__image.zoom_out()
       
    
    def __zoom_in(self):
    
        self.__image.zoom_in()


    def __zoom_out(self):
    
        self.__image.zoom_out()


    def __zoom_100(self):
    
        self.__image.zoom_100()


    def __zoom_fit(self):
    
        self.__image.zoom_fit()

