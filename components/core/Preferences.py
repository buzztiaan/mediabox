from com import Viewer, Configurator, msgs
from PrefsThumbnail import PrefsThumbnail
from mediabox import viewmodes
from theme import theme


class Preferences(Viewer):

    PRIORITY = 9999
    ICON = theme.mb_viewer_prefs
    

    def __init__(self):
    
        self.__current_configurator = None
        self.__configurators = []
        self.__thumbnails = []        
    
        Viewer.__init__(self)
        
        
    def render_this(self):
    
        w, h = self.get_size()
        for c in self.__configurators:
            c.set_size(w, h)
        
        
    def __register_configurator(self, comp):
    
        self.add(comp)    
        comp.set_visible(False)
        comp.set_geometry(0, 0, 610, 370)

        self.__configurators.append(comp)

        tn = PrefsThumbnail(comp.ICON, comp.TITLE)
        self.__thumbnails.append(tn)
        self.set_strip(self.__thumbnails)
        


    def __show_configurator(self, configurator):
        
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
            if (event == msgs.INPUT_ACT_REPORT_CONTEXT):
                self.emit_event(msgs.INPUT_EV_CONTEXT_BROWSER)

            elif (event == msgs.CORE_ACT_LOAD_ITEM):
                idx = args[0]
                configurator = self.__configurators[idx]
                self.__show_configurator(configurator)


    def show(self):
    
        Viewer.show(self)
        self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NORMAL)
        self.emit_event(msgs.INPUT_EV_CONTEXT_BROWSER)

        if (not self.__current_configurator):
            self.select_strip_item(0)

