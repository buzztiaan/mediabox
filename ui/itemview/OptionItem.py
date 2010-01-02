from Item import Item
from theme import theme


class OptionItem(Item):

    EVENT_CHANGED = "event-changed"

    def __init__(self, *options):

        self.__names = []
        self.__values = []
        self.__current_choice = 0

        Item.__init__(self)
        self.set_options(*options)


    def connect_changed(self, cb, *args):
    
        self._connect(self.EVENT_CHANGED, cb, *args)
        

    def set_options(self, *options):
    
        self.__names = []
        self.__values = []
        for i in range(0, len(options), 2):
            name = options[i]
            value = options[i + 1]

            self.__names.append(name)
            self.__values.append(value)
        #end for
        
        self.select(0)

        
    def render_at(self, cnv, x, y):
    
        w, h = self.get_size()
    
        pmap, is_new = self._get_cached_pixmap()
        if (is_new):
            pmap.fill_area(0, 0, w, h, theme.color_mb_background)
            
            pmap.fit_pixbuf(theme.mb_choicebox_switch, w - 80, 20, 80, h - 40)

            pmap.set_clip_rect(0, 0, w, h)
            name = self.__names[self.__current_choice]
            pmap.draw_formatted_text(name, theme.font_mb_headline,
                                     4, 4, w - 96, h - 8,
                                     theme.color_list_item_text)
            pmap.set_clip_rect()
        #end if
        
        # copy to the given canvas
        cnv.copy_buffer(pmap, 0, 0, x, y, w, h)


    def select(self, idx):
    
        self.__current_choice = idx
        name = self.__names[idx]
        value = self.__values[idx]

        self._invalidate_cached_pixmap()
        self.emit_event(self.EVENT_CHANGED, value)
        
        
    def select_by_value(self, value):
    
        try:
            idx = self.__values.index(value)
            self.select(idx)
        except:
            pass


    def click_at(self, px, py):
    
        w, h = self.get_size()

        if (px > w - 80):
            self.__current_choice += 1
            self.__current_choice %= len(self.__values)
            self.select(self.__current_choice)
        #end if

