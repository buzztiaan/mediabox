from com import Configurator, msgs
from storage import Device, File
from theme import theme


class PrefsDevice(Device):

    CATEGORY = Device.CATEGORY_HIDDEN
    TYPE = Device.TYPE_GENERIC


    def __init__(self):
    
        self.__configurators = []
    
        Device.__init__(self)
        
        
    def get_prefix(self):
        
        return "preferences://"
        
        
    def get_name(self):
    
        return "Preferences"
        

    def get_icon(self):
    
        return theme.mb_viewer_prefs
        
        
    def get_root(self):
    
        f = File(self)
        f.name = self.get_name()
        f.info = "Preferences"
        f.path = "/"
        f.icon = self.get_icon().get_path()
        f.mimetype = f.DEVICE_ROOT
        f.folder_flags = f.ITEMS_COMPACT

        return f
        
        
    def get_file(self, path):
    
        applet_id = path.split("/")[-1]
        cs = [ c for c in self.__configurators
               if c.get_applet_id() == applet_id ]
        if (cs):
            c = cs[0]
            f = File(self)
            f.name = c.TITLE
            f.info = c.DESCRIPTION
            f.resource = c.get_applet_id()
            f.path = "/" + f.resource
            f.mimetype = "application/x-applet"
            f.icon = c.ICON.get_path()
        
        else:
            f = self.get_root()
        
        return f


    def get_contents(self, path, begin_at, end_at, cb, *args):

        self.__configurators.sort(lambda a,b: cmp(a.TITLE, b.TITLE))

        cnt = 0
        for c in self.__configurators:
            if (cnt < begin_at): continue
            if (end_at and cnt > end_at): break

            f = File(self)
            f.name = c.TITLE
            f.info = c.DESCRIPTION
            f.resource = c.get_applet_id()
            f.path = "/" + f.resource
            f.mimetype = "application/x-applet"
            f.icon = c.ICON.get_path()
            
            cb(f, *args)
            cnt += 1
        #end for
        
        cb(None, *args)


    def __on_put_on_dashboard(self, folder, f):
    
        f.bookmarked = True


    def get_file_actions(self, folder, f):
    
        actions = []
        actions.append((None, "Put on Dashboard", self.__on_put_on_dashboard))

        return actions


    def handle_COM_EV_COMPONENT_LOADED(self, comp):
    
        if (isinstance(comp, Configurator)):
            self.__configurators.append(comp)

