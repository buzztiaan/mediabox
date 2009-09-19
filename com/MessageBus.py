"""
B{Used internally.}
"""

from exc import *
import msgs
from utils import logging


class _MessageBus(object):
    """
    Application message bus singleton. This class is intented to be used by
    the Mediator class only.
    """

    def __init__(self):
    
        self.__mediators = []
        self.__handlers = []


    def add_mediator(self, mediator):
    
        self.__mediators.append(mediator)
        self.__inspect_mediator(mediator)


    def __inspect_mediator(self, mediator):
    
        supported_events = [ ev[7:] for ev in dir(mediator)
                             if ev.startswith("handle_") ]
        for ev in supported_events:
            ev_id = msgs._name_to_id(ev)

            if (ev_id != -1):
                while (len(self.__handlers) <= ev_id):
                    self.__handlers.append([])

                handler = getattr(mediator, "handle_" + ev)
                self.__handlers[ev_id].append(handler)
            #end if
        #end for
        
        
    def send_event(self, src, event, *args):
    
        if (logging.is_level(logging.DEBUG)):
            logging.debug("*** %s%s ***", msgs._id_to_name(event), `args`[:30])
        
        try:
            handlers = self.__handlers[event]
        except:
            handlers = []
            
        for handler in handlers:
            try:
                handler(*args)
            except:
                logging.error("error during event call: %s\n%s",
                              msgs._id_to_name(event), logging.stacktrace())
        #end for
        
        """
        handler_name = "handle_" + msgs._id_to_name(event)
        for mediator in self.__mediators:
            if (mediator == src): continue
        
            # TODO: the pass type was never really used and should go away
            mediator.set_pass_type(mediator.PASS_TYPE_PASS_ON)
            try:
                if (hasattr(mediator, handler_name)):
                    getattr(mediator, handler_name)(*args)
                else:
                    mediator.handle_message(event, *args)
            except:
                import traceback; traceback.print_exc()
                continue



            ptype = mediator.get_pass_type()
            if (ptype == mediator.PASS_TYPE_DROP):
                break
            elif (ptype == mediator.PASS_TYPE_PASS_ON):
                continue
            else:
                raise SyntaxError("mediator '%s' must specify pass type" \
                                  % mediator)
        #end for
        """


    def call_service(self, svc, *args):

        if (logging.is_level(logging.DEBUG)):
            logging.debug("*** %s%s ***", msgs._id_to_name(svc), `args`[:30])
        
        try:
            handlers = self.__handlers[svc]
        except:
            handlers = []
            
        for handler in handlers:
            try:
                return handler(*args)
            except:
                logging.error("error during service call: %s\n%s",
                              msgs._id_to_name(svc), logging.stacktrace())
        #end for
        
        
        """    
        handler_name = "handle_" + msgs._id_to_name(svc)
        handler = self.__services.get(svc)

        if (not handler):            
            for mediator in self.__mediators:
                try:
                    if (hasattr(mediator, handler_name)):
                        ret = getattr(mediator, handler_name)(*args)
                    else:
                        ret = mediator.handle_message(svc, *args)
                except:
                    import traceback; traceback.print_exc()
                    pass

                if (ret != None):
                    self.__services[svc] = mediator
                    return ret
            #end for

            raise ServiceNotAvailableError(msgs._id_to_name(svc))

        else:
            if (hasattr(handler, handler_name)):
                ret = getattr(handler, handler_name)(*args)
            else:
                ret = handler.handle_message(svc, *args)

            return ret
    """
        
_singleton = _MessageBus()
def MessageBus(): return _singleton
