class _EventBus(object):
    """
    Singleton class for an event bus. This class is intented to be used by
    the Mediator class only.
    """

    def __init__(self):
    
        self.__mediators = []


    def add_mediator(self, mediator):
    
        self.__mediators.append(mediator)
        
        
    def send_event(self, src, event, *args):
    
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
        
        
_singleton = _EventBus()
def EventBus(): return _singleton
