from com import Configurator, msgs
from storage import Device, File
from theme import theme


class PrefsDevice(Device):
    """
    Storage device for browsing the configurators.
    """

    CATEGORY = Device.CATEGORY_CORE
    TYPE = Device.TYPE_SYSTEM


    def __init__(self):
    
        self.__cache = []
    
        self.__configurators = []
    
        Device.__init__(self)
        
        
    def get_prefix(self):
        
        return "preferences://"
        
        
    def get_name(self):
    
        return "Settings"
        

    def get_icon(self):
    
        return theme.mb_folder_prefs
     
     
    def __make_configurator(self, c):

        f = File(self)
        f.name = c.TITLE
        f.info = c.DESCRIPTION
        f.resource = `c`
        f.path = "/" + f.resource
        f.mimetype = f.CONFIGURATOR
        f.icon = c.ICON.get_path()
        
        return f
        
        
    def get_file(self, path):

        parts = [ p for p in path.split("/") if p ]
        len_parts = len(parts)
        
        f = None
        if (len_parts == 0):
            f = File(self)
            f.name = self.get_name()
            f.info = "Change the configuration"
            f.path = "/"
            f.icon = self.get_icon().get_path()
            f.mimetype = f.DEVICE_ROOT
            f.folder_flags = f.ITEMS_COMPACT

        elif (len_parts == 1):
            cfg_name = parts[-1]
            cs = [ c for c in self.__configurators
                   if `c` == cfg_name ]
            if (cs):
                c = cs[0]
                f = self.__make_configurator(c)
            #end if
        #end if
        
        return f


    def get_contents(self, path, begin_at, end_at, cb, *args):

        self.__configurators.sort(lambda a,b: cmp(a.TITLE, b.TITLE))

        if (self.__cache):
            items = self.__cache
        else:
            items = []
            for c in self.__configurators:
                f = self.__make_configurator(c)
                if (f): items.append(f)
            #end for
            self.__cache = items
        #end if

        items.sort()
        
        cnt = -1
        for item in items:
            cnt += 1
            if (cnt < begin_at): continue
            if (end_at and cnt > end_at): break
            cb(item, *args)
        #end for
        cb(None, *args)
 

    def __on_put_on_shelf(self, folder, f):
    
        f.bookmarked = True


    def get_file_actions(self, folder, f):
    
        actions = []
        actions.append((None, "Put on Shelf", self.__on_put_on_shelf))

        return actions


    def handle_COM_EV_COMPONENT_LOADED(self, comp):
    
        if (isinstance(comp, Configurator)):
            self.__configurators.append(comp)
            self.__cache = []

