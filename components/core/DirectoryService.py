from com import Component, msgs


class DirectoryService(Component):
    """
    Service component for browsing storage devices.
    The DirectoryService provides a means for accessing devices by using
    path strings.
    """
    
    def __init__(self):
    
        # table: prefix -> device
        self.__prefixes = {}
        # table: ID -> prefix
        self.__idents = {}
        
        Component.__init__(self)
        
        
        
    def handle_message(self, ev, *args):
    
        if (ev == msgs.CORE_SVC_LIST_PATH):
            path = args[0]
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
            
        elif (ev == msgs.CORE_SVC_GET_FILE):
            path = args[0]
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

            
            
        elif (ev == msgs.CORE_EV_DEVICE_ADDED):
            ident, device = args
            self.__prefixes[device.get_prefix()] = device
        
        elif (ev == msgs.CORE_EV_DEVICE_REMOVED):
            ident = args[0]
            try:
                prefix = self.__idents[ident]
                del self.__idents[ident]
                del self.__prefixes[prefix]
            except:
                pass
                
