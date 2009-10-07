from com import View, Configurator, msgs
from ui.itemview.ThumbableGridView import ThumbableGridView
from ui.Toolbar import Toolbar
from ui.ImageButton import ImageButton
from ui.Pixmap import Pixmap
from PrefsItem import PrefsItem
from theme import theme


class Preferences(View):

    TITLE = "Settings"
    PRIORITY = 100
    

    def __init__(self):

        # list of configurators
        self.__configurators = []
        
        # current configurator
        self.__current_configurator = None
        
    
        View.__init__(self)
        self.set_title("Settings")
        
        self.__list = ThumbableGridView()
        self.__list.set_background(theme.color_mb_background)
        self.__list.set_items_per_row(3)
        self.add(self.__list)
        
        self.__toolbar = Toolbar()
        self.add(self.__toolbar)
        
        self.__btn_back = ImageButton(theme.mb_btn_dir_up_1,
                                      theme.mb_btn_dir_up_2)
        self.__btn_back.connect_clicked(self.__on_btn_back)


    def __on_btn_back(self):
    
        self.__hide_prefs()

        
    def render_this(self):
    
        w, h = self.get_size()
       
        if (w < h):
            # portrait mode
            self.__list.set_geometry(0, 0, w, h - 70)
        
            if (self.__current_configurator):
                self.__current_configurator.set_geometry(0, 0, w, h - 70)
            
            self.__toolbar.set_geometry(0, h - 70, w, 70)
    
        else:
            # landscape mode
            self.__list.set_geometry(0, 0, w - 70, h)
        
            if (self.__current_configurator):
                self.__current_configurator.set_geometry(0, 0, w - 70, h)
            
            self.__toolbar.set_geometry(w - 70, 0, 70, h)
        

    def __register_configurator(self, comp):
    
        comp.set_visible(False)
        self.add(comp)
        
        item = PrefsItem(comp)
        item.connect_clicked(self.__show_prefs, comp)
        self.__list.append_item(item)


    def __show_prefs(self, comp):
    
        self.__toolbar.set_toolbar(self.__btn_back)
        self.__list.set_visible(False)
        comp.set_visible(True)
        self.__current_configurator = comp
        
        w, h = self.get_size()
        buf = Pixmap(None, w, h)
        self.render_at(buf)
        self.fx_slide_horizontal(buf, 0, 0, w, h, self.SLIDE_LEFT)
        del buf
        
        
    def __hide_prefs(self):
    
        self.__toolbar.set_toolbar()
        self.__list.set_visible(True)
        self.__current_configurator.set_visible(False)
        self.__current_configurator = None

        w, h = self.get_size()
        buf = Pixmap(None, w, h)
        self.render_at(buf)
        self.fx_slide_horizontal(buf, 0, 0, w, h, self.SLIDE_RIGHT)
        del buf



    def handle_COM_EV_COMPONENT_LOADED(self, comp):
    
        if (isinstance(comp, Configurator)):
            self.__configurators.append(comp)


    def handle_CORE_EV_APP_STARTED(self):

        def comparator(a, b):
            return cmp(a.TITLE, b.TITLE)

        self.__configurators.sort(comparator)
        while self.__configurators:
            self.__register_configurator(self.__configurators.pop(0))
        self.render()

