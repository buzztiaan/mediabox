from com import msgs
from utils import logging


class InputSchema(object):
    """
    Class for parsing and representing a input schemas. The input schema is
    a state machine.
    """
    
    
    def __init__(self, schema):
    
        # the current context
        self.__context = msgs.INPUT_EV_CONTEXT_BROWSER
        
        # the current event
        self.__event = None
        
        # table: (key, context) -> (event, context)
        self.__mapping = {}
        
        
        try:
            self.__parse_schema(schema)
        except:
            logging.error("syntax error in schema:\n%s\n%s",
                          schema, logging.stacktrace())

        
        
    def __parse_schema(self, schema):
    
        context = None
        for line in schema.splitlines():
            if (line.startswith("#") or not line.strip()):
                continue
                
            if (line[0] == "["):
                name = line.strip()[1:-1]
                context = getattr(msgs, "INPUT_EV_CONTEXT_" + name)
            else:
                parts = line.strip().split()
                name = parts[0]
                key = getattr(msgs, "HWKEY_EV_" + name)
                name = parts[1]
                if (name == "-"):
                    event = None
                else:
                    event = getattr(msgs, "INPUT_EV_" + name)
                name = parts[2]
                if (name == "-"):
                    new_context = None
                else:
                    new_context = getattr(msgs, "INPUT_EV_CONTEXT_" + name)
                    
                self.__mapping[(key, context)] = (event, new_context)
        #end for
        
        
    def send_key(self, key):
    
        #print key, self.__context
        if ((key, self.__context) in self.__mapping):
            self.__event, new_context = self.__mapping[(key, self.__context)]

        elif ((key, None) in self.__mapping):
            self.__event, new_context = self.__mapping[(key, None)]

        else:
            logging.warning("key [%s] undefined for the current input context",
                            msgs._id_to_name(key))
            self.__event = None
            new_context = None
        
        #print (self.__event, new_context)
        if (new_context):
            self.set_context(new_context)
        
        
        
    def get_context(self):
    
        return self.__context
        
        
    def set_context(self, context):
    
        self.__context = context
        if (logging.is_level(logging.DEBUG)):
            logging.debug("input context changed: %s",
                          msgs._id_to_name(context))

        
    def get_event(self):
    
        return self.__event

