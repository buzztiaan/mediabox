from com import Component, Applet, msgs
from ui.Window import Window


class AppletService(Component, Window):
    """
    Service for launching applets.
    """

    def __init__(self):
    
        self.__applets = {}
        self.__current_applet = None
    
        Component.__init__(self)
        Window.__init__(self, False)
        self.set_size(800, 400)
        self.connect_closed(self.__on_close_window)
        
        
    def __on_close_window(self):
    
        self.set_visible(False)
        
        
    def render_this(self):
    
        w, h = self.get_size()
        
        if (self.__current_applet):
            self.__current_applet.set_geometry(0, 0, w, h)
        
        
    def handle_COM_EV_COMPONENT_LOADED(self, comp):
    
        if (isinstance(comp, Applet)):
            self.__applets[comp.get_applet_id()] = comp
            comp.set_visible(False)
            self.add(comp)


    def handle_CORE_SVC_LAUNCH_APPLET(self, applet_id):
    
        applet = self.__applets.get(applet_id)
        if (self.__current_applet):
            self.__current_applet.set_visible(False)

        if (applet):
            self.__current_applet = applet
            applet.set_visible(True)
            self.set_title(applet.TITLE)
            self.set_visible(True)
            self.render()

