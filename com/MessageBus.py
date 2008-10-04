"""
Application message bus singleton.
"""

from exc import *
import msgs
from utils import logging


class _MessageBus(object):
    """
    Singleton class for a message bus. This class is intented to be used by
    the Mediator class only.
    """

    def __init__(self):
    
        self.__mediators = []
        self.__services = {}


    def add_mediator(self, mediator):
    
        self.__mediators.append(mediator)
        
        
    def send_event(self, src, event, *args):
    
        logging.debug("*** %s%s ***" % (msgs._id_to_name(event), `args`[:30]))
        
        for mediator in self.__mediators:
            if (mediator == src): continue
        
            mediator.set_pass_type(mediator.PASS_TYPE_PASS_ON)
            try:
                mediator.handle_event(event, *args)
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


    def call_service(self, svc, *args):
    
        try:
            handler = self.__services[svc]
        except:
            for mediator in self.__mediators:
                try:
                    ret = mediator.handle_event(svc, *args)
                except:
                    import traceback; traceback.print_exc()
                    pass
                if (ret != None):
                    self.__services[svc] = mediator
                    return ret
            #end for
            import msgs
            raise ServiceNotAvailableError(msgs._id_to_name(svc))
        else:
            return handler.handle_event(svc, *args)
            
        
_singleton = _MessageBus()
def MessageBus(): return _singleton
