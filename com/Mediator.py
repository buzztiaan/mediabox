"""
B{Used internally.}
"""

from MessageBus import MessageBus
from utils import logging


class Mediator(object):
    """
    Base class for mediator objects. These are objects receiving and emitting
    messages.
    
    Do not derive from this class directly. Derive from L{Component} or one of
    its subclasses instead.

    @since: 0.96
    """

    PASS_TYPE_INVALID = 0
    PASS_TYPE_DROP = 1
    PASS_TYPE_PASS_ON = 2


    def __init__(self):
    
        self.__pass_type = self.PASS_TYPE_PASS_ON
        self.__event_bus = MessageBus()
        self._attach_to_message_bus()
        
        
    def _attach_to_message_bus(self):
    
        try:
            self.__event_bus.add_mediator(self)
        except AttributeError:
            raise AttributeError("event bus not present. most likely the "
                                 "component was not initialized properly")


    def __repr__(self):
        """
        Returns a string representation of this component. This is the class
        name.
        
        @return: string representation
        """
    
        return self.__class__.__name__


    def set_pass_type(self, ptype):

        self.__pass_type = ptype    
        
        
    def get_pass_type(self):
    
        return self.__pass_type
        
        
    def handle_message(self, msg, *args):
        """
        Gets invoked when a message arrives on the message bus.
        Override this method in subclasses to listen for messages.
        @since: 0.96
        @deprecated: implement C{handle_<MESSAGE>} instead for the messages
                     you're interested in, e.g. C{handle_CORE_AV_SHUTDOWN}
        
        @param msg: message
        @param args: variable list of arguments
        """
    
        self.pass_on_event()
        
        
    def drop_event(self):

        self.__pass_type = self.PASS_TYPE_DROP
        
        
    def pass_on_event(self):
    
        self.__pass_type = self.PASS_TYPE_PASS_ON
        
        
    def emit_event(self, event, *args):
        """
        Emits the given message.
        @since: 0.96
        @deprecated: use L{emit_message} instead

        @param event: message
        @param args: variable list of arguments
        """
    
        logging.warning("DEPRECATED: %s called 'emit_event'",
                        self.__class__.__name__)
        self.emit_message(event, *args)
        
        
    def emit_message(self, msg, *args):
        """
        Emits the given message.
        @since: 0.96.1

        @param msg: message
        @param args: variable list of arguments
        """
    
        self.__event_bus.send_event(self, msg, *args)
    
        


    def call_service(self, svc, *args):
        """
        Calls the given service and returns the return value of the service.
        Returns C{None} if the service was not found.
        @since: 0.96
        
        @param svc: service message
        @param args: variable list of arguments
        @return: return value of service
        """
    
        return self.__event_bus.call_service(svc, *args)
        
