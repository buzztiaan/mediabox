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

    @since: 0.96
    """


    def __init__(self):
    
        Mediator.__init__(self)

