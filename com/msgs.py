"""
Application Messages. These are dynamically populated by plugins.
"""

_cnt = 0


def _id_to_name(ident):
    """
    Returns the name of the message given by the ID.
    This is an expensive operation and should only be used when logging
    error messages to the console. Even then, this function should only be
    used by the com subsystem internally.
    """

    for k, v in globals().items():
        if (v == ident):
            return k
    #end for
    
    return "<undefined>"


def _register(name):
    """
    Registers a new message. This method is only used internally by
    L{com.Container}.
    
    @param name: name of message
    """
    global _cnt
    
    globals()[name] = _cnt
    _cnt += 1
    
