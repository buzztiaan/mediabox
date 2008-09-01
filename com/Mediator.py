"""
Internally used base class for all components.
"""

from MessageBus import MessageBus


class Mediator(object):
    """
    Base class for mediator objects, i.e. object which receive messages and
    emit messages.
    
    Do not derive from this class directly. Derive from L{Component} instead.
    """

    PASS_TYPE_INVALID = 0
    PASS_TYPE_DROP = 1
    PASS_TYPE_PASS_ON = 2


    def __init__(self):
    
        self.__pass_type = self.PASS_TYPE_PASS_ON
        self.__event_bus = MessageBus()
        
        
    def _attach_to_message_bus(self):
    
        try:
            self.__event_bus.add_mediator(self)
        except AttributeError:
            raise AttributeError("event bus not present. most likely the "
                                 "component was not initialized properly")


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
        
