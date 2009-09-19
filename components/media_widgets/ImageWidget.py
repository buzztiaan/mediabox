from com import msgs
from mediabox.MediaWidget import MediaWidget
from ui.KineticScroller import KineticScroller
from ui.Label import Label
from ui.ImageButton import ImageButton
from ui.Image import Image as UIImage
from ui.Slider import Slider
from ui.layout import VBox
from mediabox import viewmodes
from Image import Image
from theme import theme

import gtk
import gobject
import os


_BACKGROUND_COLOR = theme.color_mb_image_background
_BACKGROUND_COLOR_FS = theme.color_mb_image_background_fullscreen

_MIN_ZOOM = 0.12
_MAX_ZOOM = 6.0

# amount by which the image must be dragged to get to the next or
# previous image
_DRAGGING_THRESHOLD = 60


# maximum slideshow timeout in seconds
_SLIDESHOW_MAX_TIMEOUT = 60


class ImageWidget(MediaWidget):

    def __init__(self):

        self.__is_fullscreen = False
        self.__click_pos = (0, 0)

        # the currently loaded file
        self.__current_file = None

        # whether the slideshow is playing
        self.__is_playing = False
        
        # slideshow handler
        self.__slideshow_handler = None

        # slideshow timeout in milliseconds
        self.__slideshow_timeout = 3000

        self.__scaling = 1.0

        self.__is_dragging = False
        self.__grab_point = 0
    
        MediaWidget.__init__(self)
              
        # image
        self.__image = Image()
        self.__image.add_observer(self.__on_observe_image)
        self.__image.set_background(_BACKGROUND_COLOR)
        #self.__image.connect_button_pressed(self.__on_image_clicked, True)
        #self.__image.connect_button_released(self.__on_image_clicked, False)

        self.__image.connect_button_pressed(self.__on_drag_start)
        self.__image.connect_button_released(self.__on_drag_stop)
        self.__image.connect_pointer_moved(self.__on_drag)
        self.add(self.__image)

        kscr = KineticScroller(self.__image)

        # controls
        ctrls = []
        self.__btn_slideshow = ImageButton(theme.mb_btn_play_1,
                                           theme.mb_btn_play_2)
        self.__btn_slideshow.connect_clicked(self.__toggle_slideshow)
        ctrls.append(self.__btn_slideshow)

        for icon1, icon2, action in [
          #(theme.mb_btn_zoom_out_1, theme.mb_btn_zoom_out_2, self.__zoom_out),
          (theme.mb_btn_zoom_fit_1, theme.mb_btn_zoom_fit_2, self.__zoom_fit),
          (theme.mb_btn_zoom_100_1, theme.mb_btn_zoom_100_2, self.__zoom_100)]:
          #(theme.mb_btn_zoom_in_1, theme.mb_btn_zoom_in_2, self.__zoom_in)]:
            btn = ImageButton(icon1, icon2)
            btn.connect_clicked(action)
            ctrls.append(btn)
        #end for            
            
        self.__btn_bookmark = ImageButton(theme.mb_btn_bookmark_1,
                                           theme.mb_btn_bookmark_2)
        self.__btn_bookmark.connect_clicked(self.__on_btn_bookmark)
        ctrls.append(self.__btn_bookmark)
            
            
        self._set_controls(*ctrls)

        # slideshow timer control
        self.__slideshow_timer_box = VBox()
        self.__slideshow_timer_box.set_spacing(12)

        self.__slideshow_timer_lbl = Label("",
                                           theme.font_mb_dialog_body,
                                           theme.color_mb_dialog_text)
        self.__slideshow_timer_box.add(self.__slideshow_timer_lbl, False)

        v = 2 / float(_SLIDESHOW_MAX_TIMEOUT)
        self.__slideshow_timer_slider = Slider(theme.mb_slider_gauge)
        self.__slideshow_timer_slider.set_mode(Slider.HORIZONTAL)
        self.__slideshow_timer_slider.set_value(v)
        self.__slideshow_timer_slider.set_size(600, 40)
        self.__on_change_slideshow_timer(v)
        self.__slideshow_timer_slider.connect_value_changed(
                                             self.__on_change_slideshow_timer)
        self.__slideshow_timer_box.add(self.__slideshow_timer_slider, False)


    def __on_change_slideshow_timer(self, v):
    
        secs = v * float(_SLIDESHOW_MAX_TIMEOUT - 1) + 1.0
        self.__slideshow_timer_lbl.set_text("Interval between slides:" \
                                            " %0.1f seconds" % secs)
        self.__slideshow_timeout = int(secs * 1000)


    def __on_btn_bookmark(self):
    
        self.call_service(msgs.BOOKMARK_SVC_ADD, self.__current_file)


    def render_this(self):
        
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        if (w < 800):
            screen.fill_area(x, y, w, h, theme.color_mb_background)
            screen.draw_frame(theme.mb_frame_image, x, y,
                              w, h, True)
            self.__image.set_geometry(11, 11, w - 28, h - 28)
            self.__image.set_background(_BACKGROUND_COLOR)
        else:
            self.__image.set_geometry(0, 0, w, h)
            self.__image.set_background(_BACKGROUND_COLOR_FS)


    def __on_observe_image(self, src, cmd, *args):
    
        if (cmd == src.OBS_BEGIN_LOADING):
            pass
                        
        elif (cmd == src.OBS_END_LOADING):
            self.__image.render()
           
        elif (cmd == src.OBS_PROGRESS):
            amount, total = args
            pass
            
        elif (cmd == src.OBS_ZOOMING):
            level, value = args
            value -= _MIN_ZOOM
            scale = value / float(_MAX_ZOOM - _MIN_ZOOM)
            scale = max(0.0, min(1.0, scale))
            self.__scaling = scale
            self.send_event(self.EVENT_MEDIA_SCALE, scale)


    def __on_drag_start(self, px, py):

        if (self.__image.is_image_fitting()):
            self.__is_dragging = True
            self.__grab_point = px
        
        
    def __on_drag_stop(self, px, py):
    
        if (self.__is_dragging):
            self.__is_dragging = False
            self.__image.set_drag_amount(0)


    def __on_drag(self, px, py):
    
        if (self.__is_dragging):
            dx = px - self.__grab_point
            self.__image.set_drag_amount(dx)
            
            if (dx < -_DRAGGING_THRESHOLD):
                self.__is_dragging = False
                self.__image.slide_from_right()
                self.send_event(self.EVENT_MEDIA_NEXT)
                
            elif (dx > _DRAGGING_THRESHOLD):
                self.__is_dragging = False
                self.__image.slide_from_left()
                self.send_event(self.EVENT_MEDIA_PREVIOUS)


    def __on_image_clicked(self, px, py, is_pressed):
    
        if (is_pressed):
            self.__click_pos = (px, py)
        else:
            cx, cy = self.__click_pos
            dx = abs(cx - px)
            dy = abs(cy - py)
            if (dx < 30 and dy < 30):
                w, h = self.__image.get_size()
                if (px < 80):
                    #self.__image.slide_from_left()
                    self.send_event(self.EVENT_MEDIA_PREVIOUS)
                elif (px > w - 80):
                    #self.__image.slide_from_right()
                    self.send_event(self.EVENT_MEDIA_NEXT)


    def __on_observe_overlay_ctrls(self, src, cmd, *args):
    
        if (cmd == src.OBS_PREVIOUS):
            self.__previous_image()
            
        elif (cmd == src.OBS_NEXT):
            self.__next_image()


    def load(self, item, direction = MediaWidget.DIRECTION_NEXT):

        #uri = item.get_resource()
        
        if (direction == self.DIRECTION_PREVIOUS):
            self.__image.slide_from_left()
        else:
            self.__image.slide_from_right()
        self.__image.load(item)
        self.__current_file = item
        #self.__label.set_text(self.__get_name(uri))
        #self.__current_item = self.__items.index(item)
        #self.set_title(self.__get_name(uri))
        #self.set_info("%d / %d" % (self.__current_item + 1, len(self.__items)))

        #gobject.timeout_add(3000, self.send_event, self.EVENT_MEDIA_EOF)


    def preload(self, item):
    
        self.__image.preload(item)


    def increment(self):
        

        self.__zoom_in()
        
        
    def decrement(self):
        
        self.__zoom_out()
       
       
    def set_scaling(self, v):
    
        zoom = _MIN_ZOOM + (_MAX_ZOOM - _MIN_ZOOM) * v
        
        self.__image.zoom(0, zoom)


    def play_pause(self):
    
        self.__toggle_slideshow()


    def stop(self):
    
        if (self.__is_playing):
            self.__toggle_slideshow()
       
    
    def __zoom_in(self):
    
        self.set_scaling(min(1.0, self.__scaling + 0.05))


    def __zoom_out(self):
    
        self.set_scaling(max(0.0, self.__scaling - 0.05))


    def __zoom_100(self):
    
        self.__image.zoom_100()


    def __zoom_fit(self):
    
        self.__image.zoom_fit()


    def __toggle_slideshow(self):
    
        self.__is_playing = not self.__is_playing
        if (self.__is_playing):        
            self.__btn_slideshow.set_images(theme.mb_btn_pause_1,
                                            theme.mb_btn_pause_2)

            self.call_service(msgs.DIALOG_SVC_CUSTOM, theme.mb_viewer_image,
                              "Slideshow",
                              self.__slideshow_timer_box)

            self.emit_message(msgs.MEDIA_EV_PLAY)

            if (self.__slideshow_handler):
                gobject.source_remove(self.__slideshow_handler)
            self.__slideshow_handler = gobject.timeout_add(
                                                      self.__slideshow_timeout,
                                                      self.__slideshow_timer)

        else:
            self.__btn_slideshow.set_images(theme.mb_btn_play_1,
                                            theme.mb_btn_play_2)


    def __slideshow_timer(self):
    
        gtk.main_iteration(False)
        
        if (self.__is_playing and self.may_render()):
            self.__image.slide_from_right()
            self.send_event(self.EVENT_MEDIA_NEXT)
            return True
            
        else:
            self.__btn_slideshow.set_images(theme.mb_btn_play_1,
                                            theme.mb_btn_play_2)
            self.__slideshow_handler = None
            self.__is_playing = False
            self.emit_message(msgs.MEDIA_EV_PAUSE)

            return False

