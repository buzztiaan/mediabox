"""
Application message types. These are dynamically populated by plugins.

Import this module to get access to all known message types::

  from com import Component, msgs
  
  class MyComponent(Component):
  
      def __init__(self):
      
          Component.__init__(self)
          
      
      def handle_message(self, msg, *args):
      
          if (msg == msgs.CORE_EV_APP_STARTED):
              self.call_service(msgs.NOTIFY_SVC_SHOW_MESSAGE,
                                "Application started")

  
"""

_cnt = 0
_names = []


def _id_to_name(ident):
    """
    Returns the name of the message given by the ID.
    This is an expensive operation and should only be used when logging
    error messages to the console. Even then, this function should only be
    used by the com subsystem internally.
    
    @param ident: ID of the message, e.g. C{msgs.CORE_APPLICATION_SHUTDOWN}
    @return: printable name of the message, e.g. "C{CORE_APPLICATION_SHUTDOWN}"
    """

    try:
        return _names[ident]
    except:
        return "<undefined>"
    """    
    for k, v in globals().items():
        if (v == ident):
            return k
    #end for
    
    return "<undefined>"
    """


def _register(name):
    """
    Registers a new message. This method is only used internally by
    L{com.Container}.
    
    @param name: name of message
    """
    global _cnt
    
    globals()[name] = _cnt
    _names.append(name)
    _cnt += 1

