from com import Configurator, msgs
from ui.itemview import ThumbableGridView
from ComponentListItem import ComponentListItem
from theme import theme


class PrefsComponents(Configurator):
    """
    Configurator for listing the currently loaded components.
    """

    ICON = theme.prefs_icon_system
    TITLE = "Components Info"
    DESCRIPTION = "View the loaded components"


    def __init__(self):
    
        self.__components = []
    
        Configurator.__init__(self)

        self.__list = ThumbableGridView()
        self.add(self.__list)


    def __on_item_clicked(self, item):

        comp = item.get_component()
        self.__show_com_interface(comp)


    def __show_com_interface(self, comp):

        iface = ""
        handlers = [ m for m in dir(comp)
                     if m.startswith("handle_") and not m == "handle_message" ]
        handlers.sort()
        
        for h in handlers:
            msg_name = h[7:]
            iface += msg_name + "\n"
        #end for
        
        if (not iface):
            iface = "- no public interface -"
        
        self.call_service(msgs.UI_ACT_SHOW_INFO,
                          iface.strip())


    def render_this(self):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        self.__list.set_geometry(0, 0, w, h)
        screen.fill_area(x, y, w, h, theme.color_mb_background)


    def __update_list(self):
    
        self.__list.clear_items()
        self.__components.sort(lambda a,b:cmp(a.__class__.__module__,
                                              b.__class__.__module__))
        for comp in self.__components:
            item = ComponentListItem(comp)
            item.connect_clicked(self.__on_item_clicked, item)
            self.__list.append_item(item)
        #end for

        
    def handle_COM_EV_COMPONENT_LOADED(self, comp):
    
        self.__components.append(comp)
      
        
    def handle_CORE_EV_APP_STARTED(self):
    
        self.__update_list()

