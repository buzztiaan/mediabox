"""
Base class for all components.
"""

from Mediator import Mediator


class Component(Mediator):
    """
    Base class for all components. Any object derived from this
    class automatically connects to the message bus upon instantiation.
    
    More specialized component classes inherit from C{Component}, e.g.
     - L{Viewer}
     - L{Configurator}

    Methods with prefix C{handle_} (since 0.96.5) get invoked when an
    appropriate message is on the message bus. For example, if you wanted to
    react on the COM_EV_APP_STARTED message (application startup complete)
    you'd implement the message C{handle_COM_EV_APP_STARTED}.
    
    Example::
    
      from com import Component, msgs
      
      
      class MyComponent(Component):
      
          def __init__(self):
          
              # do not forget to invoke the constructor of the super class, as
              # this is what connects your component to the message bus
              Component.__init__(self)


          def handle_COM_EV_APP_STARTED(self):
          
              print "Application startup complete!"


    The old way of message handling by implementing the dispatcher method
    C{handle_message} is deprecated and should not be used in newly written
    code.
    
    Messages are emitted by calling the L{emit_message} method along with
    the message ID (from module L{com.msgs}) and the appropriate number of
    parameters.
    
    Example::
    
      # stop playing whatever is currently playing
      self.emit_message(msgs.MEDIA_ACT_STOP)

    As the sender, your component will not receive the message it emitted. This
    is intentional.
    
    There is a special message type service (C{SVC}) which only reaches one
    component and may yield a return value. Do not use L{emit_message} for
    calling services. Use L{call_service} instead.
    
    Example::
    
      # show a question dialog
      response = self.call_service(msgs.DIALOG_SVC_QUESTION,
                                   "Question",
                                   "Do you feel good?")
      if (response == 0):
          # yes
          print "That's fine!"
      elif (response == 1):
          # no
          print "Too bad..."


    @since: 0.96
    """


    def __init__(self):
    
        self.__properties = {}
    
        Mediator.__init__(self)

        
    def get_prop(self, key, default = ""):
    
        return self.__properties.get(key, default)
        
        
    def set_prop(self, key, value):
    
        self.__properties[key] = value

