from com import Component, msgs


class DirectoryService(Component):
    """
    Service for looking up file objects by full path string.
    """
    
    def __init__(self):
    
        # table: prefix -> device
        self.__prefixes = {}
        # table: ID -> prefix
        self.__idents = {}
        
        Component.__init__(self)


    def handle_CORE_SVC_LIST_PATH(self, path):

        if (path.startswith("/")): path = "file://" + path
        
        idx = path.find("://")
        idx = path.find("/", idx + 3)
        prefix = path[:idx]
        path = path[idx:]
        #print "PREFIX", prefix, "PATH", path
        
        try:
            return self.__prefixes[prefix].ls(path)
        except:
            return []


    def handle_CORE_SVC_GET_FILE(self, path):
                
        #print "GET FILE", path
        if (path.startswith("/")): path = "file://" + path
                    
        idx = path.find("://")
        idx = path.find("/", idx + 3)
        prefix = path[:idx]
        path = path[idx:]
        #print "PREFIX", prefix, "PATH", path
        
        try:
            #print self.__prefixes, prefix, path
            return self.__prefixes[prefix].get_file(path)
        except:
            return 0


    def handle_CORE_EV_DEVICE_ADDED(self, ident, device):            
            
        self.__prefixes[device.get_prefix()] = device


    def handle_CORE_EV_DEVICE_REMOVED(self, ident):        

        try:
            prefix = self.__idents[ident]
            del self.__idents[ident]
            del self.__prefixes[prefix]
        except:
            pass

