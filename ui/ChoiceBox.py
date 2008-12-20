from Widget import Widget
from Pixmap import Pixmap, TEMPORARY_PIXMAP, pixmap_for_text
from theme import theme

import threading
import gobject
import gtk


class ChoiceBox(Widget):

    EVENT_CHANGED = "event-changed"
    

    def __init__(self, *choices):
    
        self.__names = []
        self.__values = []
        self.__current_choice = 0
        
        self.__label_pmap = None
    
        Widget.__init__(self)
        self.set_size(400, 64)
        self.connect_clicked(self.__on_click)
        
        self.set_choices(*choices)
        
        
    def __on_click(self):
    
        self.__current_choice += 1
        self.__current_choice %= len(self.__names)
        self.select(self.__current_choice)
        
        
    def connect_changed(self, cb, *args):
    
        self._connect(self.EVENT_CHANGED, cb, *args)
        
        
    def set_choices(self, *choices):
    
        self.__names = []
        self.__values = []
        for i in range(0, len(choices), 2):
            name = choices[i]
            value = choices[i + 1]

            self.__names.append(name)
            self.__values.append(value)
        #end for
        
        self.select(0)


    def select(self, idx):
    
        self.__current_choice = idx
        name = self.__names[idx]
        value = self.__values[idx]
        
        self.__label_pmap = pixmap_for_text(name, theme.font_mb_plain)
        w, h = self.__label_pmap.get_size()
        self.__label_pmap.fill_area(0, 0, w, h, "#ffffff")
        self.__label_pmap.draw_text(name, theme.font_mb_plain, 0, 0,
                                    theme.color_mb_listitem_subtext)
        if (self.may_render()):
            self.fx_slide_in()
            
        self.send_event(self.EVENT_CHANGED, value)
        
        
    def select_by_value(self, value):
    
        try:
            idx = self.__values.index(value)
            self.select(idx)
        except:
            pass
            
        
    def _reload(self):
    
        self.select(self.__current_choice)
        
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        self.use_clipping(True)
        screen.draw_frame(theme.mb_choicebox, x, y, w, h, True)
        #screen.fill_area(x, y, w - 64, h, "#000000")
        #screen.fill_area(x + 1, y + 1, w - 66, h - 2, "#ffffff")
        
        screen.draw_pixbuf(theme.mb_choicebox_switch, x + w - 64, y + 8)
        
        l_w, l_h = self.__label_pmap.get_size()
        x += 8
        w -= 64 + 16
        screen.draw_pixmap(self.__label_pmap,
                           x + max(0, (w - l_w) / 2),
                           y + (h - l_h) / 2)
        self.use_clipping(False)


    def fx_slide_in(self, wait = True):
    
        STEP = 12
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        #w -= 64
        x += 8
        y += 8
        w -= 64 + 16
        h -= 16
        screen = self.get_screen()

        l_w, l_h = self.__label_pmap.get_size()
        buf = TEMPORARY_PIXMAP
        buf.fill_area(0, 0, w, h, "#ffffff")
        buf.draw_pixmap(self.__label_pmap, max(0, (w - l_w) / 2), (h - l_h) / 2)
        finished = threading.Event()
        
        def fx(i):
            if (i + STEP > w): i = w - STEP
            self.use_clipping(True)
            screen.move_area(x + STEP, y, w - STEP, h, -STEP, 0)
            screen.copy_pixmap(buf, i, 0, x + w - STEP, y, STEP, h)
            self.use_clipping(False)
            if (i + STEP < w):
                gobject.timeout_add(7, fx, i + STEP)
            else:
                finished.set()

        self.set_events_blocked(True)
        fx(0)
        while (wait and not finished.isSet()): gtk.main_iteration(False)
        self.set_events_blocked(False)

