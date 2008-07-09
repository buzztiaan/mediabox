from com import Viewer, Configurator, msgs
from mediascanner.MediaItem import MediaItem
from PrefsThumbnail import PrefsThumbnail
import theme


class Preferences(Viewer):

    PRIORITY = 9999
    ICON = theme.viewer_prefs
    ICON_ACTIVE = theme.viewer_prefs_active
    

    def __init__(self):
    
        self.__current_configurator = None
        self.__configurators = []
        self.__items = []
    
        Viewer.__init__(self)
        
        
    def __register_configurator(self, comp):
    
        self.add(comp)    
        comp.set_geometry(0, 40, 620, 410)

        self.__configurators.append(comp)

        item = MediaItem()
        tn = PrefsThumbnail(comp.ICON, comp.TITLE)
        item.thumbnail_pmap = tn
        self.__items.append(item)
        
        self.set_collection(self.__items)


    def __load_item(self, item):
    
        idx = self.__items.index(item)
        configurator = self.__configurators[idx]
        
        self.set_title(configurator.TITLE)
    
        if (self.__current_configurator):
            self.__current_configurator.set_visible(False)
    
        configurator.set_visible(True)
        configurator.render()
        self.__current_configurator = configurator


    def handle_event(self, event, *args):
    
        if (event == msgs.COM_EV_COMPONENT_LOADED):
            comp = args[0]
            if (isinstance(comp, Configurator)):
                self.__register_configurator(comp)
            
        if (self.is_active()):
            if (event == msgs.CORE_ACT_LOAD_ITEM):
                item = args[0]
                self.__load_item(item)

