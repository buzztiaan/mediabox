from com import Component, msgs
import vkblayout
import layouts
import ui
from ui.Pixmap import Pixmap, text_extents
from theme import theme
from utils.Observable import Observable
from utils import maemo

try:
    # GNOME
    import gconf
except:
    try:
        # Maemo    
        import gnome.gconf as gconf
    except:
        # last resort...
        from utils import gconftool as gconf


import gtk
import gobject
import time
import threading



_MOD_NONE = 0
_MOD_SHIFT = 1
_MOD_ALT = 2


def _is_slide_open():
    """
    Returns whether the keyboard slide is open on the N810.
    """
    
    client = gconf.client_get_default()
    slide_open = client.get_bool("/system/osso/af/slide-open")
    return slide_open


class VirtualKeyboard(gtk.Window, Component):  

    def __init__(self):
    
        self.__is_showing = False
        self.__invalidated = True
    
        # current keyboard layout
        self.__current_layout = layouts.get_default_layout()
    
        self.__keys = []
        
        # cache for key pixmaps: (w, h): (pixmap1, pixmap2)
        self.__key_cache = {}
        
        self.__current_key = 0
        self.__key_release_time = 0
        self.__key_motion_timer = None
        self.__is_button_pressed = False

        self.__modifier = _MOD_NONE
        
        self.__size = (800, 150)
        self.__parent = None
    
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        Component.__init__(self)
        self.set_size_request(800, 150)
        self.connect("expose-event", self.__on_expose)
        self.set_app_paintable(True)

        if (not maemo.IS_MAEMO):
            # try to switch on compositing
            ui.try_rgba(self)

        self.set_events(gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.BUTTON_RELEASE_MASK |
                        gtk.gdk.POINTER_MOTION_MASK |
                        gtk.gdk.POINTER_MOTION_HINT_MASK)
        self.move(0, 1000)
        self.show()
        self.__screen = Pixmap(self.window)
        self.__clear_keyboard()

        self.hide()
        #self.__render_keyboard(self.__current_layout)
        
        self.connect("button-press-event", self.__on_press)
        self.connect("button-release-event", self.__on_release)
        #self.connect("motion-notify-event", self.__on_motion)


    def __clear_keyboard(self):
    
        w, h = self.__size
        self.__screen.fill_area(0, 0, w, h, theme.color_mb_vkb_background)
        self.__screen.draw_line(0, 0, w, 0, "#000000")



    def __render_keyboard(self, layout):
    
        w, h = self.__size
        offx = 3
        offy = 3
        w -= 6
        h -= 6
        cnt = 0
        self.__keys = []

        for block in layout.get_blocks():
            if (block.get_rows()):
                row_height = h / len(block.get_rows())
            else:
                row_height = h
            block_width = int(w * block.get_size())
            y = offy
            for row in block.get_rows():
                row_length = len(row.get_keys())
                key_width = block_width / row_length
            
                x = offx
                for key in row.get_keys():
                    self.__keys.append((x, y, key_width, row_height, key))
                    self.__render_key(cnt, False)
                    x += key_width
                    cnt += 1
                #end for
                y += row_height
            #end for
            offx += block_width
        #end for
    

    def __on_expose(self, src, ev):
    
        x, y, w, h = ev.area
        self.__screen.restore(x, y, w, h)
        
        
    def __popup(self, parent):
    
        self.__parent = parent
        w, h = self.__size
        px, py = parent.get_pos()
        pw, ph = parent.get_size()
        #self.move(px, py + ph)
        self.move(px, py + ph - h)
        self.show()
        #self.fx_slide(px, py + ph, py + ph - h)


    
    def __render_key(self, key, is_pressed):

        x, y, w, h, k = self.__keys[key]
        keychar = self.__get_key_char(k)
            
        key_pmap1, key_pmap2 = self.__key_cache.get((w, h), (None, None))

        if (not key_pmap1):
            key_pmap1 = Pixmap(None, w, h)
            key_pmap2 = Pixmap(None, w, h)
            key_pmap1.fill_area(0, 0, w, h, theme.color_mb_vkb_background)
            key_pmap2.fill_area(0, 0, w, h, theme.color_mb_vkb_background)
            #key_pmap1.copy_pixmap(self.__screen, x, y, w, h, 0, 0)
            #key_pmap2.copy_pixmap(self.__screen, x, y, w, h, 0, 0)
            key_pmap1.draw_frame(theme.mb_vkb_key_1, 0, 0, w, h, True)
            key_pmap2.draw_frame(theme.mb_vkb_key_2, 0, 0, w, h, True)
            self.__key_cache[(w, h)] = (key_pmap1, key_pmap2)
        #end if            

        if (is_pressed):
            self.__screen.draw_pixmap(key_pmap2, x, y)
        else:
            self.__screen.draw_pixmap(key_pmap1, x, y)

        if (k == vkblayout.LAYOUT):
            self.__screen.draw_pixbuf(theme.mb_vkb_layout,
                                      x + (w - 32) / 2, y + (h - 32) / 2)
        elif (k == vkblayout.BACKSPACE):
            self.__screen.draw_pixbuf(theme.mb_vkb_backspace,
                                      x + (w - 32) / 2, y + (h - 32) / 2)
        elif (k == vkblayout.SHIFT):
            self.__screen.draw_pixbuf(theme.mb_vkb_shift,
                                      x + (w - 32) / 2, y + (h - 32) / 2)
        elif (k == vkblayout.HIDE):
            self.__screen.draw_pixbuf(theme.mb_vkb_hide,
                                      x + (w - 32) / 2, y + (h - 32) / 2)
        else:
            tw, th = text_extents(keychar, theme.font_mb_vkb)
            self.__screen.draw_text(keychar, theme.font_mb_vkb,
                                    x + (w - tw) / 2, y + (h - th) / 2,
                                    theme.color_mb_vkb_text)

        
        
    def __find_key(self, px, py):

        cnt = 0    
        for x, y, w, h, k in self.__keys:            
            if (x <= px <= x + w and y <= py <= y + h):
                return cnt
            else:
                cnt += 1
        #end for
        
        return -1
        
        
    def __get_key_char(self, key):
    
        if (self.__modifier == _MOD_NONE):
            return key.get_char()
        elif (self.__modifier == _MOD_SHIFT):
            return key.get_shifted_char()
        elif (self.__modifier == _MOD_ALT):
            return key.get_alt_char()


    def __handle_key(self, key):
    
        kx, ky, kw, kh, k = self.__keys[key]
        keychar = self.__get_key_char(k)
        new_layout = k.get_layout()
        
        if (new_layout):
            self.__current_layout = new_layout
            self.__clear_keyboard()
            self.__render_keyboard(new_layout)
        
        elif (k == vkblayout.HIDE):
            w, h = self.__size
            px, py = self.__parent.get_pos()
            pw, ph = self.__parent.get_size()
        
            #self.fx_slide(px, py + ph - h, py + ph)
            self.__parent = None
            self.__is_showing = False
            self.hide()
            
        elif (k == vkblayout.LAYOUT):
            selector_layout = layouts.get_selector_layout()
            self.__clear_keyboard()
            self.__render_keyboard(selector_layout)
            
        elif (k == vkblayout.BACKSPACE):
            #self.emit_event(msgs.HWKEY_EV_BACKSPACE)
            self.__parent.send_event(self.__parent.EVENT_KEY_PRESS, "BackSpace")

        elif (k == vkblayout.SHIFT):
            if (self.__modifier == _MOD_SHIFT):
                self.__modifier = _MOD_NONE
            else:
                self.__modifier = _MOD_SHIFT
            self.__render_keyboard(self.__current_layout)
            
        elif (k == vkblayout.ALT):
            if (self.__modifier == _MOD_ALT):
                self.__modifier = _MOD_NONE
            else:
                self.__modifier = _MOD_ALT
            self.__render_keyboard(self.__current_layout)

        else:
            #self.emit_message(msgs.HWKEY_EV_KEY, keychar)
            self.__parent.send_event(self.__parent.EVENT_KEY_PRESS, keychar)


    def __on_press(self, src, ev):

        px, py = src.get_pointer()
        key = self.__find_key(px, py)
        self.__current_key = key
        self.__is_button_pressed = True
        self.__render_key(key, True)

        if (self.__key_motion_timer):
            gobject.source_remove(self.__key_motion_timer)
            self.__key_motion_timer = None
            
        
        
    def __on_release(self, src, ev):

        px, py = src.get_pointer()
        key = self.__current_key
        key2 = self.__find_key(px, py)
        self.__is_button_pressed = False
        self.__render_key(key, False)
        self.__current_key = -1

        if (self.__key_motion_timer):
            gobject.source_remove(self.__key_motion_timer)
            self.__key_motion_timer = None

        if (time.time() > self.__key_release_time + 0.1):        
            if (key != -1 and key == key2):            
                self.__handle_key(key)

            self.__key_release_time = time.time()
        #end if
        
        
        
    def __check_key_motion(self, key, x, y):
    
        px, py = self.get_pointer()
        if (abs(px - x) < 10 and abs(py - y) < 10):
            self.__render_key(key, True)
            self.__handle_key(key)
            gobject.timeout_add(250, self.__render_key, key, False)
        #end if
        self.__key_motion_timer = None
        
        
    def __on_motion(self, src, ev):

        if (self.__is_button_pressed):
            px, py = src.get_pointer()
            key = self.__find_key(px, py)

            if (self.__key_motion_timer):
                gobject.source_remove(self.__key_motion_timer)
                self.__key_motion_timer = None
            
            if (key != self.__current_key):
                if (self.__current_key != -1):
                    self.__render_key(self.__current_key, False)
                    self.__handle_key(self.__current_key)                    
                self.__current_key = -1
                self.__key_motion_timer = gobject.timeout_add(100,
                                                self.__check_key_motion, key, px, py)
        #end if


    def handle_VKB_ACT_SHOW(self, parent):

        # don't show virtual keyboard if the hw keyboard slide is open
        if (_is_slide_open()): return
    
        if (self.__invalidated):
            self.__key_cache.clear()
            self.__clear_keyboard()
            self.__render_keyboard(self.__current_layout)
            self.__invalidated = False
        self.__is_showing = True
        self.__popup(parent)


    def handle_CORE_EV_THEME_CHANGED(self):            

        self.__invalidated = True


    def fx_slide(self, x, from_y, to_y, wait = True):
    
        def fx(from_y, to_y):
        
            dy = (to_y - from_y) / 5
            if (abs(dy) > 0):
                self.move(x, from_y + dy)
                gobject.timeout_add(10, fx, from_y + dy, to_y)
            else:
                self.move(x, to_y)
                finished.set()
            
            
        finished = threading.Event()
        fx(from_y, to_y)
        while (wait and not finished.isSet()):
            while (gtk.events_pending()): gtk.main_iteration(False)

