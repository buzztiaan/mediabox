"""
Class for storing and retrieving configuration values via GConf.
"""


try:
    # GNOME
    import gconf
except:
    try:
        # Maemo    
        import gnome.gconf as gconf
    except:
        # last resort...
        from utils import gconftool as gconf
        
        
_CLIENT = gconf.client_get_default()
_PREFIX = "/apps/maemo-mediabox/"


class Config(object):
    """
    Class for storing and retrieving configuration values via GConf.
    
    Example::
      cfg = Config("my-plugin", [("foo", Config.STRING, "foobar"),
                                 ("bar", Config.INTEGER, 10)])
      cfg["foo"] = "Some string"
      print cfg["bar"]
      
    @since: 0.96
    """

    INTEGER = 0
    STRING = 1
    BOOL = 2
    INTEGER_LIST = 3
    STRING_LIST = 4
    
    
    def __init__(self, agent, schema):
        """
        Creates a new Config object for storing configuration of the given
        agent with the given schema. The agent name is used to avoid clashes
        when different plugins use keys of the same name. The agent name should
        usually be the name of your plugin.
        
        Schema is a list of tuples of the form
        C{(key_name, datatype, default_value)}
        describing the valid keys that can be stored.
        @since: 0.96
        
        @param agent: name of agent
        @param schema: list of schema tuples
        """
        
        if (agent):
            self.__prefix = _PREFIX + agent + "/"
        else:
            self.__prefix = _PREFIX
            
        self.__schema = schema
        
        
    def __lookup_schema(self, key):
        
        for k, t, d in self.__schema:
            if (k == key):
                return (t, d)
        #end for
        raise KeyError("no such key %s" % key)
        
        
    def __getitem__(self, key):
    
        return self.__get(key)
        
        
    def __setitem__(self, key, value):
    
        self.__set(key, value)
        

    def __get(self, key):
    
        dtype, default = self.__lookup_schema(key)
        
        if (dtype == self.STRING):
            return _CLIENT.get_string(self.__prefix + key) \
                   or default
        elif (dtype == self.STRING_LIST):
            l = _CLIENT.get_list(self.__prefix + key, gconf.VALUE_STRING) or []
            return l[:] or default[:]
        elif (dtype == self.INTEGER):
            try:
                have_key = _CLIENT.get_without_default(self.__prefix + key)
            except:
                have_key = False

            v = _CLIENT.get_int(self.__prefix + key)
            if (not have_key): v = default
            return v
        elif (dtype == self.INTEGER_LIST):                
            l = _CLIENT.get_list(self.__prefix + key, gconf.VALUE_INT) or []
            return l[:] or default[:]
        elif (dtype == self.BOOL):
            try:
                have_key = _CLIENT.get_without_default(self.__prefix + key)
            except:
                have_key = False

            v = _CLIENT.get_bool(self.__prefix + key)
            if (not have_key): v = default
            return v
        else:
            return None    
        
        
    def __set(self, key, value):
    
        dtype, default = self.__lookup_schema(key)
        
        if (dtype == self.STRING):
            _CLIENT.set_string(self.__prefix + key, value)
        elif (dtype == self.STRING_LIST):
            _CLIENT.set_list(self.__prefix + key, gconf.VALUE_STRING, value)
        elif (dtype == self.INTEGER):
            _CLIENT.set_int(self.__prefix + key, value)
        elif (dtype == self.INTEGER_LIST):
            _CLIENT.set_list(self.__prefix + key, gconf.VALUE_INT, value)
        elif (dtype == self.BOOL):
            _CLIENT.set_bool(self.__prefix + key, value)

