from com import View, Configurator, msgs
from ui.itemview.ThumbableGridView import ThumbableGridView
from ui.Widget import Widget
from PrefsItem import PrefsItem


class Preferences(View):

    TITLE = "Settings"
    PRIORITY = 100
    

    def __init__(self):

        # list of configurators
        self.__configurators = []
        
        # current configurator
        self.__current_configurator = None
        
    
        View.__init__(self)
        
        self.__list = ThumbableGridView()
        self.add(self.__list)
        
        
    def render_this(self):
    
        w, h = self.get_size()
        self.__list.set_geometry(0, 0, w, h)
        
        if (self.__current_configurator):
            self.__current_configurator.is_visible()
            self.__current_configurator.set_geometry(0, 0, w, h)
        

    def __register_configurator(self, comp):
    
        comp.set_visible(False)
        self.add(comp)
        
        item = PrefsItem(comp)
        item.connect_clicked(self.__show_prefs, comp)
        self.__list.append_item(item)


    def __show_prefs(self, comp):
    
        self.__list.set_visible(False)
        comp.set_visible(True)
        self.__current_configurator = comp
        self.render()
        
        
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

