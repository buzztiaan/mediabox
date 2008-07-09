from MessageBus import MessageBus


class Mediator(object):
    """
    Base class for mediator objects, i.e. object which receive messages and
    emit messages.
    """

    PASS_TYPE_INVALID = 0
    PASS_TYPE_DROP = 1
    PASS_TYPE_PASS_ON = 2


    def __init__(self):
    
        self.__pass_type = self.PASS_TYPE_PASS_ON
        self.__event_bus = MessageBus()
        self.__event_bus.add_mediator(self)


    def __repr__(self):
    
        return self.__class__.__name__


    def set_pass_type(self, ptype):

        self.__pass_type = ptype    
        
        
    def get_pass_type(self):
    
        return self.__pass_type
        
        
    def handle_event(self, event, *args):
    
        self.pass_on_event()
        
        
    def drop_event(self):

        self.__pass_type = self.PASS_TYPE_DROP
        
        
    def pass_on_event(self):
    
        self.__pass_type = self.PASS_TYPE_PASS_ON
        
        
    def emit_event(self, event, *args):
    
        self.__event_bus.send_event(self, event, *args)


    def call_service(self, svc, *args):
    
        return self.__event_bus.call_service(svc, *args)
        
